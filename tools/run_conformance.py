#!/usr/bin/env python3
"""The reference conformance runner for Lyric 5. See conformance/README.md for the case format.

A case is built with 'lyric5 build' — a 'check' case only through the front end ('--emit ir'),
a 'run' case to a native binary in the profile asked for — and compared with its header. Exit
codes it relies on (14 §1, 13 §1.4): 0 success, 1 rejected compilation, 101 panic.

A case is one '.lyr' file, or — for the rules of packages — one directory holding a package: its
'lyric.toml', its 'src/', and the header in 'src/main.lyr'."""

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib

def parse_header(path):
    spec = {"mode": None, "exit": 0, "panic": None, "stdout": None, "stderr": None,
            "errors": [], "warnings": [], "since": None, "until": None}
    lines = path.read_text(encoding="utf-8").splitlines()
    out = None
    for line in lines:
        if not line.startswith("//!"):
            break
        body = line[3:].strip()
        if body == "run":
            spec["mode"] = "run"
        elif body == "check":
            spec["mode"] = "check"
        elif body.startswith("exit:"):
            spec["exit"] = int(body[5:].strip())
        elif body.startswith("panic:"):
            spec["panic"] = body[6:].strip()
        elif body in ("stdout:", "stderr:"):
            out = spec[body[:-1]] = []
        elif body.startswith("|"):
            if out is None:
                raise ValueError(f"{path}: a '|' line before 'stdout:' or 'stderr:'")
            # One space after the bar is the format's, more are the text's: a report's
            # '  suppressed:' keeps its indentation.
            out.append(body[2:] if body[1:].startswith(" ") else body[1:])
        elif body.startswith("error:"):
            spec["errors"].append(body[6:].strip())
        elif body.startswith("warning:"):
            spec["warnings"].append(body[8:].strip())
        elif body.startswith("since:"):
            spec["since"] = tuple(int(p) for p in body[6:].strip().split("."))
        elif body.startswith("until:"):
            spec["until"] = tuple(int(p) for p in body[6:].strip().split("."))
        else:
            raise ValueError(f"{path}: unknown directive '{body}'")
    if spec["mode"] is None:
        raise ValueError(f"{path}: header must lead with 'run' or 'check'")
    return spec

def find_cases(root):
    """The single-file cases and the package cases under root, in one sorted list. A '.lyr' file
    inside a package is one of its modules, not a case of its own; a package inside a package case
    is one of its dependencies, which the case holds in its own directory ('deps/geo')."""
    manifests = sorted(manifest.parent for manifest in root.rglob("lyric.toml"))
    packages = [p for p in manifests if not any(outer in p.parents for outer in manifests)]
    files = [p for p in root.rglob("*.lyr") if not any(pkg in p.parents for pkg in packages)]
    return sorted(files + packages)

def header_of(case):
    """Where a case's header stands: in the file, or in the package's program."""
    return case / "src" / "main.lyr" if case.is_dir() else case

def run_case(case, spec, lyric5, profile, workdir):
    def fail(reason):
        return (False, reason)

    # A copy in the work directory: 'lyric5 build' puts 'out/' by the nearest manifest or
    # '.git' above the source, and the suite must not build into the specification's tree. A
    # package gets a directory of its own, built from there as a user builds it: no file named.
    if case.is_dir():
        cwd = workdir / case.name
        shutil.copytree(case, cwd)
        command = [str(lyric5), "build", "--profile", profile]
    else:
        cwd = workdir
        source = workdir / case.name
        shutil.copy(case, source)
        command = [str(lyric5), "build", str(source), "--profile", profile]
    front_end_only = spec["mode"] == "check"
    if front_end_only:
        command += ["--emit", "ir"]
    compiled = subprocess.run(command, capture_output=True, text=True, cwd=cwd)
    diagnostics = compiled.stderr

    if spec["errors"]:
        if compiled.returncode != 1:
            return fail(f"expected rejection (exit 1), got exit {compiled.returncode}:\n{diagnostics}")
        # Exactly the codes the header names: one mistake, the errors it names, and no cascade
        # behind them. A case that only asked "is the code among them" passed with a second error
        # for the same mistake.
        reported = set(re.findall(r"error\[(LYR-[A-Z]+[0-9]+)\]", diagnostics))
        if reported != set(spec["errors"]):
            return fail(f"expected exactly {sorted(set(spec['errors']))}, reported {sorted(reported)}:\n{diagnostics}")
        return (True, "")

    if compiled.returncode != 0:
        return fail(f"did not compile (exit {compiled.returncode}):\n{diagnostics}")
    for code in spec["warnings"]:
        if f"warning[{code}]" not in diagnostics:
            return fail(f"expected warning {code}, diagnostics were:\n{diagnostics}")
    if front_end_only:
        if not spec["warnings"] and diagnostics.strip():
            return fail(f"expected silence, got:\n{diagnostics}")
        return (True, "")

    # The binary is named exactly ('.exe' on Windows): after the file's stem, or after the
    # package (15 §1). A prefix glob found a neighbour's binary too —
    # 'default-type-argument-on-a-class' beside 'default-type-argument' — and ran whichever the
    # file system listed first.
    if case.is_dir():
        name = tomllib.loads((cwd / "lyric.toml").read_text(encoding="utf-8"))["package"]["name"]
    else:
        name = case.stem
    binaries = [p for p in (cwd / "out" / profile).rglob(name + "*")
                if p.is_file() and p.name in (name, name + ".exe")]
    if not binaries:
        return fail(f"no binary '{name}' under {cwd / 'out' / profile}")
    executed = subprocess.run([str(binaries[0])], capture_output=True, text=True, cwd=cwd)
    expected_exit = 101 if spec["panic"] else spec["exit"]
    if executed.returncode != expected_exit:
        return fail(f"exit {executed.returncode}, expected {expected_exit};"
                    f" stderr:\n{executed.stderr}")
    if spec["panic"] and f"panic [{spec['panic']}]" not in executed.stderr:
        return fail(f"expected panic {spec['panic']}, stderr:\n{executed.stderr}")
    if spec["stdout"] is not None:
        actual = executed.stdout.replace("\r\n", "\n").rstrip("\n")
        wanted = "\n".join(spec["stdout"])
        if actual != wanted:
            return fail(f"stdout mismatch\n-- expected --\n{wanted}\n-- actual --\n{actual}")
    if spec["stderr"] is not None:
        # The error stream BEGINS with these lines: the report's own, then — in the debug
        # profile — a trace whose frames are the implementation's.
        actual = executed.stderr.replace("\r\n", "\n").split("\n")
        if actual[:len(spec["stderr"])] != spec["stderr"]:
            wanted = "\n".join(spec["stderr"])
            return fail(f"stderr mismatch\n-- expected to begin with --\n{wanted}\n-- actual --\n{executed.stderr}")
    return (True, "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lyric5", type=pathlib.Path, default=None,
                    help="the compiler executable (default: 'lyric5' on PATH)")
    ap.add_argument("--profile", default="debug", choices=["debug", "release"],
                    help="the build profile of the 'run' cases")
    ap.add_argument("--cases", type=pathlib.Path,
                    default=pathlib.Path(__file__).parent.parent / "conformance" / "cases")
    ap.add_argument("--toolchain-version", default=None,
                    help="the toolchain's version; cases with a newer 'since:' are skipped, "
                         "and cases whose 'until:' it has reached are retired. "
                         "Omitted means: run everything (a working tree is the newest state).")
    ap.add_argument("--parse-only", action="store_true",
                    help="read every header and run nothing: the suite's own format check")
    args = ap.parse_args()
    version = (tuple(int(p) for p in args.toolchain_version.split("."))
               if args.toolchain_version else None)

    cases = find_cases(args.cases)
    if not cases:
        print("no cases found", file=sys.stderr)
        return 2
    if args.parse_only:
        for case in cases:
            parse_header(header_of(case))
        print(f"{len(cases)} cases, every header well-formed")
        return 0

    lyric5 = args.lyric5 or shutil.which("lyric5")
    if not lyric5:
        print("need --lyric5 or 'lyric5' on PATH", file=sys.stderr)
        return 2
    # Absolute: a case is built from its work directory, where a relative path means nothing.
    lyric5 = pathlib.Path(lyric5).resolve()

    failed = 0
    skipped = 0
    with tempfile.TemporaryDirectory() as tmp:
        for case in cases:
            spec = parse_header(header_of(case))
            label = case.relative_to(args.cases).as_posix() + ("/" if case.is_dir() else "")
            if spec["since"] and version and spec["since"] > version:
                skipped += 1
                print(f"SKIP {label} (since {'.'.join(map(str, spec['since']))})")
                continue

            # A case the language has left behind. The mirror of 'since', and the reason it
            # exists: a MAJOR may change a form the suite pinned, and the case then describes a
            # version range rather than the language. Retiring it here keeps both lanes honest —
            # against a released toolchain it still runs, against the tree that broke it it
            # does not, and the replacement carries the matching 'since'.
            if spec["until"] and version and version >= spec["until"]:
                skipped += 1
                print(f"SKIP {label} (until {'.'.join(map(str, spec['until']))})")
                continue
            ok, reason = run_case(case, spec, lyric5, args.profile, pathlib.Path(tmp))
            if ok:
                print(f"PASS {label}")
            else:
                failed += 1
                print(f"FAIL {label}: {reason}")

    ran = len(cases) - skipped
    tail = f", {skipped} skipped" if skipped else ""
    print(f"\n{ran - failed}/{ran} passed ({args.profile}){tail}")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""The reference conformance runner of Lyric-Script. See conformance/README.md for the case format.

Lyric 5's runner (tools/run_conformance.py on main) with a script's differences: one executable,
`lyric-script check` and `lyric-script run`; `since:` required; a header that may trail the case;
a program of modules is a folder with a `main.lyrs`, the case its entry; a package case is a
folder with a `lyric-script.toml`, read from its `src/main.lyrs` and built from its folder.
"""

import argparse
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile


def header_lines(lines):
    """The leading block of '//!' lines, or the trailing one where the case does not open with it."""
    if lines and lines[0].startswith("//!"):
        block = []
        for line in lines:
            if not line.startswith("//!"):
                break
            block.append(line)
        return block
    block = []
    for line in reversed(lines):
        if not line.strip():
            if block:
                break
            continue
        if not line.startswith("//!"):
            break
        block.append(line)
    return list(reversed(block))


def parse_header(path):
    spec = {"mode": None, "exit": 0, "panic": None, "stdout": None, "stderr": None,
            "errors": [], "warnings": [], "since": None, "until": None, "options": []}
    out = None
    for line in header_lines(path.read_text(encoding="utf-8").splitlines()):
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
            # '  caused by:' keeps its indentation.
            out.append(body[2:] if body[1:].startswith(" ") else body[1:])
        elif body.startswith("error:"):
            spec["errors"].append(body[6:].strip())
        elif body.startswith("warning:"):
            spec["warnings"].append(body[8:].strip())
        elif body.startswith("since:"):
            spec["since"] = tuple(int(p) for p in body[6:].strip().split("."))
        elif body.startswith("until:"):
            spec["until"] = tuple(int(p) for p in body[6:].strip().split("."))
        elif body.startswith("option:"):
            spec["options"].append(body[7:].strip())
        elif body == "update":
            spec["update"] = True
        else:
            raise ValueError(f"{path}: unknown directive '{body}'")
    if spec["mode"] is None:
        raise ValueError(f"{path}: the header must lead with 'run' or 'check'")
    if spec["since"] is None or spec["since"] < (1, 0, 0):
        raise ValueError(f"{path}: every case carries 'since:', at least 1.0.0")
    return spec


def program_of(path, root):
    """The folder of the program a file belongs to: the nearest one above it, below `root`, that
    holds a `main.lyrs`; None for a case of one file."""
    for parent in path.parents:
        if parent == root or root not in parent.parents:
            return None
        if (parent / "main.lyrs").is_file():
            return parent
    return None


def package_of(path, root):
    """The outermost folder above a file, below `root`, that holds a `lyric-script.toml`: the
    package case it belongs to — a package nested in it is its dependency; None for none."""
    found = None
    for parent in path.parents:
        if parent == root or root not in parent.parents:
            break
        if (parent / "lyric-script.toml").is_file():
            found = parent
    return found


def is_case(path, root):
    """A file of one file's case, a program's entry, or a package case's `src/main.lyrs`; the
    other files of a program or a package are its modules."""
    package = package_of(path, root)
    if package is not None:
        return path == package / "src" / "main.lyrs"
    program = program_of(path, root)
    return program is None or path == program / "main.lyrs"


def version_key(name):
    """A version folder's name as a sortable key: its numbers, then the rest."""
    core = name.split("-")[0].split("+")[0]
    return tuple(int(p) if p.isdigit() else 0 for p in core.split(".")) + (name,)


def git(args, cwd):
    # a fixed author at fixed times, so a case's lock can name the commits
    env = dict(os.environ, GIT_AUTHOR_NAME="conformance", GIT_AUTHOR_EMAIL="conformance@lyric",
               GIT_COMMITTER_NAME="conformance", GIT_COMMITTER_EMAIL="conformance@lyric",
               GIT_AUTHOR_DATE="2026-01-01T00:00:00Z", GIT_COMMITTER_DATE="2026-01-01T00:00:00Z")
    # and modes that do not depend on the file system the case was checked out to
    subprocess.run(["git", "-c", "core.autocrlf=false", "-c", "core.fileMode=false",
                    "-c", "commit.gpgsign=false", *args],
                   cwd=cwd, env=env, check=True, capture_output=True)


def fill_repos(text, url):
    return text.replace("{repos}", url)


def prepare_package(package, work):
    """A package case's copy in `work`, as a user's folder: its `repos/<name>/<version>/` made git
    repositories beside it — one commit per version, oldest first, each tagged `v<version>`, on
    the branch `main` —, and `{repos}` in its manifests and locks their place as a `file://` URL.
    Returns the copy's folder."""
    copy = work / package.name
    shutil.copytree(package, copy, ignore=shutil.ignore_patterns("repos"))
    repos = work / "repos"
    url = repos.resolve().as_uri()
    source = package / "repos"
    if source.is_dir():
        for repo in sorted(p for p in source.iterdir() if p.is_dir()):
            target = repos / repo.name
            target.mkdir(parents=True)
            git(["init", "-q", "-b", "main"], target)
            for ver in sorted((v for v in repo.iterdir() if v.is_dir()), key=lambda v: version_key(v.name)):
                for old in target.iterdir():
                    if old.name != ".git":
                        shutil.rmtree(old) if old.is_dir() else old.unlink()
                shutil.copytree(ver, target, dirs_exist_ok=True)
                for f in target.rglob("*"):
                    if f.is_file() and f.name in ("lyric-script.toml", "lyric-script.lock"):
                        f.write_text(fill_repos(f.read_text(encoding="utf-8"), url), encoding="utf-8", newline="\n")
                git(["add", "-A"], target)
                git(["commit", "-q", "-m", f"v{ver.name}"], target)
                git(["tag", f"v{ver.name}"], target)
    # a manifest, a lock, and a script, whose frontmatter may name the repositories too
    for f in copy.rglob("*"):
        if f.is_file() and (f.name in ("lyric-script.toml", "lyric-script.lock") or f.suffix == ".lyrs"):
            f.write_text(fill_repos(f.read_text(encoding="utf-8"), url), encoding="utf-8", newline="\n")
    return copy


def run_case(path, spec, exe, package=None, env=None):
    def fail(reason):
        return (False, reason)

    # a package case is built from its folder, naming no file, as a user builds a package
    def command(verb):
        if package is not None:
            return subprocess.run([str(exe), verb, *spec["options"]], capture_output=True, text=True,
                                  cwd=package, env=env)
        return subprocess.run([str(exe), verb, *spec["options"], str(path)], capture_output=True, text=True,
                              env=env)

    # `update`: the package's git dependencies read anew before the build
    if spec.get("update") and package is not None:
        updated = subprocess.run([str(exe), "update"], capture_output=True, text=True, cwd=package, env=env)
        if updated.returncode != 0:
            return fail(f"update exited {updated.returncode}:\n{updated.stderr}")

    checked = command("check")
    diagnostics = checked.stderr

    if spec["errors"]:
        # a rejection exits 1; a fault of the environment as the case's `exit:` says
        wanted_exit = spec["exit"] or 1
        if checked.returncode == 0:
            return fail("expected rejection, checked cleanly")
        if checked.returncode != wanted_exit:
            return fail(f"check exited {checked.returncode}, expected {wanted_exit}:\n{diagnostics}")
        # a case may expect warnings beside its errors
        for code in spec["errors"] + spec["warnings"]:
            if code not in diagnostics:
                return fail(f"expected {code}, diagnostics were:\n{diagnostics}")
        return (True, "")

    if checked.returncode != 0:
        return fail(f"did not check:\n{diagnostics}")
    for code in spec["warnings"]:
        if code not in diagnostics:
            return fail(f"expected warning {code}, diagnostics were:\n{diagnostics}")
    if spec["mode"] == "check":
        if not spec["warnings"] and diagnostics.strip():
            return fail(f"expected silence, got:\n{diagnostics}")
        return (True, "")

    executed = command("run")
    expected_exit = 101 if spec["panic"] else spec["exit"]
    if executed.returncode != expected_exit:
        return fail(f"exit {executed.returncode}, expected {expected_exit};"
                    f" stderr:\n{executed.stderr}")
    if spec["panic"] and spec["panic"] not in executed.stderr:
        return fail(f"expected panic {spec['panic']}, stderr:\n{executed.stderr}")
    if spec["stdout"] is not None:
        actual = executed.stdout.replace("\r\n", "\n").rstrip("\n")
        wanted = "\n".join(spec["stdout"])
        if actual != wanted:
            return fail(f"stdout mismatch\n-- expected --\n{wanted}\n-- actual --\n{actual}")
    if spec["stderr"] is not None:
        # The error stream BEGINS with these lines: the report's own, then the frames, which are
        # the implementation's.
        actual = executed.stderr.replace("\r\n", "\n").split("\n")
        if actual[:len(spec["stderr"])] != spec["stderr"]:
            wanted = "\n".join(spec["stderr"])
            return fail(f"stderr mismatch\n-- expected to begin with --\n{wanted}"
                        f"\n-- actual --\n{executed.stderr}")
    return (True, "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lyric-script", type=pathlib.Path, required=True,
                    help="the lyric-script executable")
    ap.add_argument("--cases", type=pathlib.Path,
                    default=pathlib.Path(__file__).parent.parent / "conformance" / "cases")
    ap.add_argument("--toolchain-version", default=None,
                    help="the toolchain's version; cases with a newer 'since:' are skipped, "
                         "and cases whose 'until:' it has reached are retired. "
                         "Omitted means: run everything (a working tree is the newest state).")
    args = ap.parse_args()
    version = (tuple(int(p) for p in args.toolchain_version.split("-")[0].split("."))
               if args.toolchain_version else None)

    if not args.lyric_script.is_file():
        print(f"no lyric-script at '{args.lyric_script}'", file=sys.stderr)
        return 2

    cases = sorted(c for c in args.cases.rglob("*.lyrs") if is_case(c, args.cases))
    if not cases:
        print("no cases found", file=sys.stderr)
        return 2

    failed = 0
    skipped = 0
    for case in cases:
        spec = parse_header(case)
        label = case.relative_to(args.cases)
        package = package_of(case, args.cases)
        if package is not None:
            label = f"{package.relative_to(args.cases).as_posix()}/"
        elif case.name == "main.lyrs" and program_of(case, args.cases) is not None:
            label = f"{label.parent.as_posix()}/"
        if version and spec["since"] > version:
            skipped += 1
            print(f"SKIP {label} (since {'.'.join(map(str, spec['since']))})")
            continue
        if spec["until"] and version and version >= spec["until"]:
            skipped += 1
            print(f"SKIP {label} (until {'.'.join(map(str, spec['until']))})")
            continue
        program = program_of(case, args.cases)
        if package is None and program is not None and (program / "repos").is_dir():
            # a script whose frontmatter reads from git: built from a copy, its cache its own
            with tempfile.TemporaryDirectory() as work:
                work = pathlib.Path(work)
                copy = prepare_package(program, work)
                env = dict(os.environ, LYRIC_SCRIPT_CACHE=str(work / "cache"))
                ok, reason = run_case(copy / "main.lyrs", spec, args.lyric_script.resolve(), None, env)
        elif package is None:
            ok, reason = run_case(case, spec, args.lyric_script.resolve())
        else:
            # built from a copy, with a cache of its own: what it fetches and locks stays there
            with tempfile.TemporaryDirectory() as work:
                work = pathlib.Path(work)
                copy = prepare_package(package, work)
                env = dict(os.environ, LYRIC_SCRIPT_CACHE=str(work / "cache"))
                ok, reason = run_case(copy / "src" / "main.lyrs", spec, args.lyric_script.resolve(), copy, env)
        if ok:
            print(f"PASS {label}")
        else:
            failed += 1
            print(f"FAIL {label}: {reason}")

    ran = len(cases) - skipped
    tail = f", {skipped} skipped" if skipped else ""
    print(f"\n{ran - failed}/{ran} passed{tail}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

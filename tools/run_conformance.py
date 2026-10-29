#!/usr/bin/env python3
"""The reference conformance runner of Lyric-Script. See conformance/README.md for the case format.

Lyric 5's runner (tools/run_conformance.py on main) with a script's differences: one executable,
`lyric-script check` and `lyric-script run`; `since:` required; a header that may trail the case.
"""

import argparse
import pathlib
import subprocess
import sys


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
            "errors": [], "warnings": [], "since": None, "until": None}
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
        else:
            raise ValueError(f"{path}: unknown directive '{body}'")
    if spec["mode"] is None:
        raise ValueError(f"{path}: the header must lead with 'run' or 'check'")
    if spec["since"] is None or spec["since"] < (1, 0, 0):
        raise ValueError(f"{path}: every case carries 'since:', at least 1.0.0")
    return spec


def run_case(path, spec, exe):
    def fail(reason):
        return (False, reason)

    checked = subprocess.run([str(exe), "check", str(path)], capture_output=True, text=True)
    diagnostics = checked.stderr

    if spec["errors"]:
        if checked.returncode == 0:
            return fail("expected rejection, checked cleanly")
        if checked.returncode != 1:
            return fail(f"check exited {checked.returncode}, expected 1:\n{diagnostics}")
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

    executed = subprocess.run([str(exe), "run", str(path)], capture_output=True, text=True)
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

    cases = sorted(args.cases.rglob("*.lyrs"))
    if not cases:
        print("no cases found", file=sys.stderr)
        return 2

    failed = 0
    skipped = 0
    for case in cases:
        spec = parse_header(case)
        label = case.relative_to(args.cases)
        if version and spec["since"] > version:
            skipped += 1
            print(f"SKIP {label} (since {'.'.join(map(str, spec['since']))})")
            continue
        if spec["until"] and version and version >= spec["until"]:
            skipped += 1
            print(f"SKIP {label} (until {'.'.join(map(str, spec['until']))})")
            continue
        ok, reason = run_case(case, spec, args.lyric_script)
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

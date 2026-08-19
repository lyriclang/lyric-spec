#!/usr/bin/env python3
"""The reference conformance runner. See conformance/README.md for the case format."""

import argparse
import pathlib
import subprocess
import sys
import tempfile

def parse_header(path):
    spec = {"mode": None, "exit": 0, "panic": None, "stdout": None,
            "errors": [], "warnings": []}
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
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
        elif body == "stdout:":
            spec["stdout"] = out
        elif body.startswith("|"):
            out.append(body[1:].lstrip(" ") if body[1:].startswith(" ") else body[1:])
        elif body.startswith("error:"):
            spec["errors"].append(body[6:].strip())
        elif body.startswith("warning:"):
            spec["warnings"].append(body[8:].strip())
        else:
            raise ValueError(f"{path}: unknown directive '{body}'")
    if spec["mode"] is None:
        raise ValueError(f"{path}: header must lead with 'run' or 'check'")
    return spec

def run_case(path, spec, lyrc, lyrvm, stdlib, workdir):
    def fail(reason):
        return (False, reason)

    module = workdir / (path.stem + ".lyrbc")
    compile_cmd = [str(lyrc), "build", str(path), "-o", str(module), "-q"]
    if stdlib:
        compile_cmd += ["--stdlib", str(stdlib)]
    compiled = subprocess.run(compile_cmd, capture_output=True, text=True)
    diagnostics = compiled.stderr

    if spec["errors"]:
        if compiled.returncode == 0:
            return fail("expected rejection, compiled cleanly")
        for code in spec["errors"]:
            if code not in diagnostics:
                return fail(f"expected {code}, diagnostics were:\n{diagnostics}")
        return (True, "")

    if compiled.returncode != 0:
        return fail(f"did not compile:\n{diagnostics}")
    for code in spec["warnings"]:
        if code not in diagnostics:
            return fail(f"expected warning {code}, diagnostics were:\n{diagnostics}")
    if spec["mode"] == "check":
        if not spec["warnings"] and diagnostics.strip():
            return fail(f"expected silence, got:\n{diagnostics}")
        return (True, "")

    executed = subprocess.run([str(lyrvm), "run", str(module)],
                              capture_output=True, text=True)
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
    return (True, "")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--toolchain", type=pathlib.Path, default=None,
                    help="directory holding lyrc and lyrvm (a release archive's layout)")
    ap.add_argument("--lyrc", type=pathlib.Path, default=None,
                    help="compiler executable; overrides --toolchain")
    ap.add_argument("--lyrvm", type=pathlib.Path, default=None,
                    help="runtime executable; overrides --toolchain")
    ap.add_argument("--stdlib", type=pathlib.Path, default=None)
    ap.add_argument("--cases", type=pathlib.Path,
                    default=pathlib.Path(__file__).parent.parent / "conformance" / "cases")
    args = ap.parse_args()

    exe = ".exe" if sys.platform == "win32" else ""
    lyrc = args.lyrc or (args.toolchain and args.toolchain / f"lyrc{exe}")
    lyrvm = args.lyrvm or (args.toolchain and args.toolchain / f"lyrvm{exe}")
    if not lyrc or not lyrvm:
        print("need --toolchain or both --lyrc and --lyrvm", file=sys.stderr)
        return 2

    cases = sorted(args.cases.rglob("*.lyr"))
    if not cases:
        print("no cases found", file=sys.stderr)
        return 2

    failed = 0
    with tempfile.TemporaryDirectory() as tmp:
        for case in cases:
            spec = parse_header(case)
            ok, reason = run_case(case, spec, lyrc, lyrvm, args.stdlib, pathlib.Path(tmp))
            label = case.relative_to(args.cases)
            if ok:
                print(f"PASS {label}")
            else:
                failed += 1
                print(f"FAIL {label}: {reason}")

    print(f"\n{len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0

if __name__ == "__main__":
    sys.exit(main())

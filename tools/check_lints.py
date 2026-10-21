#!/usr/bin/env python3
"""Every lint of the groups this checks has a red case and a green case in the suite (16 §5).

    python3 tools/check_lints.py [--groups unused,correctness,...]

The lints are Appendix A's table (generated from the toolchain's catalogue). A red case names the
lint's code under 'warning:' (or 'error:', where it denies it); a green case names the lint under
'clean:' and compiles without a word. A lint without one of them is a rule the suite does not hold —
the two rule 9 names aside.
"""
import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import run_conformance as runner  # noqa: E402

GROUPS = "unused,correctness,resources,concurrency,deprecation,style,perf,docs"

# 16 §5 rule 9: the lints held otherwise, and which of their cases they go without
NO_RED = {
    "reserved-device-name": "its red program is a file Windows cannot hold",
    "deprecated-edition": "there is no edition yet",
}
NO_GREEN = {
    "deprecated-edition": "there is no edition yet",
}

def lints():
    table = (ROOT / "spec" / "appendix-a-diagnostics.md").read_text(encoding="utf-8")
    found = {}
    for m in re.finditer(r"^\| `([a-z0-9-]+)` \| (LYR-[A-Z]+[0-9]{4}) \| ([a-z]+) \| ([a-z]+) \|", table, re.M):
        found[m.group(1)] = (m.group(2), m.group(3))
    return found

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--groups", default=GROUPS)
    args = ap.parse_args()
    groups = set(args.groups.split(","))
    red, green = set(), set()
    for case in runner.find_cases(ROOT / "conformance" / "cases"):
        spec = runner.parse_header(runner.header_of(case))
        red.update(spec["warnings"])
        red.update(spec["errors"])
        green.update(spec["clean"])
    missing = []
    for name, (code, group) in sorted(lints().items()):
        if group not in groups:
            continue
        if code not in red and name not in NO_RED:
            missing.append(f"{name} ({code}): no red case — 'warning: {code}'")
        if name not in green and name not in NO_GREEN:
            missing.append(f"{name} ({code}): no green case — 'clean: {name}'")
    for line in missing:
        print(line)
    print(f"{len(lints())} lints, groups {sorted(groups)}: {len(missing)} missing")
    return 1 if missing else 0

if __name__ == "__main__":
    sys.exit(main())

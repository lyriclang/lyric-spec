#!/usr/bin/env python3
"""The suite holds the specification where it has numbers: every code of Appendix A, and every
section of the chapters of rules (16 §3; the plan's measure of "complete").

    python3 tools/check_coverage.py

A code is held by a case that names it under 'error:', 'warning:' or 'panic:'. A section — a
'##' of chapters 03 to 13, 15 and 16 — is held by a case whose leading comment cites it, as the
cases do: '08 §5', '12 §Time' (the chapter's number may be left out in the chapter's own
directory). What the suite cannot hold is listed below, each with the reason; a code or a section
that is neither held nor listed is a rule the suite does not test, and fails the check.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import run_conformance as runner  # noqa: E402

CHAPTERS = ["03-types", "04-modules", "05-interfaces", "06-errors", "07-statements",
            "08-expressions", "09-patterns", "10-concurrency", "11-metaprogramming",
            "12-stdlib", "13-abi", "15-project", "16-diagnostics"]

# Codes no program of the suite can raise: the command line's, the build driver's, and the
# compiler's own failures — the toolchain's tests hold them (14 §1).
TOOLING_PREFIXES = {
    "LYR-CLI": "the command line's — a case is a program, not an invocation (14 §1)",
    "LYR-BLD": "the build driver's: the C compiler and the linker at work (14 §1)",
    "LYR-ICE": "an internal compiler error — no program is meant to raise one",
    "LYR-IR": "the IR verifier's — a compiler bug, never a program's",
    "LYR-CG": "the C emitter's — a compiler bug, never a program's",
    "LYR-MIG": "lyric fix --from-4's, run on a Lyric 4 package (14 §14)",
}
CODES_HELD_ELSEWHERE = {
    "LYR-PKG0007": "a repository or an archive that cannot be loaded — the suite fetches nothing (GitDependencyTests, VendorTests)",
    "LYR-RES0007": "two files of one module, reported where every file is compiled: a library's build and lyric test (WarningAnalyzerTests)",
    "LYR-RES0013": "a single file named std.lyr — a case is named for what it shows (PreludeTests)",
    "LYR-RES0015": "a test module twice, under src/tests/ and tests/ — lyric test's (TestCommandTests)",
    "LYR-RT0015": "the system refused the runtime what it needs — no program text causes it",
    "LYR-RT0017": "control reached code the compiler holds unreachable — a compiler bug, never a program's",
    "LYR-RT0020": "the runtime found its own invariant broken — a bug of the runtime or the compiler",
    "LYR-RT0022": "C calls Lyric on a thread C started itself — a package's native part (NativeTests, ExportTests)",
    "LYR-SEM0195": "a part of the standard library missing from the module path — lyric5 always brings it",
    "LYR-SEM0214": "deprecated-edition: there is no edition yet to retire a construct",
    "LYR-SEM0216": "reserved-device-name: its red program is a file Windows cannot hold (check_lints.py)",
}
SECTIONS_HELD_ELSEWHERE = {
    "16-diagnostics §3": "every case that names a code holds it, and this check holds the catalogue",
    "15-project §6": "reproducibility is two builds compared byte by byte (ReproducibilityTests)",
    "15-project §7": "a package's tests run by lyric test (TestCommandTests)",
    "16-diagnostics §4": "the JSON form is the command line's (JsonFormTests, EventWriterTests)",
    "16-diagnostics §6": "lyric fix rewrites files (FixTests)",
}


def codes():
    """The codes of Appendix A a program can still meet: a retired one stands in the table for
    what it once meant, and no rule of this specification raises it."""
    table = (ROOT / "spec" / "appendix-a-diagnostics.md").read_text(encoding="utf-8")
    return {m.group(1): m.group(2)
            for m in re.finditer(r"^\| (LYR-[A-Z]+[0-9]{4}) \| ([EWP]) \|([^\n]*)$", table, re.M)
            if "*(retired)*" not in m.group(3)}


def sections():
    found = []
    for ch in CHAPTERS:
        text = (ROOT / "spec" / f"{ch}.md").read_text(encoding="utf-8")
        for number, title in re.findall(r"^## (?:([0-9]+)\. )?(.+)$", text, re.M):
            if title != "Scope":
                found.append((ch, number, title))
    return found


def comment_of(case):
    lines = runner.header_of(case).read_text(encoding="utf-8", errors="replace").splitlines()[:16]
    return "\n".join(l for l in lines if l.startswith("//") and not l.startswith("//!"))


def cites(text, chapter, number, title, own):
    num = chapter[:2]
    refs = []
    if number:
        refs.append(rf"\b{num} §{number}\b")
        if own:
            refs.append(rf"(?<![0-9] )§{number}\b")
    refs.append(rf"\b{num} §\s*{re.escape(title)}")
    if own:
        refs.append(rf"§\s*{re.escape(title)}")
    return any(re.search(r, text, re.I) for r in refs)


def main():
    cases = list(runner.find_cases(ROOT / "conformance" / "cases"))
    named = set()
    comments = []
    for case in cases:
        spec = runner.parse_header(runner.header_of(case))
        named.update(spec["errors"])
        named.update(spec["warnings"])
        if spec["panic"]:
            named.add(spec["panic"])
        comments.append((case.relative_to(ROOT / "conformance" / "cases").parts[0], comment_of(case)))

    missing = []
    all_codes = codes()
    for code in sorted(all_codes):
        if code in named or code in CODES_HELD_ELSEWHERE:
            continue
        if any(code.startswith(p) for p in TOOLING_PREFIXES):
            continue
        missing.append(f"{code}: no case names it")
    for code in sorted(CODES_HELD_ELSEWHERE):
        if code in named:
            missing.append(f"{code}: listed as held elsewhere, but a case names it — take it off the list")

    all_sections = sections()
    for chapter, number, title in all_sections:
        key = f"{chapter} §{number or title}"
        if key in SECTIONS_HELD_ELSEWHERE:
            continue
        if not any(cites(text, chapter, number, title, own=(d == chapter)) for d, text in comments):
            missing.append(f"{key} ({title}): no case cites it")

    for line in missing:
        print(line)
    print(f"{len(all_codes)} codes, {len(all_sections)} sections, {len(cases)} cases: {len(missing)} missing")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())

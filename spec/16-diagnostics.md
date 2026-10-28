# 16. Diagnostics

**Base.** Lyric 5.0 [§16](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/16-diagnostics.md) applies, with the deviations below.

**Status.** The forms written (S2); the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

## Written (S2)

1. **Codes** carry the prefix `LYS-`; the catalogue is `diagnostics.toml` in lyric-script
   ([12](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)). In each area that Lyric 5 has as well — `LEX`, `PAR`, `SEM`, `RT` — a code means
   what Lyric 5's code of the same number means, whatever its number; Lyric-Script's own codes
   start at **0900**, beyond the numbers Lyric 5 uses (its `SEM` codes reach 0232). `LYS-NYI0001` names a form a later milestone builds and leaves the
   toolchain before 1.0.
2. **The text form** is Lyric 5's: `severity[CODE]: message`, the place as `--> file:line:column`
   with the column in characters, the line with the span marked under it (a tab drawn as four
   spaces), and `= help: …` where the finding has a short answer.
3. **The JSON form** (`--json` on `run` and `check`) is Lyric 5's events, schema version 1: one
   object a line on the standard output, a `diagnostic` for each finding — `code`, `severity`,
   `message`, `span` with `file` and its `start` and `end` as `line`, `column` and `offset`,
   `labels`, `notes` (a help as a note of `kind` `help`), `rendered` — and a `summary` with the
   counts of errors and warnings that closes the compilation, before a script runs.

**Conformance.** `conformance/cases/16-diagnostics/` (`since: 1.0.0`).

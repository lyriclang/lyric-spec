# Diagnostics

> **Partly written.** §1–§2 were written with milestone **M12a** of the Lyric 5 plan (slice S2); the
> rest follows, spec-first: each rule lands here with its conformance case before or with its
> implementation. Source of the decisions:
> [11 Tooling and interop W6/W7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md).

## Scope

The diagnostic record, codes and areas, severities, lints and their levels, fixes, the output forms.

## 1. The text form

What the toolchain writes to the standard error for a person to read
([11 G5, C7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)). A
program reads the JSON form instead (to come, M12a S4).

**Conformance.** The suite reads the head lines (rule 1) of every rejecting case; the layout in the
toolchain's own tests (`tests/Lyric.Tests.Core`, `TextRendererTests`).

1. A diagnostic begins with its **head**, `severity[CODE]: message`, on a line of its own; the
   severity is `error`, `warning` or `hint`. Nothing else in the output begins a line that way.
2. A diagnostic with a place follows it with the **arrow**, ` --> path:line:column` — line and
   column from 1, the column in characters of the line as the file holds them.
3. The **source lines** of its places follow, in a gutter of line numbers: the primary place marked
   `^`, the secondary ones `-`, each with its label beside or under its mark. The places of one file
   stand together, in line order; a place in another file has its lines under ` ::: path:line:column`.
   A span across lines is marked on its first line and its last. A tab takes four columns, a wide
   character two, a combining one none, a control character one stand-in, so a mark stands under
   what it marks; a line too wide is cut around its marks, with `…` where it was cut.
4. A **note** without a place is the line `= note: …`, advice `= help: …`. A note with a place is a
   block of its own, `note: …` with its arrow and lines; a suggested change is `help: …` with the line
   as it would read after it.
5. **Paths** are said relative to the package's root where the file lies under it, else as the file
   system has them; `--absolute-paths` says every one as the file system has it.
6. **Colour**: `--color auto|always|never`. `auto`, the default, colours where the standard error
   is a terminal, unless `NO_COLOR` is set to a non-empty value or `TERM` is `dumb`. Colour changes no
   character of the text.
7. The diagnostics come in the order of their files, then their places; the order is the same for
   the same input and is not otherwise a contract. Each is said once.
8. Rules 1, 2 and 6 and what rules 3–4 show are normative; the widths, the spacing and the colours
   chosen are not.

## 2. What follows from an error

([11 G6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** `conformance/cases/16-diagnostics/`.

1. A declaration the parser cannot read whole reports its lexical and syntax errors (`LYR-LEX…`,
   `LYR-PAR…`) and nothing that follows from them: no finding whose place lies inside it. The other
   declarations of the file report as they would.
2. **`--max-errors N`** draws the first `N` errors, 50 unless said, all of them for `0`; what comes
   after is counted, and one closing line, `note: …`, says how many errors and other findings were
   not drawn. The exit code is what it would be without the limit.

# Diagnostics

> **Partly written.** §1–§5 were written with milestone **M12a** of the Lyric 5 plan (slices S2–S5); the
> rest follows, spec-first: each rule lands here with its conformance case before or with its
> implementation. Source of the decisions:
> [11 Tooling and interop W6/W7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md).

## Scope

The diagnostic record, codes and areas, severities, lints and their levels, fixes, the output forms.

## 1. The text form

What the toolchain writes to the standard error for a person to read
([11 G5, C7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)). A
program reads the JSON form instead (§4).

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
2. **A mistake is said once.** What follows from it is not said again: an instance whose type
   arguments an annotation got wrong, refused there and not again where an initializer takes them;
   the names an or-pattern's alternative does not bind, in one finding; the parser's recovery, which
   skips the rest of an unclosed interpolation and reads `T { x: 1 }` as the initializer it is
   (`LYR-PAR0037`, with `=` as its fix); a literal's suffix the lexer refused, which the parser does
   not refuse again; a conformance written twice (`LYR-SEM0133`), whose second block the calls do not
   see; a compile-time-only call, said where the program makes it and not again inside the standard
   library.
3. A file the parser reads as holding nothing — nesting it does not carry (`LYR-PAR0045`) — holds
   nothing for the rest of the build: neither its missing `main` nor a name its importers do not
   find is said.
4. **`--max-errors N`** draws the first `N` errors, 50 unless said, all of them for `0`; what comes
   after is counted, and one closing line, `note: …`, says how many errors and other findings were
   not drawn. The exit code is what it would be without the limit.

## 3. Codes and the catalogue

([11 G9, G10](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** Every rejecting case names its codes; the catalogue against the compiler in the toolchain's
own tests (`tests/Lyric5.Tests`, `CatalogTests`).

1. A code is `LYR-`, an area — `LEX`, `PAR`, `RES`, `SEM`, `MAC`, `CT`, `CG`, `PKG`, `BLD`, `CLI`, `ICE`,
   `RT`, and `IR`, retired —, and four digits. The code and its severity are contract; the message's wording is not.
2. Every code the toolchain reports stands in [Appendix A](appendix-a-diagnostics.md), generated from the
   toolchain's catalogue, with its severity, the chapter whose rule it is, and when it is reported. A code no
   longer reported is **retired** there: its number is not given to another finding.
3. **`lyric explain CODE`** prints the catalogue's entry — for an error or a warning an explanation, a
   program that reports it and the program put right. A code is read as `LYR-SEM0001`, `SEM0001` or
   `sem0001`; one the catalogue does not hold is a usage error (exit 2, [14 §1.1](14-cli.md)).
4. A message begins in lowercase and ends without a period; it names the program's own names in quotes.

## 4. The JSON form

([11 G8, C6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `JsonFormTests`; `tests/Lyric.Tests.Core`,
`EventWriterTests`).

1. **`--json`** on `build`, `run`, `check`, `test` and `fix` writes, in place of the text form, one JSON object a line on
   the standard output — a reader takes a line at a time while the command runs. Nothing else is written
   there, but the output of the program `run` runs, after the build's lines; the standard error stays
   empty. (`metadata --json` is a document of its own, 14 §2.)
2. Every line holds `"type"` and `"version"`, the schema's version, `1`. A reader skips a type it does not
   know and refuses a version it does not know.
3. **`diagnostic`**: `code`, `severity` (`error`, `warning`, `hint`), `message`, `span`, the primary
   `label` where there is one, `labels` (each `span` and `label`), `notes` (each `kind` — `note`, `help`,
   `suggestion`, `category` —, `message`, `span`, and for a suggestion its `fix`: `span`, `text`,
   `applicability` `safe` or `needs-review`), and `rendered`, the finding in the text form without colour.
   A span is `null` or `{file, start, end}`, `start` and `end` each `{line, column, offset}`, the file as
   the text form says it (§1 rule 5). Every finding is a line — §2's limit is the text form's.
4. **`artifact`**: what a build wrote — `kind` (`binary`), `name`, `path`.
5. **`test`**: a test of `lyric test` as it ends — `name`, `outcome` (`passed`, `failed`, `skipped`), and
   where there is one a `message` (why it was skipped, what ended it) and the `panic`'s code. **`tests`**:
   the run's count — `passed`, `failed`, `skipped`. **`output`**: a line the program wrote that is no event
   — `stream` (`stdout`, `stderr`) and `text`.
6. **`fix`**: a change `lyric fix` made (§6) — `path`, the `line` and `column` where it begins, the `code`
   of the finding it answers, and the `text` put in.
7. **`summary`** closes the command — `errors` and `warnings`, the findings said — once; `run` writes it
   before its program runs. **`ice`**: the toolchain's own failure (`LYR-ICE…`) — `code`, `message`, where
   it was (`while`) and its `trace`.

## 5. Lints

([11 W7 L1–L5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md),
[09 A10, A11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/09-metaprogrammierung.md))

**Conformance.** `conformance/cases/16-diagnostics/`; the places and the precedence in the toolchain's own tests
(`tests/Lyric5.Tests`, `LintTests`).

1. **Every warning is a lint**: a name — lowercase words joined by `-`, as `unused-variable` —, a group, and a
   level of its own; [Appendix A](appendix-a-diagnostics.md) lists them, `lyric explain NAME` prints one. The
   groups are `unused`, `correctness`, `resources`, `concurrency`, `deprecation`, `style`, `perf` and `docs`;
   `warnings` names every lint. A warning that is no lint does not exist.
2. A lint's **level** is `allow` — it is not said —, `warn` — it is said as a warning —, or `deny` — it is said as
   an error, with a note that names who denied it, and the build fails (exit 1, [14 §1.1](14-cli.md)).
3. A **selector** names a lint, by its name or its code, a group, or `warnings`. One that names nothing is
   refused: in an attribute `LYR-SEM0179`, in a manifest `LYR-PKG0002`, on the command line as a usage error
   (exit 2) — each with the selector closest to it in spelling, where one is.
4. **Three places, one mechanism**: `@Allow`, `@Warn`, `@Deny` with a selector on a declaration set the level
   in what the declaration holds ([11 §1](11-metaprogramming.md) rule 13); `allow`, `warn`, `deny` of a
   package's `[lints]`, each an array of selectors, set it in the package's files
   ([15 §1](15-project.md) rule 4) — a selector in one of them; `-A`, `-W`, `-D` with a selector on the command
   line of `build`, `run`, `check`, `expand`, `test`, `bench` and `fix` set it in the files of the package built.
5. **Precedence**: the narrowest attribute around the finding decides; without one the command line, then the
   manifest, then the lint's own level. Within one place the more specific selector decides — a lint over its
   group over `warnings` —, and of two alike the later.
6. The warnings of a **dependency** and of **`std`** are not said; `--warn-deps` says them, at the
   dependency's own levels — but never as errors: another package's levels do not fail this build. Their
   errors always are.
7. An `@Allow` that decides no warning — none of its lints is met in what it sits on, or a narrower level
   decides each — warns: `useless-allow` (`LYR-SEM0180`). The `@Allow` itself never decides that warning.
8. **Warnings as errors** is a switch: a profile's `denyWarnings` ([15 §4](15-project.md) rule 4) and
   `--deny-warnings` are `-D warnings` for the package built, in front of the command line's own levels —
   each warning is an error, and its note names the profile. A build script's warnings are the lint
   `build-script-warning` and denied the same way.
9. **Every lint is held by two cases** of the suite: a red one, whose program the lint reads (`warning:`
   its code), and a green one, the same program put right, which compiles in silence (`clean:` its name).
   Two lints are held otherwise: `reserved-device-name` by its green case alone, as its red program is a
   file Windows cannot hold — the toolchain's own tests read it where such a file can be made —, and
   `deprecated-edition` by neither, as it names the warning on a construct an edition retires and there is
   no edition yet.

## 6. Fixes and `lyric fix`

([11 G7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `FixTests`): the suite compiles and runs
programs; it does not change them.

1. A finding may carry a **suggestion**: a note with a change — a span and the text put in its place — and
   its **applicability**, `safe` or `needs-review`. A safe change is the finding's whole remedy and leaves
   the program's meaning as it was; one that needs a reader is a guess, or a remedy among others. The
   text form draws the line as the change would leave it (§1); the JSON form carries the change (§4 rule 3).
2. **`lyric fix [<file.lyr>]`** makes the safe changes of the findings in the package's own files —
   under its `src/`; a file alone, its own — and none in a dependency's or in `std`. A pass checks the
   program as `build` does, without building it, and makes in each file the changes that do not overlap
   one before them, in source order; the next pass checks the changed text, until a pass finds nothing to
   change. Then it says what stays — the findings without a safe change, each change that needs a reader
   among them —, and exits 1 where an error stays, else 0. A second `fix` changes nothing.
3. `fix` takes `-C`, `--offline`, the lint options of §5 rule 4 — a lint set to `allow` says nothing and
   so suggests nothing — and `--json` (§4). **`--dry-run`** makes one pass and writes nothing: it prints
   the changes as a unified diff on the standard output.
4. The safe changes: `unused-import` takes the import out, or the one name out of its list;
   `unused-var` writes `let` for `var`; `useless-try` takes a plain `try` out (`try?` and `try!` change the
   value's type, and a `catch` is code); `needless-return` takes the `return;` out; `self-assignment`
   writes `x++` for `x = x++`; `deprecated` writes the `@Deprecated`'s `replacement` where it is a name.
   A change that needs a reader: `naming`'s new name, written where the name is declared (its uses are an
   editor's rename); `self-assignment`'s removal of `x = x`, which may stand for an assignment meant
   otherwise; an unknown name's closest known one (`did you mean`).

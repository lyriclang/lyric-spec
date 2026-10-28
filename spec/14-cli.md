# The command line

> **Partly written.** §1 was written with milestone **M2** of the Lyric 5 plan, §2 with **M7**, §3
> with **M8a**; the rest comes with **M8a–M13**, spec-first: each rule lands here with its
> conformance case before or with its implementation. Source of the decisions:
> [11 Tooling and interop W1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md).

## Scope

The one binary and its verbs, option grammar, the precedence ladder, exit codes, the NDJSON output schema. Versioned as a contract (C10).

## 1. `build` and `run`

What the command line does for a single file (M2) and for a package (M7). The precedence ladder,
the NDJSON stream and the other verbs follow with their milestones; the rules below stay.

**Conformance.** Until the suite can drive the command line (M13), the toolchain's own tests
are the conformance of this section (`tests/Lyric5.Tests`, `BuildTests` and `DriverTests`).

### 1.1 Verbs and options

1. `lyric build <file.lyr>` compiles the program that starts at the file to a binary: a single
   file's own, or — for a module of a package — the package's, entered there
   ([04 §2](04-modules.md)). `lyric build` without a file builds the programs of the package
   of the current directory — the nearest `lyric.toml` at or above it —: its `src/main.lyr` and
   its `[[bin]]` programs ([15 §1](15-project.md)); `--bin <name>` names one, and a file is a
   program by itself. `lyric run [<file.lyr>] [-- args…]` builds the same way and then
   runs the binary with the arguments after `--`, on the caller's own console. `--` belongs to
   `run`: `build` refuses it. `lyric update [<package>…]` reads the packages from git anew,
   raises a tag that is a version to the newest of its line in the manifest, and writes the lock
   ([15 §3](15-project.md)); it takes `-C` and `--offline`.
2. Options take a value as `--name value` or `--name=value`
   ([11 C3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)):
   `--profile <name>` — a profile built in or the manifest's ([15 §4](15-project.md)); without
   the option the environment's `LYRIC_PROFILE`, then `debug`; an unknown name is refused, from
   either; `asan` and `tsan` need clang —, `--target <triple>`
   (a Tier 1 triple; default: this machine), `--emit ir|c` (prints instead of building; `run`
   refuses it), `-C <dir>` (the package is searched from `<dir>` instead of the current
   directory, and a relative file is relative to it). `--offline` takes no value: nothing is
   fetched, and a package read from git comes from the user's cache ([15 §2](15-project.md)).
   `--locked` takes none either: `build`, `run` and `test` take the lock as it is
   ([15 §3](15-project.md) rule 4).
   A profile's fields change for one build with `--opt <0-3>`, `--gc <immix|boehm>` and `--lto`,
   `--debug-info`, `--deny-warnings`, `--overflow-checks`, `--fast-math`, each with its `--no-`
   form; a field flag
   is over the profile ([11 C4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)), and a flag with its `--no-` form is refused.
3. The command line is strict: an unknown verb, option or value is refused.
4. A binary for a target that is not this machine is built and not run: `run` refuses it and
   names the binary.
5. Without a file and without a manifest at or above the directory there is nothing to build
   (`LYR-CLI0004`). A package without `src/main.lyr` is a library: `build` checks it
   ([15 §2](15-project.md)) — `build --lib` builds it for C (rule 9) —, and `run` has no program
   there (`LYR-CLI0005`).
6. **`lyric expand [<file.lyr>]`** prints the program's entry module after its macros' expansion
   ([11 §5](11-metaprogramming.md)) to standard output: the results in the sites' places, the
   rest as written, in the formatter's form — comments fall, as do the module's header line and
   attributes. It chooses the program as `run` does (`--bin`, `-C`, the profile and the target,
   which `comptime` reads), builds nothing, and refuses `--emit`. The program is resolved and
   expanded, not checked: what the expansion needs is reported with exit 1 — a site of no macro,
   a macro's own error —, and a type error after it is `build`'s to find. Without a site, the
   module prints as it is.
7. **`lyric fix [<file.lyr>]`** makes the safe changes the findings suggest in the package's own
   files, and **`--dry-run`** prints them as a diff instead ([16 §6](16-diagnostics.md)).
8. **`lyric check [<file.lyr>]`** takes the programs `build` would take — or checks the library, as
   `build` does — through everything a build does before the C: the build scripts, for what they
   write into `gen/` ([15 §8](15-project.md)), the front end and the lints, `comptime`, and the
   lowering. It says what `build` says, exits as `build` does (§1.3), and makes neither C nor a
   binary. It takes `build`'s options but `--emit`, `--lib` and `--shared`.
9. **`lyric build --lib`** builds the package's library for C — its `src/lib.lyr` and what that
   imports — instead of its programs ([13 §4](13-abi.md#4-exports-and-libraries)): the archive
   `lib<name>.a` and the header `<name>.h`, or with **`--shared`** a shared library in the
   archive's place. Without `src/lib.lyr` there is nothing to build (`LYR-CLI0001`); `--shared`
   without `--lib`, and `--lib` with a file, `--bin` or `--emit`, are refused (exit 2).

### 1.2 Where the files go

1. A single file is an implicit package named after the file
   ([11 C8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md));
   a package is named in its manifest ([15 §1](15-project.md)).
2. `out/` lies by the manifest — the nearest `lyric.toml` at or above the file, also for a single
   file beside a package's `src/`; without one, at the nearest directory upward holding `.git`;
   without that, by the file (P5). Under it, the binary is `out/<profile>/<target>/<name>`, with
   the executable suffix of the target — named after the package for its `src/main.lyr`, after
   the module's last segment for another module of the package, after the file for a single file
   —, a library for C beside it ([13 §4](13-abi.md#4-exports-and-libraries) rule 7), and
   `out/cache/` holds what the build keeps between runs (P4; 01 L7).
3. An unchanged program compiles nothing twice: the same sources — every module of the program,
   the standard library's included —, toolchain and options reuse the cache, and the binary is
   linked only when an input to it changed (11 C9). A build that reuses the cache **says again
   what the build that filled it said**: the same findings, in the form and the colour the command
   line asks for now, counted in its `summary` ([16 §4](16-diagnostics.md)).
4. A build holds **`out/.lock`** while it writes into `out/`
   ([11 P5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)): a second build of the package waits for the first, and says so
   once. The lock is the operating system's on an open file; it ends with its process.

### 1.3 Exit codes

As [11 C5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md):

| Code | Meaning |
|---|---|
| 0 | done |
| 1 | the program or its manifest was refused: a compile error, or a construct the compiler does not translate yet |
| 2 | the command line or the environment: unknown verb, option or value, a missing file, no package to build, a program to run among several unnamed, no C compiler, a git repository that cannot be reached, a toolchain below what a package asks for |
| 101 | the toolchain itself failed (`LYR-ICE0001`) |
| the program's | `run` passes the program's own exit through: its `main` value masked to `0..255` ([13 §1.5](13-abi.md)), 101 for a panic |

## 2. `clean`, `metadata`, `add` and `remove`

The verbs about a package besides building it — the package of the nearest `lyric.toml` at or
above the current directory, or above `-C <dir>`; without one there is nothing to do
(`LYR-CLI0004`).

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `OutTests`,
`ManifestEditTests`).

1. **`lyric clean`** removes the package's `out/`, once a build that writes into it is done
   (§1.2).
2. **`lyric metadata`** writes the package as one JSON object, on one line, to standard output
   ([11 P10](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)):
   - `"version"`, the schema's: 1; `"toolchain"`, the toolchain's version; `"root"`, the
     package's name;
   - `"packages"`, the graph's, each with its `"name"`, `"version"`, `"edition"`, `"manifest"`,
     its `"toolchain"` pin where it has one, where it is read from — `"path"`, its directory, or
     `"git"` with the `"url"`, the revision (`"tag"`, `"branch"` or `"rev"`, none for the default
     branch) and the `"commit"` — and the `"dependencies"` it declares;
   - `"programs"`, each with its binary's `"name"`, its `"entry"` file and its `"module"`;
   - `"profiles"`, each with its `"name"`, its `"base"` — the built-in profile it comes from —
     and its fields;
   - `"targets"`, the Tier 1 triples, `"host"`, this machine's, and `"out"`.

   Within a schema version a field may be added, none is changed or removed
   ([11 C10](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)). Its options are `-C`, `--offline`, and `--json`, the one form
   there is.
3. **`lyric add <name> --path <dir>`** or **`--git <url>`**, with at most one of `--tag`,
   `--branch` and `--rev`, writes the dependency into `[dependencies]` as one line —
   `geo = { path = "../geo" }`, the path relative to the manifest — in place of the line that
   names it, or after the table's last, or in a table it begins at the end. Every other line of
   the manifest stays as it was. The graph is then read with the dependency
   ([15 §2](15-project.md)); a graph that refuses it leaves the manifest as it was, and the
   refusal is the graph's. With **`--vendor`** the line names a source tree and goes into
   `[native.vendor]` instead ([15 §5.3](15-project.md#53-source-trees)): `--git <url>` and a
   revision as above, read once to show the revision is there — the lock gets it when a build
   needs it —, or **`--url <url>`**, the file loaded and its SHA-256 written as the line's
   `hash`. `--path` names no tree, and `--url` goes with `--vendor` alone (`LYR-CLI0003`).
4. **`lyric remove <name>`** takes the dependency's line out of `[dependencies]`, and the graph —
   the lock with it ([15 §3](15-project.md)) — is read again; with `--vendor`, the tree's line
   out of `[native.vendor]`. A name the table does not hold is refused (`LYR-CLI0003`).
5. A dependency written otherwise than as one line — a table of its own, dotted keys — is the
   person's to edit: `add` and `remove` refuse it (`LYR-CLI0008`). Both take `-C` and
   `--offline`.

## 3. `test`

The package's tests ([10 B12](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md), [07 V4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)) — the package of the nearest `lyric.toml`,
as in §2.

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `TestCommandTests`, `DocTestTests`;
the standard library's own tests through it, `StdTests`).

1. **`lyric test`** builds every function the package marks `@Test`
   ([11 §1](11-metaprogramming.md)) — in its modules under `src/` and under `tests/`
   ([15 §7](15-project.md)) — into one program for this machine, under the profile asked for as
   `build` takes it (§1.1), and runs it in the package's directory, the one its `lyric.toml`
   stands in, wherever `lyric` is called: a test reads its package's files by their paths in it
   (the sweep after M10, X1). A library has tests as well. It takes no file. Built
   for another machine — or for the target `--target` names, as `run` takes it — the program is
   named and not run, exit 2.
2. The tests run one after another — module by module in the order of their paths, each
   module's in the order it writes them —, each in a task of its own: a panic or an error that
   leaves a test fails it, and the run goes on. A test with a `skip` is named and not run.
   A test marked **`parallel`** — `@Test { parallel = true }` — runs beside the others marked so,
   after the rest, each in a task of its own on a pool of a thread for each processor (X3: an
   opt-in, since what tests share — the working directory, the environment, a global `var` — they
   share as threads do). Their lines come in their order; their `timeout`s are one deadline, the
   longest of them, from their start; and a parallel test has no subtest — `subtest` fails it, as
   a subtest is reported under the test that runs alone.
3. After each test has ended, a line: `ok`, `FAIL` with the panic or the error below it, or
   `skip` with the reason — a test's own output comes before its line —; then the count. A
   subtest — `std.test.subtest("name") { … }` — runs in a task of its own and has a line of its
   own, `app.tests.math.table/name`; one that fails fails its test, and the test goes on.
   A test that outlives its `timeout` ends the run, with its `FAIL` line, exit 1: a task gives
   way only where it waits, so nothing stops it short of the end. A failure's further lines —
   the first difference of two values too long to compare by eye — stand under its first.
   `-f <text>` (`--filter <text>`) runs the tests whose name — the module's path and the
   function's, `app.tests.math.adds` — holds the text.
4. The exit is 0 when every test held — or when there is none to run —, and 1 when one failed or
   the program was refused (§1.3).
5. **Doc-tests**: each ` ```lyric ` block in a documentation comment — `///` or `//!` — of the
   package's modules under `src/` is a test of its own, after the marked ones, module by module in
   the order of their paths. It is named `doc: <module>.<element> (<file>:<line>)` — the element
   the comment documents, a member as `Type.member`, the module alone for `//!` — and `-f` and the
   count take it as the others. Its fence says what it must do, as the Book's snippets
   ([Book](https://lyric.oil1i.de/dev/book/)) do: `lyric` builds and runs, and prints what an
   ` ```output ` block right below it says; `lyric,no_run` builds; `lyric,compile_fail=CODE` fails
   to build with that code and no other, and says what a ` ```diagnostic ` block right below it
   says. A block without `fn main` is made a program as the Book's are — its statements the body
   of `main`, or its declarations beside an empty one —, and imports the element it documents, its
   type for a member, where that is `pub` and the block imports nothing of the module itself. A
   comment whose block the form refuses fails a test named after its module. Built for another
   machine, no doc-test is built.
6. **`--no-run`** builds the program and runs none of it: its path is the last line printed, and no
   doc-test is built — each is a program of its own. It is what a debugger launches (§12).

## 4. `bench`

The package's benchmarks ([12 §Benchmarks](12-stdlib.md), [10 X4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)) — the package of the nearest
`lyric.toml`, as in §2.

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `BenchCommandTests`).

1. **`lyric bench`** builds every function the package marks `@Bench` — in its modules under
   `src/` and under `tests/` — into one program for this machine, in the **release** profile
   unless `--profile` names another, and runs them one after another on one thread, in the
   package's directory as `test` runs its program; `--target` as `test` takes it (§3). The files
   of `--save` and `--compare` are where the command line names them.
2. A line for each: `bench app.tests.speed.reads: 412.3 ns/op, 0 allocs/op, 0 B/op, 2483.2 MB/s
   (290000 runs)` — the nanoseconds a run, the allocations a run and their bytes, the megabytes a
   second where the benchmark said its bytes, and the runs measured. `-f <text>`
   (`--filter <text>`) runs those whose name holds the text; where none does, or there is none,
   a line says so.
3. **`--save <file>`** writes the run's times to the file, a line a benchmark — its name, then the
   nanoseconds, the allocations and the bytes a run, apart by tabs —; **`--compare <file>`** reads
   such a file, and the line of a benchmark it has a row for ends with how its time changed:
   `, was 400.1 ns/op: +3.0%`.
4. The exit is 0, and 1 where the file to compare with or to save to could not be read or
   written, or the program was refused (§1.3).

## 5. The verbs and their options

([11 C2, C3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `VerbTableTests`).

1. The verbs and their options are **one table**: the command line is read by it, `lyric help`
   prints it, and the table below is printed from it (`lyric help --markdown`). An option the table
   does not give a verb is refused with exit 2 (§1.1 rule 3), as is a value missing or a value given
   to a flag (`--lto=yes`).
2. **`lyric help`** lists the verbs and the options every verb takes; **`lyric help <verb>`** and
   **`lyric <verb> --help`** (`-h`) list the verb's own. A `--help` after `run`'s `--` is the
   program's.
3. The options every verb takes, before or after the verb: `--color <auto|always|never>`,
   `--absolute-paths`, `--max-errors <n>` ([16 §1](16-diagnostics.md)); where the table marks the
   verb, `--json` ([16 §4](16-diagnostics.md)) and the lint options `-A`, `-W`, `-D <lint>` and
   `--warn-deps` ([16 §5](16-diagnostics.md)). A field of the profile is `--x` and `--no-x`.

| verb | words | options | lints | `--json` |
|---|---|---|---|---|
| `build` | `[<file.lyr>]` | `--profile <name>`, `--opt <0-3>`, `--gc <immix|boehm>`, `--[no-]lto`, `--[no-]debug-info`, `--[no-]deny-warnings`, `--[no-]overflow-checks`, `--[no-]fast-math`, `--target <triple>`, `-C <dir>`, `--bin <name>`, `--offline`, `--locked`, `--emit <ir|c>`, `--lib`, `--shared` | yes | yes |
| `run` | `[<file.lyr>] [-- <args>…]` | `--profile <name>`, `--opt <0-3>`, `--gc <immix|boehm>`, `--[no-]lto`, `--[no-]debug-info`, `--[no-]deny-warnings`, `--[no-]overflow-checks`, `--[no-]fast-math`, `--target <triple>`, `-C <dir>`, `--bin <name>`, `--offline`, `--locked` | yes | yes |
| `check` | `[<file.lyr>]` | `--profile <name>`, `--opt <0-3>`, `--gc <immix|boehm>`, `--[no-]lto`, `--[no-]debug-info`, `--[no-]deny-warnings`, `--[no-]overflow-checks`, `--[no-]fast-math`, `--target <triple>`, `-C <dir>`, `--bin <name>`, `--offline`, `--locked` | yes | yes |
| `expand` | `[<file.lyr>]` | `--profile <name>`, `--opt <0-3>`, `--gc <immix|boehm>`, `--[no-]lto`, `--[no-]debug-info`, `--[no-]deny-warnings`, `--[no-]overflow-checks`, `--[no-]fast-math`, `--target <triple>`, `-C <dir>`, `--bin <name>`, `--offline`, `--locked` | yes | — |
| `test` | — | `--profile <name>`, `--opt <0-3>`, `--gc <immix|boehm>`, `--[no-]lto`, `--[no-]debug-info`, `--[no-]deny-warnings`, `--[no-]overflow-checks`, `--[no-]fast-math`, `--target <triple>`, `-C <dir>`, `--offline`, `--locked`, `--filter, -f <text>`, `--no-run` | yes | yes |
| `bench` | — | `--profile <name>`, `--opt <0-3>`, `--gc <immix|boehm>`, `--[no-]lto`, `--[no-]debug-info`, `--[no-]deny-warnings`, `--[no-]overflow-checks`, `--[no-]fast-math`, `--target <triple>`, `-C <dir>`, `--offline`, `--locked`, `--filter, -f <text>`, `--save <file>`, `--compare <file>` | yes | — |
| `fix` | `[<file.lyr>]` | `-C <dir>`, `--offline`, `--dry-run` | yes | yes |
| `fmt` | `[<file.lyr>…]` | `-C <dir>`, `--check`, `--diff` | — | — |
| `doc` | — | `-C <dir>`, `--offline`, `--out <dir>`, `--std` | — | — |
| `api` | — | `-C <dir>`, `--json`, `--diff <rev>`, `--std` | — | — |
| `lsp` | — | `--stdio` | — | — |
| `dap` | — | — | — | — |
| `env` | — | `-C <dir>`, `--profile <name>`, `--target <triple>`, `--opt <0-3>`, `--gc <immix|boehm>`, `--[no-]lto`, `--[no-]debug-info`, `--[no-]deny-warnings`, `--[no-]overflow-checks`, `--[no-]fast-math`, `--offline`, `--json` | — | — |
| `new` | `<name>` | `--lib`, `--[no-]git`, `-C <dir>` | — | — |
| `init` | — | `--lib`, `--name <name>`, `--[no-]git`, `-C <dir>` | — | — |
| `update` | `[<package>…]` | `-C <dir>`, `--offline` | — | — |
| `add` | `<name>` | `--path <dir>`, `--git <url>`, `--tag <tag>`, `--branch <branch>`, `--rev <commit>`, `--vendor`, `--url <url>`, `-C <dir>`, `--offline` | — | — |
| `remove` | `<name>` | `--vendor`, `-C <dir>`, `--offline` | — | — |
| `clean` | — | `-C <dir>` | — | — |
| `metadata` | — | `-C <dir>`, `--offline`, `--json` | — | — |
| `toolchain` | `<install|list|default|remove|update> [<version>]` | `--available` | — | — |
| `explain` | `<code>` | — | — | — |
| `completions` | `<bash|zsh|fish|pwsh>` | — | — | — |
| `version` | — | — | — | — |
| `help` | `[<verb>]` | `--markdown` | — | — |

## 6. `env`

([11 C4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `VerbTableTests`).

1. **`lyric env`** says every setting a build of the package here reads — the toolchain, the
   standard library, the manifest, the C compiler, the cache, the profile and each of its fields,
   the target, and each `LYRIC_*` variable that is set — with its value and **where it comes
   from**: `command line`, the variable's name (`LYRIC_PROFILE`), `lyric.toml`, or `default`. The
   command line is over the environment, the environment over the manifest, the manifest over the
   default.
2. It takes the options that change a setting — `-C`, `--profile`, the profile's fields,
   `--target` — so that it says what the build with them would read. **`--json`** writes one
   document instead: `{"version": 1, "settings": [{"name", "value", "origin"}, …]}`.

## 7. `new`, `init` and `completions`

([11 C2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `NewCommandTests`).

1. **`lyric new <name>`** makes the directory `<name>` and a package in it; **`lyric init`** makes
   the package in the directory it runs in — `-C` names another —, named after the directory unless
   `--name <name>` names it. The files: `lyric.toml` (`[package]` with `name` and
   `version = "0.1.0"`), `src/main.lyr` printing `Hello, world!` — or, with **`--lib`**, a library's
   `src/lib.lyr` —, and `.gitignore` holding `out/`; no build script. A file `init` finds there is
   kept.
2. A name that is no package name ([15 §1](15-project.md) rule 2) is refused with exit 2, and with
   the name it would be where there is one (`My-App` → `my_app`). `new` into a directory that is
   there, and `init` where a `lyric.toml` is, are refused (`LYR-CLI0021`, exit 2).
3. **git**: `--git` makes a repository in the package's directory, `--no-git` none; without either,
   the environment's **`LYRIC_GIT_ON_NEW`** decides — `1` or `true` makes one where no repository
   holds the directory already and git is found. The command line is over the environment (§6).
   A `--git` that git refuses, or that finds no git, fails the command (`LYR-CLI0021`) after the
   files are written.
4. **`lyric completions <bash|zsh|fish|pwsh>`** prints the shell's completion script — the verbs,
   and for each its options and the options every verb takes, as §5's table has them — and runs
   nothing. Another shell is refused (exit 2).

## 8. `fmt`

([11 E5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `FmtCommandTests`; the form itself
in `tests/Lyric.Tests.Formatting`).

1. **`lyric fmt`** puts Lyric files in **the one form**: there are no options that change it. Without
   words it takes the package found from here (`-C` names another directory) — every `.lyr` file
   under `src/` and `tests/`, and `build.lyr` —; with words, the files named and no others.
2. The form keeps what the program means, its comments and the parentheses it writes; formatting a
   formatted file changes nothing. A file in the form is not written. A file is written with LF line
   ends and one final newline.
3. A file that does not parse is **left as it is**: its findings are said, and the command ends with
   exit 1 after the other files are formatted.
4. **`--check`** writes nothing: it names each file that would change, one to a line, and ends with
   exit 1 where one would, 0 where none would. **`--diff`**, with `--check` only, shows each change
   as a unified diff instead of the name.

## 9. `doc`

([11 E7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `DocCommandTests`).

1. **`lyric doc`** writes the reference of the package found from here (`-C` names another
   directory) as static pages, into `out/doc/` or the directory `--out` names: a page for the
   package, one for each module and one for each type, from the `pub` declarations the checker sees
   and their documentation comments. A package that does not check is not documented: its findings
   are said and the command ends with exit 1, writing nothing.
2. A **module's documentation** is the `//!` lines that open its file
   ([01](01-lexical.md)); an item's is the `///` lines above it. A page shows each item's signature
   as written, its documentation as Markdown, and for a type its conformances — those its
   declaration lists and those blocks of the package add.
3. Each member stands under an anchor that names its kind: `#field.x`, `#method.push`,
   `#variant.Up`, `#assoc.Item`, `#const.x` on a type's page, `#fn.name`, `#const.name`,
   `#type.Alias` on a module's. A second member of one name and kind takes `-2`, and so on.
4. **`--std`** writes the standard library's reference instead of a package's.

## 10. `api`

([11 E7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md),
[07 B3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `ApiCommandTests`).

1. **`lyric api`** prints the **public surface** of the package found from here (`-C` names another
   directory): what `lyric doc` documents (§9) — each `pub` item of its modules, each member of a
   type, each conformance a type's declaration lists or a block of the package adds — **one line per
   element**. A package that does not check prints nothing: its findings are said and the command
   ends with exit 1. **`--std`** prints the standard library's surface instead.
2. A line is the element's **signature with its qualified path for its name**
   (`pub fn geo.distance(a: Point, b: Point): float`, `pub geo.Point.y: float = 0.0`,
   `variant geo.Dir.Up`); a conformance is a line of its own (`geo.Point :: Equatable`), and a
   type's line carries no `::` list. An interface's method that has a body ends with `{ … }`.
3. The lines are written in **one spelling**: comments, line breaks, spaces and a trailing comma do
   not change a line; a parameter's name does, since a call may name its argument. The lines are
   sorted by path, a type's own line before its conformances: the same declarations print the same
   text, byte for byte.
4. **`--json`** prints the same elements as one document:
   `{"package", "version", "elements": [{"module", "path", "kind", "signature", "line", "owner"?, "default"?}]}`,
   in the text's order; `kind` is one of `fn`, `struct`, `class`, `enum`, `interface`, `type`,
   `const`, `field`, `method`, `variant`, `assoc`, `conformance`; `owner` is the kind of a member's
   type, `default` is present and true where a field or an associated type has a value or an
   interface's method has a body.
5. **`--diff <rev>`** compares the surface with the package's as the **git revision** `<rev>` of its
   repository holds it — read from the repository, not from the working tree. Each element is
   **removed**, **added** or **changed** (the same kind and path with another line). Removed and
   changed are **breaking**; added is breaking only where the language makes code written before
   write it out: a field without a value in a struct or class (an initializer names it), a variant of
   an enum (a `match` over every case misses it), an interface's method without a body or
   associated type without a value (each conformer must give it). An interface's method that only
   gains a body is compatible; one that loses it is breaking.
6. The diff lists the breaking changes first, each with the old line (`-`) and the new (`+`), then
   the compatible ones, and ends with the count. The command ends with **exit 1** where a change is
   breaking and 0 where none is; **`--json`** prints
   `{"breaking": n, "changes": [{"change", "breaking", "path", "kind", "old"?, "new"?, "why"}]}`.
7. A directory in no git repository, a revision git cannot read, or one without the package's
   `lyric.toml` is **LYR-CLI0022**, exit 2. `--diff` with `--std` is refused with exit 2.

## 11. `lsp`

([11 E1, E3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** The toolchain's own tests (`tests/Lyric.Tests.Lsp`; the verb in `tests/Lyric5.Tests`,
`LspCommandTests`).

1. **`lyric lsp`** is the language server: it speaks the Language Server Protocol with an editor
   over its standard input and output until the editor says `exit`, and ends with exit 0 after a
   `shutdown`, 1 without one. **`--stdio`** names the one way there is; editors pass it.
2. A file is analysed **as a module of its package** where it lies under the `src/` or `tests/` of
   the nearest `lyric.toml` above it: with every other module of the package, in the one
   compilation `lyric test` makes of them ([§3](#3-test)), and the packages of its graph. Any other
   file is analysed **alone**, with the standard library, as `lyric check <file>` checks it.
3. The findings the editor shows are those `lyric check` says of the same text, except those only
   the lowering finds — a monomorphization that does not end (`LYR-SEM0197`) is said by the build;
   the text of every file the editor holds open counts instead of what is saved.
4. The server reads the manifest and the graph as a build reads them, except that it **fetches
   nothing** — a package from git comes from the cache — and **writes nothing**: `lyric.lock` is
   left as it is. A manifest it cannot read leaves the file analysed alone, and the server says why
   in the editor's log.
5. An edit arrives as the ranges it replaces. A client that asks for a document's findings
   (`textDocument/diagnostic`) gets them for the documents it has open; the findings of every other
   file of the package are sent to it (`textDocument/publishDiagnostics`), as to a client that does
   not ask.
6. A `comptime` site of the program is evaluated under at most a tenth of the toolchain's budget
   ([11 §2](11-metaprogramming.md#2-comptime) rule 5); a site that runs out of it is shown without a
   value and without a finding — the build evaluates it under the program's budget. The standard
   library's sites keep theirs.
7. What a declaration is under the cursor — its signature, its uses, its new name — is answered for
   every package the editor has analysed: the uses of a library's function include those of an open
   program that depends on it. A rename edits each of them, and nothing in a package read from git or
   in the standard library; a rename that would is refused, and says why.
8. A finding links the page of its code in the catalog, of the toolchain's version, the one
   `lyric explain` names. The quick fixes at a place are the changes the findings' notes suggest,
   word for word — the one `lyric fix` applies preferred, the others offered —, and for a lint the
   `@Allow` of its code above the declaration it stands in; the editor composes no change of its
   own.
9. The document's form is `lyric fmt`'s ([§8](#8-fmt)), sent as the lines it changes. The command
   `lyric.expand` answers the open module with its macros expanded, as `lyric expand` prints it.
10. Each `@Test` function of a package's file and each runnable block of its documentation carries
    two commands for the editor to run, *run* and *debug*, with the package's directory and the
    name `lyric test` gives it — `app.tests.check.adds`, `doc: app.add (src/lib.lyr:3)`; the request
    `lyric/tests` lists them for a document. The server runs no test: the editor runs
    `lyric test -f <name>` ([§3](#3-test)).

## 12. `dap`

([11 E4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md),
[01 L12](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `DapCommandTests`).

1. **`lyric dap`** is the debug adapter: it speaks the Debug Adapter Protocol with an editor over
   its standard input and output, and **lldb-dap** behind it does the debugging — breakpoints with
   their conditions, logpoints, stepping, threads, attaching are lldb's. Where no lldb-dap is
   found (`LYRIC_LLDB_DAP` names one, else the path and Xcode's), each request is refused with the
   reason.
2. A **`launch`** names in `program` a package's directory or a `.lyr` file: the adapter builds it
   in the debug profile first, what the build says reaches the editor's console, and a program
   that does not build is refused; the binary built is what runs, with the `args` and `cwd` the
   launch gives.
3. **A panic** is the exception filter `lyric-panic`, on unless the editor turns it off: the
   program stops where it panics, before the panic leaves its task. It is the only filter offered.
4. A frame is shown by its **Lyric name** (`app.main.deep`) at its Lyric line. A build writes the
   names beside the binary — `<binary>.lyric-names`, a line per function: its C name, a tab, its
   Lyric name —; a frame of the runtime keeps its name and is marked as set back (`subtle`).
5. A **value** is shown as Lyric writes it: a local by its Lyric name, a string as its text, an
   array as its length with its elements, an optional as its value or `none`, an enum as its
   variant with its payload, a struct's and a class's fields by their names; what the compiler made
   — its temporaries, its locals of its own — is not shown, nor what the runtime keeps beside the
   program. The names file says which C type is which Lyric type (`type`, `variant`, `global`
   lines beside the functions'); the toolchain's `lldb/lyric_lldb.py` reads it, and lldb loads it
   with `command script import`.
6. A **line breakpoint** stops at the line's code: the function's own setting up stands at the
   function's line, never at a line after it. The sources are found where they lie, by the names
   the binary writes for them (§1.2).
7. On **Windows** the adapter is measured, not promised: the binary carries PDB, and whether
   lldb-dap reads it is reported, not gated.
8. A `launch` with a **`test`** debugs the package's tests whose names hold it: the program
   `lyric test --no-run -f <test>` builds (§3), run in the package's directory as `test` runs it.

## 13. `toolchain`

([11 T1–T8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md),
[14 C9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/14-website.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `ToolchainCommandTests`, against
a mirror served on the machine): a conformance case fetches nothing.

1. **The home.** Toolchains are installed side by side under `~/.lyric` — or the directory
   **`LYRIC_HOME`** names: `toolchains/<version>/` holds each as its archive unpacked it,
   `config.toml` names the default (`default = "<version>"`, the one key it takes), and `bin` is a
   link to the default's directory — a symbolic link, on Windows a junction —, so that `bin` on the
   `PATH` runs the default. A directory an install has not finished is no toolchain.
2. **`lyric toolchain install <version|dev|stable>`** installs a toolchain for this machine's
   target. `dev` and `stable` name the newest version of their channel; a version is one its
   channel lists, written with its build part (`+…`) or without. A development build's version
   (`-dev.…`) is the `dev` channel's, every other the `stable` channel's. The first toolchain
   installed becomes the default. A version installed already is said and fetched no further.
3. **What an install trusts.** The channel's index is fetched with its signature and checked with
   the key the toolchain carries; the archive is fetched no further than the size the index gives
   and checked against its SHA-256; it is unpacked beside the toolchains and checked against its
   own `toolchain.json` — its version, its target and every file; only then is it moved into
   place. A difference anywhere installs nothing (`LYR-CLI0024`), and a run cut short leaves
   nothing a later one counts as installed.
4. **Where from.** The index and the archives come from the mirror, and from GitHub's releases
   where the mirror cannot be reached; a signature or a hash that does not hold is never routed
   around. **`LYRIC_MIRROR`** names another mirror in place of both, and **`LYRIC_MIRROR_KEY`**
   the key its signatures are checked with — set without a mirror, it is refused. A toolchain
   that carries no key installs only from such a mirror.
5. **`lyric toolchain list`** names the installed toolchains, the newest first, the default
   marked; with **`--available`**, the versions both channels offer, with their dates, those
   installed marked. A channel that cannot be fetched is said, and is an error only where neither
   can.
6. **`lyric toolchain default [<version>]`** says the default, or makes the installed version the
   default: `config.toml` written, `bin` pointed at it. A `bin` that is no link is refused, and
   left as it is.
7. **`lyric toolchain remove <version>`** removes an installed toolchain; not the default, nor the
   toolchain the command runs from (`LYR-CLI0025`).
8. **`lyric toolchain update`** installs the newest version of the default's channel beside the
   default and makes it the default; the old one stays until it is removed. Where the default is
   the newest, it is said.
9. While an archive is fetched, its progress is drawn on the standard error where that is a
   terminal, and nowhere else.
10. Every refusal is the environment's, exit 2: an action or a version missing, an unknown action,
    `--available` beside another action (§1.3); a toolchain that cannot be fetched
    (`LYR-CLI0023`); one that is not what its index says (`LYR-CLI0024`); a change the installed
    toolchains refuse (`LYR-CLI0025`).

### 13.1 The archive, the index and the signature *(informative)*

- **The archive** of a toolchain is one per Tier 1 target: `.zip` for Windows, `.tar.gz` for the
  others, holding the binary, `stdlib5/`, the runtime as C source and prebuilt for the archive's
  target, `lldb/`, `LICENSE` and the notices, and **`toolchain.json`** —
  `{"version", "triple", "files": [{"path", "size", "sha256"}, …]}`, every other file with its
  size and SHA-256.
- **The index** of a channel is `dev.json` or `stable.json`:
  `{"channel", "versions": [{"version", "date", "archives": {"<triple>": {"file", "size", "sha256"}}}]}`.
  On a mirror it lies at `<base>/<channel>.json`, its archives under `<base>/<channel>/`; on GitHub
  the release `dev` carries the development build with `dev.json`, the release `channels` carries
  `stable.json`, and each stable version has its release `v<version>`.
- **The signature** is minisign's, beside the file as `<file>.minisig`: Ed25519 over the file's
  BLAKE2b-512 hash, and over that signature with its trusted comment; minisign's legacy form,
  which signs the file itself, is refused.

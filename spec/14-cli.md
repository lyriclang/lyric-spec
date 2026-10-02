# The command line

> **Partly written.** §1 was written with milestone **M2** of the Lyric 5 plan; the rest comes with
> **M7–M13**, spec-first: each rule lands here with its conformance case before or with its
> implementation. Source of the decisions:
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
   ([04 §2](04-modules.md)). `lyric build` without a file builds the package of the current
   directory — the nearest `lyric.toml` at or above it — from its `src/main.lyr`
   ([15 §1](15-project.md)). `lyric run [<file.lyr>] [-- args…]` builds the same way and then
   runs the binary with the arguments after `--`, on the caller's own console. `--` belongs to
   `run`: `build` refuses it. `lyric update [<package>…]` reads the packages from git anew and
   writes the lock ([15 §3](15-project.md)); it takes `-C` and `--offline`.
2. Options take a value as `--name value` or `--name=value`
   ([11 C3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)):
   `--profile debug|release` (default `debug`; `asan` and `tsan` need clang), `--target <triple>`
   (a Tier 1 triple; default: this machine), `--emit ir|c` (prints instead of building; `run`
   refuses it), `-C <dir>` (the package is searched from `<dir>` instead of the current
   directory, and a relative file is relative to it). `--offline` takes no value: nothing is
   fetched, and a package read from git comes from the user's cache ([15 §2](15-project.md)).
3. The command line is strict: an unknown verb, option or value is refused.
4. A binary for a target that is not this machine is built and not run: `run` refuses it and
   names the binary.
5. Without a file and without a manifest at or above the directory there is nothing to build
   (`LYR-CLI0004`). A package without `src/main.lyr` is a library: `build` checks it
   ([15 §2](15-project.md)), and `run` has no program there (`LYR-CLI0005`).

### 1.2 Where the files go

1. A single file is an implicit package named after the file
   ([11 C8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md));
   a package is named in its manifest ([15 §1](15-project.md)).
2. `out/` lies by the manifest — the nearest `lyric.toml` at or above the file, also for a single
   file beside a package's `src/`; without one, at the nearest directory upward holding `.git`;
   without that, by the file (P5). Under it, the binary is `out/<profile>/<target>/<name>`, with
   the executable suffix of the target — named after the package for its `src/main.lyr`, after
   the module's last segment for another module of the package, after the file for a single file
   —, and `out/cache/` holds what the build keeps between runs (P4; 01 L7).
3. An unchanged program compiles nothing twice: the same sources — every module of the program,
   the standard library's included —, toolchain and options reuse the cache, and the binary is
   linked only when an input to it changed (11 C9).

### 1.3 Exit codes

As [11 C5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md):

| Code | Meaning |
|---|---|
| 0 | done |
| 1 | the program or its manifest was refused: a compile error, or a construct the compiler does not translate yet |
| 2 | the command line or the environment: unknown verb, option or value, a missing file, no package to build, no C compiler, a git repository that cannot be reached |
| 101 | the toolchain itself failed (`LYR-ICE0001`) |
| the program's | `run` passes the program's own exit through: its `main` value masked to `0..255` ([13 §1.5](13-abi.md)), 101 for a panic |

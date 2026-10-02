# The command line

> **Partly written.** §1 was written with milestone **M2** of the Lyric 5 plan, §2 with **M7**; the
> rest comes with **M7–M13**, spec-first: each rule lands here with its conformance case before or
> with its implementation. Source of the decisions:
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
   `run`: `build` refuses it. `lyric update [<package>…]` reads the packages from git anew and
   writes the lock ([15 §3](15-project.md)); it takes `-C` and `--offline`.
2. Options take a value as `--name value` or `--name=value`
   ([11 C3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)):
   `--profile <name>` — a profile built in or the manifest's ([15 §4](15-project.md)); without
   the option the environment's `LYRIC_PROFILE`, then `debug`; an unknown name is refused, from
   either; `asan` and `tsan` need clang —, `--target <triple>`
   (a Tier 1 triple; default: this machine), `--emit ir|c` (prints instead of building; `run`
   refuses it), `-C <dir>` (the package is searched from `<dir>` instead of the current
   directory, and a relative file is relative to it). `--offline` takes no value: nothing is
   fetched, and a package read from git comes from the user's cache ([15 §2](15-project.md)).
   A profile's fields change for one build with `--opt <0-3>` and `--lto`, `--debug-info`,
   `--deny-warnings`, `--overflow-checks`, `--fast-math`, each with its `--no-` form; a field flag
   is over the profile ([11 C4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)), and a flag with its `--no-` form is refused.
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
   refusal is the graph's.
4. **`lyric remove <name>`** takes the dependency's line out of `[dependencies]`, and the graph —
   the lock with it ([15 §3](15-project.md)) — is read again. A name the table does not hold is
   refused (`LYR-CLI0003`).
5. A dependency written otherwise than as one line — a table of its own, dotted keys — is the
   person's to edit: `add` and `remove` refuse it (`LYR-CLI0008`). Both take `-C` and
   `--offline`.

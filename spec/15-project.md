# Projects

> **Partly written.** §1 and §2 were written with milestone **M7** of the Lyric 5 plan (slices S1,
> S4, S5a); the rest follows with M7, spec-first: each rule lands here with its conformance case before
> or with its implementation. Source of the decisions:
> [11 Tooling and interop W2/W3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md), [07 Modules](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md).

## Scope

`lyric.toml`, profiles, targets, the lock file, `out/`, build scripts and their trust rule, reproducibility.

## 1. The manifest

A package's manifest, `lyric.toml` at its root, is read and never run
([11 P1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md), [07 V7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)).

**Conformance.** `conformance/cases/15-project/`, package cases; the TOML subset in the
toolchain's own tests (`tests/Lyric5.Tests`, `ManifestTests`).

1. A manifest is **TOML**, the part of it a manifest needs: tables and arrays of tables; bare,
   quoted and dotted keys; basic and literal strings, integers, booleans, arrays and inline
   tables; comments. Floats, dates and times, and multi-line strings are refused, as is what TOML
   itself refuses — a key or a table defined twice, a value where a table is needed
   (`LYR-PKG0001`, at its line and column).
2. **`[package]`** is required. Its `name` is a lowercase letter followed by lowercase letters,
   digits and `_` — the first segment of every module path of the package
   ([04 §2](04-modules.md)) — and not `std`, the standard library's (07 M3, D1). Its `version` is
   a semantic version, `MAJOR.MINOR.PATCH` with optional pre-release and build parts. Its
   `edition` names the edition of the language the package is written in (07 V9): `"5"`, the one
   there is, and the default. A missing or malformed field is refused (`LYR-PKG0002`).
3. `[package]` may also hold `description`, `license` and `repository` — strings — and `authors`,
   an array of strings: they describe the package and change no build (`LYR-PKG0002` for another
   type).
4. A key or a section the toolchain does not know is refused (`LYR-PKG0003`), as an unknown option
   is ([14 §1.1](14-cli.md)). `[dependencies]`, `[override]`, `include` and `exclude` are §2's.
   The other parts of a manifest ([11 W2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)) — binaries, profiles, the native
   part, lints, the trust rule, the toolchain pin — are refused the same way until this chapter
   writes them.
5. A package's **program** is its `src/main.lyr`, and its binary is named after the package
   ([14 §1.2](14-cli.md)). Without `src/main.lyr`, the package is a library (P2).

## 2. Dependencies

The packages a package imports from ([11 W2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md), [07 V7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)).

**Conformance.** `conformance/cases/15-project/`, package cases that hold their dependencies in
their own directories, and the git repositories they read as their versions
([the suite's README](../conformance/README.md)); the toolchain's own tests
(`tests/Lyric5.Tests`: `DependencyTests`, `GitDependencyTests`, `PackageContentTests`).

1. `[dependencies]` names them, each where it is read from: a directory,
   `geo = { path = "../geo" }`, relative to the manifest — or a git repository,
   `http = { git = "https://…", tag = "v1.2.0" }`. The directory, or the root of the
   repository, holds a manifest that names the package (`LYR-PKG0004`). A version alone,
   `geo = "1.2"`, is a registry's form, and 5.0 has no registry (`LYR-PKG0003`) (07 P8).
2. A git dependency reads **one revision** of its repository
   ([11 P9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)): a `tag`, a `branch`, a commit — `rev`, its id or the first 7 to
   64 hexadecimal digits of it — or, naming none, the branch the repository's `HEAD` names. Its
   `git` is a URL — `https://`, `http://`, `ssh://`, `git://`, `file://` — or `user@host:path`
   (`LYR-PKG0002`, as for two revisions, or a revision beside a `path`). A revision the
   repository does not have, or a repository without a package at its root, is refused
   (`LYR-PKG0006`); a repository that cannot be reached is the environment's failure
   (`LYR-PKG0007`, exit 2, [14 §1.3](14-cli.md)).
3. What is read from git is kept in the **user's cache**, not in the project: each repository
   once, each revision's package once, for every project that reads it (P9; 07 P10). A tag or a
   commit the cache holds is not fetched again; a branch moves, and is fetched again by each
   build that may fetch. **`--offline`** fetches nothing: what the cache does not hold is refused
   (`LYR-PKG0007`).
4. A package read from git is its **package content** (11 P8): its manifest, `src/`,
   `native/`, `build.lyr`, and the files `README*` and `LICENSE*` at its root — not `tests/`,
   not `out/`. `[package] include = […]` names the files instead of that default — the
   manifest belongs always —, and `exclude = […]` takes files out. A pattern is relative to the
   package's root, `/` between directories; `*` stands for any characters within a directory,
   `?` for one, `**` for any number of directories, and a pattern that names a directory holds
   what lies below it (`LYR-PKG0002` for another form). A module outside the content is not
   there (`LYR-RES0003`). A package read from git names its own dependencies by git: a directory
   is no part of it (`LYR-PKG0004`).
5. A module imports from its own package, from `std`, and from the packages its package's
   manifest declares — not from what those depend on (`LYR-RES0014`) (07 P6).
6. A program holds **one package of each name** (07 P3): two sources for one name — two
   directories, two repositories, two revisions of one — are refused (`LYR-PKG0005`), unless the
   root manifest's `[override] units = { path = "…" }` picks the one — read wherever the graph
   asks for `units`, and what it replaces is not read at all, not fetched either (07 P7). An
   override reads a directory (`LYR-PKG0003` for the git form); an override in another
   package's manifest is not read.
7. A **library** — a package without `src/main.lyr` — builds as a check: every module of it
   through the compiler, nothing built ([07 B6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)); `lyric run` has no program there
   (`LYR-CLI0005`).

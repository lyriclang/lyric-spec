# Projects

> **Partly written.** §1–§6 were written with milestone **M7** of the Lyric 5 plan (slices S1, S4,
> S5a–S6e, S8a), §7 with **M8a**; the rest follows, spec-first: each rule lands here with its
> conformance case before or with its implementation. Source of the decisions:
> [11 Tooling and interop W2/W3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md), [07 Modules](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md).

## Scope

`lyric.toml`, profiles, targets, the lock file, `out/`, build scripts and their trust rule, reproducibility.

## 1. The manifest

A package's manifest, `lyric.toml` at its root, is read and never run
([11 P1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md), [07 V7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)).

**Conformance.** `conformance/cases/15-project/`, package cases; the TOML subset in the
toolchain's own tests (`tests/Lyric5.Tests`, `ManifestTests`), the programs and the toolchain pin
in `ProgramTests`.

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
   `[profile]` is §4's, `[native]` §5's. The other parts of a manifest
   ([11 W2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)) — lints, the trust rule — are refused the same way until this
   chapter writes them.
5. A package's **programs** are its `src/main.lyr`, whose binary is named after the package
   ([14 §1.2](14-cli.md)), and each `[[bin]]`: `name = "tool"` — a lowercase letter, then
   letters, digits, `_` and `-` —, its binary's, and `entry = "src/tool.lyr"`, a module of the
   package under `src/` (`LYR-PKG0002`, as for an entry that is no file and for two programs of
   one name; another key is `LYR-PKG0003`). Without any program, the package is a library (P2).
   A package's **root module** is its `src/lib.lyr` ([04 §2](04-modules.md) rule 1a), what
   `import geo { … }` names; it is no program, and a package may hold both.
   `lyric build` builds every program; `run` and `--emit` the one `--bin` names, else
   `src/main.lyr`'s, else the only one — of several, `--bin` names it (`LYR-CLI0007`).
6. **`toolchain = "5.1"`** — or `">=5.1"` — in `[package]` is the least toolchain that builds the
   package ([11 P12](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)): a toolchain below what any package of the program asks
   for refuses the program (`LYR-PKG0009`, exit 2, [14 §1.3](14-cli.md)), a development build of
   a version counting as that version. Another form is refused (`LYR-PKG0002`).

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
   (`LYR-PKG0002`, as for two revisions, or a revision beside a `path`). The URL is compared,
   cached and locked in its **normal form** (the review's M7-10): a `/` and a `.git` at the end
   dropped, the scheme and the host in lower case — `HTTPS://Example.com/org/geo.git/` and
   `https://example.com/org/geo` are one repository; the rest keeps its case, and `https://` and
   `ssh://` to one host stay two. A revision the repository does not have, or a repository
   without a package at its root, is refused (`LYR-PKG0006`), and so is a tag that is a version
   over a manifest that gives another — `v1.2.0` where the manifest says `version = "1.1.0"`:
   the build chooses among versions by the tag. A repository that cannot be reached is the
   environment's failure (`LYR-PKG0007`, exit 2, [14 §1.3](14-cli.md)).
3. What is read from git is kept in the **user's cache**, not in the project: each repository
   once, each revision's package once, for every project that reads it (P9; 07 P10). A tag or a
   commit the cache holds is not fetched again; a branch, or no revision, is read where the lock
   holds it (§3), and at its head — fetched — where the lock holds nothing for it yet.
   **`--offline`** fetches nothing: what the cache does not hold is refused (`LYR-PKG0007`).
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
6. A program holds **one package of each name** (07 P3). **Versions of one repository** are one
   package: a tag that is a semantic version, `v1.2.0` or `1.2.0`, asks for that version or a
   later one of its **line** — the same major version; below 1, the same minor; below 0.1, the
   version alone (07 P2) —, and of all the versions the graph asks for, directly or through a
   version read on the way, the build takes the greatest: the least that satisfies them all
   (**minimal version selection**, [07 P4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)). Any other two sources for one name —
   two directories, two repositories, two revisions of one, versions of two lines — are refused
   (`LYR-PKG0005`), unless the root manifest's `[override] units = { path = "…" }` picks the one — read wherever the graph
   asks for `units`, and what it replaces is not read at all, not fetched either (07 P7). An
   override reads a directory (`LYR-PKG0003` for the git form); an override in another
   package's manifest is not read. No package depends on itself, at once or through others: a
   **cycle** is refused with its path, `app -> geo -> app` (`LYR-PKG0010`; the review's M7-6) — a
   package's dependencies are built before it, and a cycle has no first one.
7. A **library** — a package without `src/main.lyr` — builds as a check: every module of it
   through the compiler, nothing built ([07 B6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)); `lyric run` has no program there
   (`LYR-CLI0005`).

## 3. The lock file

What a build read from git, kept so that the next build reads the same
([07 P5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)): minimal version selection makes the choice, the lock makes the content
reproducible.

**Conformance.** `conformance/cases/15-project/`, package cases that hold their `lyric.lock`;
the toolchain's own tests (`tests/Lyric5.Tests`, `LockTests`).

1. **`lyric.lock`**, beside the root manifest, holds every revision of a git repository the
   graph read — the versions chosen and the ones read on the way —, each with its package's name
   and version, its repository and revision, the **commit** it was, and the **hash** of its
   package content (§2): SHA-256 over one line per file — the file's SHA-256 in hexadecimal, two
   spaces, its path with `/` between directories —, the lines sorted by path; written `h1:` and
   base64. The toolchain writes the lock — only when what it holds changes, and none for a
   program that reads nothing from git —, and it is checked in with the manifest. A
   dependency's lock is not read.
2. A build reads a revision the lock holds **at the commit the lock holds**: a branch stays where
   it was locked, and a tag moved in the repository too. Content that is not what the lock holds
   is refused, as is a locked commit the repository does not have (`LYR-PKG0008`). What the lock
   does not hold yet is resolved and added; what the graph no longer reads is dropped. A lock that
   is not one is refused (`LYR-PKG0001`, `LYR-PKG0002`).
3. **`lyric update [<package>…]`** reads every package from git anew — or those it names, the
   others staying at their commits —, fetching their repositories first, and writes the lock: a
   branch moves to its head, a moved tag to its commit. A tag of the root manifest that is a
   version is first **raised to the newest tag of its line** the repository has (the review's
   M7-8) — never another major version; below 1, never another minor; a pre-release only for a
   pre-release — and written on its line of `lyric.toml`, the rest of the file as it was; a
   dependency's own manifest is its own, and a branch, a commit or a tag that is no version stays.
   A name that no package read from git has is refused (`LYR-CLI0003`).
4. Under **`--locked`** (the review's M7-9), `build`, `run` and `test` take the lock **as it
   is** and write nothing: a revision the graph reads that the lock does not hold is refused
   before anything is fetched, and so is a lock that holds what the graph does not read, or no
   lock where the program reads from git (`LYR-PKG0011`, exit 1). A program that reads nothing
   from git needs none. Without the flag a build writes the lock on (rule 1).

## 4. Profiles

How a program is built — the compiler's settings, not the program
([11 P3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).

**Conformance.** `conformance/cases/15-project/`, package cases whose manifest changes the
built-in profiles the suite builds with; the toolchain's own tests (`tests/Lyric5.Tests`,
`ProfileTests`, `LtoTests`).

1. **`debug`, `release`, `asan` and `tsan`** are built in. `[profile.<name>]` changes a built-in
   profile, or names one of the manifest's own — a lowercase letter, then letters, digits, `_`
   and `-` —, which **inherits** from another, `inherits = "release"`, the chain ending in a
   built-in one. A built-in profile inherits from nothing, a manifest's own profile always does,
   and none inherits from itself (`LYR-PKG0002`). Only the root manifest's profiles count: the
   program is built one way. `out/<profile>/` is named after the profile
   ([14 §1.2](14-cli.md)).
2. A profile sets **fields**: `opt`, the C optimization level from 0 to 3, and `debugInfo`,
   `lto`, `denyWarnings`, `overflowChecks`, `fastMath`, each `true` or `false` (`LYR-PKG0002` for
   another type, `LYR-PKG0003` for another key). A field a profile does not set is the one it
   inherits — as the manifest has that profile. The built-in ones: `debug` `opt = 0`, `release`
   `opt = 2`, the sanitizers' `opt = 1`; all four with `debugInfo` and `overflowChecks`, none with
   `lto`, `denyWarnings` or `fastMath`.
3. **`overflowChecks = false`** makes integer overflow wrap instead of panicking, for the whole
   program ([03 §1.6](03-types.md)). Nothing is without the checks unless a profile says so.
4. **`denyWarnings = true`** fails a compilation that warns: the warnings stay warnings, and an
   error says why the build failed (`LYR-CLI0006`).
5. **`fastMath = true`** lets the C compiler treat the program's floating point as not
   IEEE-exact ([03 §1.6](03-types.md)); the runtime's stays exact.
6. **`lto = true`** lets the C compiler optimize across the program, the native parts
   ([§5](#5-the-native-part)) and the runtime as they are linked — ThinLTO. A target whose linker
   takes none — macOS, with the toolchain's C compiler — is built without it, not refused. What a
   program does is the same either way.

## 5. The native part

C a package brings with it, compiled with the program and linked into it
([07 B5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md); [11 W2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).

**Conformance.** `conformance/cases/13-abi/`, package cases that call their native part; the
toolchain's own tests (`tests/Lyric5.Tests`, `NativeTests`).

1. `[native]` names `sources`, patterns of the package's files as §2's `include` has them — the C
   sources compiled with the program under its profile —, `include`, directories of the package
   the sources find their includes in, and `libs`, libraries linked by name (`-lz`). Another key
   is refused (`LYR-PKG0003`), as is another form of an entry (`LYR-PKG0002`).
2. `[native.linux]`, `[native.windows]` and `[native.macos]` take the same keys: what a build for
   that operating system gets on top of `[native]`.
3. Every package of the program brings its native part — a dependency's too —, and each library is
   linked once. The C functions of a native part are called through `extern "C"`
   ([13 §2](13-abi.md)).

## 6. Reproducibility

([11 P6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `ReproducibilityTests`): one
package built in two directories a second apart — for the host in both built-in profiles, and for
each operating system from any host — compared byte for byte.

1. The same sources, options, toolchain and C compiler give the **same bytes** — wherever the
   package lies, wherever the build runs from, and whenever it is built. A binary carries no time
   stamp, and no path of the machine that built it: a path the build would write into it — a
   source's, the emitted C's, the runtime's — is written as the name of the package it lies in, or
   `lyric` for the toolchain's own, and the directory the C compiler works in as `.`. A library
   the C compiler brings of its own — zig's `libunwind` on Linux — comes as the C compiler built
   it.
2. Debug information that names the machine's paths lies **beside** the binary, not in it: a
   Windows binary's PDB, a macOS binary's `.dSYM` — gathered on a macOS host, where `dsymutil` is.
   The binary names it by a hash of its own bytes — a PE image's PDB GUID, a Mach-O image's UUID —,
   so the two still pair.

## 7. Tests

([07 V4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `TestCommandTests`).

1. A package's **`tests/`**, beside `src/`, holds modules of the package: `tests/math.lyr` in
   `app` is `app.tests.math`. A test there sees what the package does not make `private`; a test
   beside the code, in the module it tests, sees that module's `private` too. A module that would
   lie both under `src/tests/` and under `tests/` is refused (`LYR-RES0015`).
2. Only `lyric test` compiles `tests/` ([14 §3](14-cli.md)): no program's build reaches it, and a
   package's content (§2) leaves it out.

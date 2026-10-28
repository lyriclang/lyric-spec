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
   `[profile]` is §4's, `[native]` §5's, `[build-dependencies]` and `[trust]` §8's. `[lints]`
   holds `allow`, `warn` and `deny`, each an array of lints, groups or `warnings` — the levels of the
   package's lints in its files ([16 §5](16-diagnostics.md#5-lints)): `[lints] deny = ["unused"]`; a
   selector that names nothing, or stands in two of them, is refused (`LYR-PKG0002`), another key
   (`LYR-PKG0003`).
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
   a version counting as that version. Another form is refused (`LYR-PKG0002`). The root package's
   pin also chooses the toolchain: a command in the package is handed to an installed toolchain
   that meets it, where the one started does not ([14 §13](14-cli.md) rule 11).
7. **`comptimeBudget = 100_000_000`** in `[package]` is the steps one `comptime` site may take
   ([11 §2](11-metaprogramming.md) rule 5), for the whole program but the standard library where
   it stands in the root manifest; a dependency's changes no build. A number that is not positive, or another value,
   is refused (`LYR-PKG0002`).

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
   base64 — and the source trees from git a build read (§5 rule 15). The toolchain writes the
   lock — only when what it holds changes, and none for a program that reads nothing from git —,
   and it is checked in with the manifest. A dependency's lock is not read.
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
2. A profile sets **fields**: `opt`, the C optimization level from 0 to 3; `debugInfo`, `lto`,
   `denyWarnings`, `overflowChecks`, `fastMath`, each `true` or `false`; and `gc`, `"immix"` or
   `"boehm"` (`LYR-PKG0002` for another type or value, `LYR-PKG0003` for another key). A field a
   profile does not set is the one it inherits — as the manifest has that profile. The built-in
   ones: `debug` `opt = 0`, `release` `opt = 2`, the sanitizers' `opt = 1`; all four with
   `debugInfo` and `overflowChecks`, none with `lto`, `denyWarnings` or `fastMath`, all with
   `gc = "immix"`.
3. **`overflowChecks = false`** makes integer overflow wrap instead of panicking, for the whole
   program ([03 §1.6](03-types.md)). Nothing is without the checks unless a profile says so.
4. **`denyWarnings = true`** fails a compilation that warns: it is `-D warnings`
   ([16 §5](16-diagnostics.md#5-lints) rule 8) — each warning is an error, its note naming the profile.
5. **`fastMath = true`** lets the C compiler treat the program's floating point as not
   IEEE-exact ([03 §1.6](03-types.md)); the runtime's stays exact.
6. **`lto = true`** lets the C compiler optimize across the program, the native parts
   ([§5](#5-the-native-part)) and the runtime as they are linked — ThinLTO. A target whose linker
   takes none — macOS, with the toolchain's C compiler — is built without it, not refused. What a
   program does is the same either way.
7. **`gc`** chooses the runtime's collector
   ([01 L1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)):
   `"immix"`, its own, or `"boehm"`, the Boehm–Demers–Weiser collector it began with, kept to
   compare against. What a program does is the same under either; what it costs in time and
   memory is not.

## 5. The native part

C a package brings with it, compiled with the program and linked into it
([07 B5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md); [11 W2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).

**Conformance.** `conformance/cases/13-abi/` and `conformance/cases/15-project/`, package cases
that call their native part or whose manifest a rule refuses; the toolchain's own tests
(`tests/Lyric5.Tests`, `NativeTests`, `VendorTests`, `BindingsTests`).

*(Rules 9–11 and the findings `LYR-LNK…` of rule 12 are written ahead of their implementation, milestone M14b of the Lyric 5 plan — the
decisions of [11, review 2026-10-28](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md);
each comes with its cases.)*

### 5.1 Sources

1. `[native]` names `sources`, patterns of the package's files as §2's `include` has them — the C
   sources compiled with the program under its profile —, `include`, directories of the package
   the sources find their includes in, and `libs`, libraries linked by name (`-lz`). Another key
   than this section's is refused (`LYR-PKG0003`), as is another form of an entry (`LYR-PKG0002`).
2. `[native.linux]`, `[native.windows]` and `[native.macos]` take the same keys: what a build for
   that operating system gets on top of `[native]`.
3. Every package of the program brings its native part — a dependency's too —, and each library is
   linked once. The C functions of a native part are called through `extern "C"`
   ([13 §2](13-abi.md)).
4. **`[native.<triple>]`** — a Tier 1 or Tier 2 target's triple, `[native.x86_64-windows-gnu]` —
   takes the same keys, and what a build for that target gets comes on top of `[native]` and of its
   operating system's table: the three tables are **layered**, each list the one before with its
   own entries after. A triple no tier holds is refused (`LYR-PKG0003`).
5. **`defines = ["RAYLIB_STATIC", "LEVEL=2"]`** are the package's sources' preprocessor
   definitions, `NAME` or `NAME=value`, `NAME` a C identifier (`LYR-PKG0002`). The manifest takes no
   other flag for the C compiler: one that names the machine or a path outside the package would
   break §6 and the builds for other targets.
6. A native source finds, besides its package's `include`, the toolchain's **`<lyric.h>`**
   ([13 §4](13-abi.md#4-exports-and-libraries)) and the `include` of each package its package
   declares as a dependency — not of the packages those depend on (§2 rule 5). Of the toolchain's
   headers only `lyric.h` is promised.

### 5.2 Linking

7. **`archives = ["native/lib/libz.a"]`** are static libraries the package brings, prebuilt — files
   of the package's content (§2) or of a source tree (§5.3): each is linked **by its path**, not
   searched for. A file outside the content, or one that is not there, is refused when the build
   needs it (`LYR-PKG0002`). An archive is built for one
   target, so it stands in the table of its triple (rule 4) as a rule. On Windows an archive is
   promised to link where it was built for the GNU ABI — by MinGW or zig cc —, not by MSVC.
8. **`dylibs`** are shared libraries the package brings, prebuilt — files of the package's content
   or of a source tree, linked **by their path**. A shared library is built for one target, so
   `dylibs` is a key of the operating systems' and the triples' tables only (`LYR-PKG0003` in
   `[native]`): on Linux and macOS each entry is the path of a `.so` or a `.dylib`
   (`"native/linux/libfoo.so"`); on Windows `{ dll = "native/win/foo.dll", lib =
   "native/win/libfoo.dll.a" }`, the DLL and its import library, for the GNU ABI as rule 7 has it.
   Another form, a file outside the content, or a shared library named in `archives` is refused
   (`LYR-PKG0002`). The build puts each beside every binary it makes of the program, as §8 rule 3.2
   puts a file there, and with the same rules: the binary searches its own directory first, no
   directory of the machine is written into it, and two files of one name stop the build. A
   Mach-O library whose install name does not begin with `@rpath/` would not be found there, and an
   ELF library without a `soname` would be recorded by the path it was linked from — the
   machine's; each is refused (`LYR-BLD0006`, exit 1), the message saying how to name it. A shared library of
   the system is linked by name (`libs`); one the program finds while it runs is `std.ffi`'s
   `Library` ([13 §5](13-abi.md)). *(Rule 8 replaces, the same day, a rule that refused every
   shared library of a package — [07, E3′](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md).)*
9. **`frameworks = ["Cocoa"]`** are macOS frameworks, linked as `-framework Cocoa`: a key of
   `[native.macos]` and of the macOS triples' tables only (`LYR-PKG0003` elsewhere).
10. **`pkgConfig = ["sdl2"]`** names libraries of the system as `pkg-config` knows them: a build for
    the host asks `pkg-config --cflags --libs` and gives what it says about include directories and
    definitions to the package's sources, and the rest to the link. `pkg-config` missing, or a
    name it does not know, stops the build (`LYR-BLD0004`, exit 2).
11. **What only the host has**: a framework comes from the macOS SDK and a name of `pkgConfig` from
    the host's system, so a build for another target that needs one is refused before it compiles
    (`LYR-BLD0004`, exit 2, naming the package and the key). *(Informative: with the toolchain's C
    compiler a build for Windows links Windows' system libraries from any host; a build for Linux
    links a library of the system beside libc only on a Linux host, and one for macOS a framework
    only on a macOS host.)*
12. The link takes, in this order: the program's objects and the native parts' — the packages
    **before the packages they depend on**, the root's first —, their `archives` and `dylibs` in that order, the
    libraries by name and from `pkgConfig`, then the frameworks; each archive, library and framework
    once, where it first stands. A symbol two packages define fails the link (`LYR-LNK0003`), and
    so does one nothing defines (`LYR-LNK0001`) or a library the linker does not find
    (`LYR-LNK0002`) — each exit 2, as the link is ([14 §1.3](14-cli.md)). A binary is linked anew
    where an archive's or a shared library's bytes changed, not only its time.

### 5.3 Source trees

13. **`[native.vendor]`** names **source trees**: C that the package does not hold and that is no
    package — no manifest, no modules. `raylib = { git = "https://…", tag = "5.5" }` is a revision
    of a repository, read as §2 rule 2 reads one (`branch`, `rev`, or none), cached and locked as
    §2 rule 3 and §3 have it, its content every file of the commit; `sqlite = { url =
    "https://…/sqlite.zip", hash = "sha256:…" }` is a file loaded from `https://`, `http://` or
    `file://` — its `hash` is its SHA-256, 64 hexadecimal digits, and makes the way it came
    irrelevant —, a tar compressed with gzip or a zip, told by its bytes, not its name, and
    unpacked with a single top directory left out. A name is a lowercase letter, then letters,
    digits, `_` and `-`; another key or form is refused (`LYR-PKG0002`). *(A tar compressed with xz
    is no tree in 5.0; such a tree comes from git.)*
14. A path of the native part — in `sources`, `include`, `archives`, `dylibs` and `bindings` — that
    begins with **`@name/`** lies in the tree `name`; a name `[native.vendor]` does not hold is
    refused (`LYR-PKG0002`). A tree's file is no part of the package's content (§2 rule 4) and is
    not refused for it; one that is not there is refused when the build needs it (`LYR-PKG0002`).
    A tree is the package's own: another package's `@name` is another tree, and two packages that
    compile one tree define its symbols twice (rule 12).
15. A tree is read **only where a build needs it**: where a table that holds for the build's target
    names it. `lyric check` reads only those its bindings need (§5.4); `lyric metadata` and the
    editor read none. What a build reads is
    fetched into the user's cache — a URL's file once by its hash, unpacked once —, under
    `--offline` not at all (`LYR-PKG0007`). A URL without `hash` is refused, the message giving the
    hash of what it loaded (`LYR-PKG0002`); a file whose hash is another is refused, the message
    giving both (`LYR-PKG0008`), as is a revision whose content is not what the lock holds; a
    revision the repository does not have (`LYR-PKG0006`); a repository or a URL that cannot be
    reached is the environment's (`LYR-PKG0007`, exit 2).

    The lock (§3) holds a **git tree** a build read as it holds a package read from git — its
    repository, revision, commit and the hash of its content —, written `kind = "native"`, with
    `of`, the name of the package whose tree it is, and no `version`; a URL's tree is held by its
    `hash` in the manifest, not in the lock. A build adds the trees it resolved; reading the graph
    keeps the trees a manifest of the graph still names so and drops the rest — a tree no build
    has needed is not held. Under `--locked` a build that needs a tree the lock does not hold is
    refused (`LYR-PKG0011`), as §3 rule 4 refuses a revision. **`lyric update`** reads the trees
    the lock holds anew — those it names, or every one —, a branch at its head and a moved tag at
    its commit; a tree's tag is not raised, as a tree has no version.
16. A tree runs nothing: it is compiled, as the package's sources are, and no trust is asked for it
    (§8 rule 6). What an archive does, its bytes say; the lock holds them.
16. A tree runs nothing: it is compiled, as the package's sources are, and no trust is asked for it
    (§8 rule 6). What an archive does, its bytes say; the lock holds them.

### 5.4 Bindings

17. **`bindings = [{ header = "@raylib/src/raylib.h", module = "rl" }]`** makes a **module of the
    package from a C header**: `rl` in `game` is the module `game.rl`, a path of segments as §2's
    modules have, each a lowercase letter, then letters, digits and `_` (`LYR-PKG0002`). Its
    declarations are `pub`, its names C's. A module of that path under `src/`, `gen/` or `tests/`
    is refused (`LYR-RES0016`). The packages that declare the package as a dependency import it as
    any of its modules. `bindings` is a key of every table of rule 4, layered as the others.
18. The module is made **for the build's target**, from what the C compiler reads of the header
    with the package's `include` and `defines` — C's types differ between targets. It holds the
    declarations of the header and of the headers beside and below it, in the order they come, not
    the system's:
    - a function as `extern "C" fn` ([13 §2](13-abi.md)), with `...` where it is variadic;
    - a struct as a `@Layout(C)` struct of the same fields ([13 §3](13-abi.md) rule 4); a struct
      C declares without its fields as `Ptr<void>` where a pointer names it;
    - an enum's constants as module-level constants of its integer type, and the enum's name as an
      alias of that type;
    - a `typedef` as an alias ([03 §10](03-types.md)), a pointer to a C function as its type
      `extern "C" fn(…) -> R`;
    - a `#define` whose body is one integer literal, or one string literal, as a constant.

    The C types as [13 §2–§3](13-abi.md) cross them: the integers by their width on the target —
    `char` as the target's `int8` or `uint8`, `size_t` as `uint`, `ptrdiff_t` as `int` —, `float`
    and `double`, `bool`; `const char *` as `?CStr`; any other `T *` as `?Ptr<T>`, `void *` as
    `?Ptr<void>`; an array parameter as the pointer it is. In a **field**, where 13 §3 rule 4 takes
    no optional, a pointer is `Ptr<T>`, `CStr` or the function pointer's type — a null there is the
    program's to look for —, and an array of arrays is one array of all their elements,
    `float m[4][4]` as `float32[16]`, laid out alike. A constant is a `pub let`: an enum's of its
    integer type; a `#define`'s integer of the type C gives the literal — the first of `int32` and
    `int` it fits, unsigned with a `u` suffix or where a hexadecimal or octal one needs it, `int`
    or `uint` with an `l` —, so that it goes where C's `int` goes; its string as `string`. A name
    that is a word of Lyric or a builtin type's name gets a `_` after it: `string` as `string_`.
19. What it cannot write — a union, a bit field, a struct with one, a function-like macro, a
    `static inline` function, a variable, a declaration that needs one of them — is **left out**,
    and the module's last lines list each by its name, its file and line, and why; a `#define`
    with an empty body — an include guard — is passed over. No lint looks at the module
    ([16 §5](16-diagnostics.md#5-lints)): it is written by the toolchain, as a dependency's
    modules are written by others.
20. A header that does not compile, or a module the toolchain cannot write — a C compiler that
    writes no syntax tree, which only zig cc and clang do —, stops the build (`LYR-BLD0005`, exit 1)
    with what the C compiler said. The module is made anew where the
    header, a header it reads, the `defines`, the target or the toolchain changed.
21. **`lyric bindgen`** writes the module one entry makes to standard output, to keep it under
    `src/` instead ([14 §2](14-cli.md) rule 6).

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
3. A package's **archives**, **shared libraries** and **source trees** (§5.2, §5.3) are inputs as
   its sources are: the lock holds their bytes, and an archive comes into the binary as it was
   built — what it carries of the machine that built it is its own. A library linked by name,
   through `pkgConfig` or from a directory a build script names (§8 rule 3.1) is the machine's:
   the same bytes need the same system libraries.

## 7. Tests

([07 V4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md))

**Conformance.** The toolchain's own tests (`tests/Lyric5.Tests`, `TestCommandTests`).

1. A package's **`tests/`**, beside `src/`, holds modules of the package: `tests/math.lyr` in
   `app` is `app.tests.math`. A test there sees what the package does not make `private`; a test
   beside the code, in the module it tests, sees that module's `private` too. A module that would
   lie both under `src/tests/` and under `tests/` is refused (`LYR-RES0015`).
2. Only `lyric test` compiles `tests/` ([14 §3](14-cli.md)): no program's build reaches it, and a
   package's content (§2) leaves it out.

## 8. The build script

([11 W3 BS1–BS6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md); M8b S13.)

1. A package's **`build.lyr`**, at its root, is a program that runs before the package compiles.
   It does things — writes modules into `gen/`, names C to compile, libraries to link and where
   to find them, and files to put beside the program — and defines nothing: what the package is,
   the manifest says (§1).
2. It is **a program of its own**: its module is `build`, a file `build/x.lyr` beside it the
   module `build.x`, and it imports from `std` and from the packages of the manifest's
   **`[build-dependencies]`**, a graph of its own (§2), read at the commits the same lock holds and
   held in it beside the program's (§3). Nothing of it is compiled into the package, and the
   package's program sees none of its dependencies; `build` names no package of that graph. It runs
   on the host, with the package's root as its working directory, whatever the build's target.
3. **`std.build`** is its view of the build: `target()` and `profile()`, the build's; `outDir()`,
   the package's `out/`; `genDir()`; `rerunIfChanged(paths…)`, `rerunIfEnvChanged(names…)`,
   `linkLib(name)`, `linkSearch(dir)`, `cFlags(flags…)`, `compileC(sources…)`,
   `besideBinary(paths…)` — paths from the package's root, or absolute —, and `warn(message)`,
   which the build shows (`LYR-BLD0003`). Outside a build script they panic.
   1. **`linkSearch(dir)`** names a directory the link searches for the libraries of `linkLib`
      and of `[native]`'s `libs` (§5), before the linker's own and in the order named — the
      scripts of dependencies by their names, the root's last. For a Windows target a library `X`
      is found as `X.dll`, `X.lib`, `libX.a`, or as the import library `libX.dll.a` or `X.dll.a` a
      MinGW toolchain makes. **No directory the link searched is written into the binary**: a
      shared library is found when the program starts where the system looks, or beside it (rule
      3.2). A directory that is not there is no error: the link that does not find a library says
      where it searched.
   2. **`besideBinary(paths…)`** names files the program needs beside it when it runs — a shared
      library above all. After each link the build copies them, under their own names, into the
      directory of every binary it makes of the program — of `build` and `run`, of `test` and
      `bench` ([14 §3](14-cli.md)), of a library `--lib` makes, not of a build script —, and such
      a binary searches its own directory for shared libraries first: an ELF binary by the run path
      `$ORIGIN`, a Mach-O binary by `@executable_path`; a Windows binary does so by itself. A file
      that is not there when the script has ended, and two files of one name — counting the
      `dylibs` of §5 rule 8 —, stop the build (`LYR-BLD0006`, exit 1).
   *(Written ahead of M14b, replacing `cFlags` and `compileC` when it lands:)* `target()` is a
   **`Target`** — its `triple`, its `os` (`Os.linux`, `Os.windows`, `Os.macos`), its `arch`
   (`Arch.x86_64`, `Arch.aarch64`) and whether it `isHost` —; `vendorDir(name)` is the directory of
   a source tree (§5.3), read where the script asks for it; **`cLibrary(name)`** is a C library the
   script compiles with the program — its `sources(…)`, `include(…)`, `define(name)` and
   `define(name, value)`, and `flags(…)`, the C compiler's own, its alone — and `compile()` adds it:
   its sources see the package's `include`, `<lyric.h>` and the headers §5 rule 6 names; paths are
   the package's or a tree's (`@name/…`). `linkLib(name)`, `linkArchive(path)`,
   `linkFramework(name)` and `pkgConfig(name)` are §5.2's keys, with their rules; `cEnv()` is the
   environment — `CC`, `AR`, `CFLAGS` — under which another build system compiles C for the target
   with the toolchain's C compiler.
4. **`gen/`**, which the toolchain makes before the script runs, is a module space of the
   package: `gen/schema.lyr` in `app` is `app.gen.schema`, as `tests/` is §7's. It is no part of
   the package's content (§2).
5. **When it runs**: before the compile, where the script changed — `build.lyr`, `build/`, its
   dependencies, the toolchain, the target, the profile —, where a file it named with
   `rerunIfChanged` changed, where an environment variable it named with `rerunIfEnvChanged` has
   another value than in its last run — set where it was not, or not where it was —, or where
   `gen/` is not as it left it; else what its last run asked stands. What the script's state holds
   of a variable is a hash of its value, not the value. A script that does not
   compile, that ends with an exit other than 0, or that does not end within 10 minutes, stops the
   build (`LYR-BLD0002`), with what it wrote — exit 1, as a program refused ([14 §1.3](14-cli.md)):
   the package's code failed, not the environment.
6. **Trust**: the root package's script always runs; a dependency's only where the root
   manifest's **`[trust] build-scripts = ["geo"]`** names the package. Else the build stops before
   anything runs (`LYR-PKG0012`), at the line that declares the dependency.

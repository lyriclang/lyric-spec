# 15. Project

**Base.** Lyric 5.0 [§15](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/15-project.md) applies, with the deviations below.

**Status.** The manifest, path and git dependencies, the lock, version lines, `[override]` and a
script's frontmatter written (S5b–S5d); `[lints]` comes with S11 — until then the design
documents decide.

## Written (S5b, the manifest and path dependencies)

1. **The manifest** ([07 Man](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); Lyric 5 §1 rules 1–4). A package's manifest is
   `lyric-script.toml` at its root, read and never run: TOML, the part a manifest needs — a
   syntax error, a key or table written twice, a float, a date or a time is refused at its line
   (`LYS-PKG0001`). `[package]` is required, with its `name` — a lowercase letter, then lowercase
   letters, digits and `_`, not `std` —, a semantic `version` and the `edition`, `"1"` and the
   default; `description`, `license` and `repository` are strings, `authors` an array of strings
   (`LYS-PKG0002`). A key or section the manifest does not take is refused (`LYS-PKG0003`).
   `[override]`, `include`, `exclude` and a git dependency come with S5c, `[lints]` with S11
   (`LYS-NYI0001` until then).
2. **The package of a program** ([07 Path](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); Lyric 5 04 §2 rules 1, 1a, 3). A program is a
   package's where the nearest `lyric-script.toml` above its entry has the entry under its
   `src/`; `lyric-script run` and `check` without a file, in a package's folder, take its
   `src/main.lyrs` ([14](14-cli.md); `LYS-CLI0005` where there is none). There Lyric 5's path rule
   holds instead of [04](04-modules.md) rule 1's: `app.a.b` is the file `src/a/b.lyrs` of the
   package `app`, and `app` alone its `src/lib.lyrs`, the package's root module — there is no
   module `app.lib` (`LYS-RES0003`). The package's own modules write their paths the same way.
3. **Path dependencies** (Lyric 5 §2 rules 1, 5, 6). `[dependencies]` names them, each
   `geo = { path = "../geo" }`, the folder relative to the manifest; it holds a manifest that
   names the package so (`LYS-PKG0004`). A version alone, `geo = "1.2"`, is a registry's form,
   and Lyric-Script 1.0 has no registry (`LYS-PKG0003`). A module imports from its own package
   and from those its package's manifest declares, not from what those depend on
   (`LYS-RES0014`). A program holds one package of each name (`LYS-PKG0005`), each read once.
4. **`internal`** ([07 V2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)) keeps a declaration or a member to its package
   (`LYS-RES0009`); without a manifest every module is of one package, and `internal` is public.
5. **`toolchain = "1.1"`** — or `">=1.1"` — in `[package]` is the least toolchain that builds the
   package (Lyric 5 §1 rule 6): a toolchain below what any package of the program asks for
   refuses the program with exit code 2, a fault of the environment (`LYS-PKG0009`); a
   development build counts as its version.

## Written (S5c1, git dependencies)

6. **A git dependency** (Lyric 5 §2 rules 2, 4) reads one revision of its repository:
   `geo = { git = "https://…", tag = "v1.0.0" }`, a `branch`, a commit — `rev`, its id or the
   first 7 to 64 hexadecimal digits of it —, or, naming none, the branch the repository's `HEAD`
   names. Its `git` is a URL — `https://`, `http://`, `ssh://`, `git://`, `file://` — or
   `user@host:path` (`LYS-PKG0002`, as for two revisions, or a revision beside a `path`). The URL
   is compared, cached and read in its **normal form**: a `/` and a `.git` at its end dropped, the
   scheme and the host in lower case. A revision the repository does not have, a repository
   without the package at its root, and a tag that is a version over a manifest of another
   version are refused (`LYS-PKG0006`); a repository that cannot be reached is a fault of the
   environment (`LYS-PKG0007`, exit 2). A package read from git names its own dependencies by
   git (`LYS-PKG0004`).
7. **The user's cache** (Lyric 5 §2 rule 3; [14](14-cli.md)) keeps what is read from git, beside
   the bytecode: each repository once, each commit's tree once, for every project. A tag or a
   commit the cache holds is not fetched again; a branch, or no revision, is read at its head,
   fetched. **`--offline`** (`run`, `check`) fetches nothing: what the cache does not hold is
   refused (`LYS-PKG0007`, exit 2).

## Written (S5c2, the lock)

8. **`lyric-script.lock`** (Lyric 5 §3 rules 1–2), beside the root manifest, holds every revision
   of a git repository the program read, each with its package's name and version, its
   repository in its normal form, the revision as the manifest asks for it — `tag v1.0.0`,
   `branch main`, `rev 0123abc`, `HEAD` —, the **commit** it was, and the **hash** of its
   package content: its manifest, the files under `src/`, and `README*` and `LICENSE*` at its
   root; SHA-256 over one line per file — the file's SHA-256 in hexadecimal, two spaces, its path
   with `/` between folders —, the lines sorted by path, written `h1:` and Base64. The toolchain
   writes it, in one order, only when what it holds changes, and none for a program that reads
   nothing from git; it is checked in with the manifest, and a dependency's lock is not read. A
   revision the lock holds is read **at its commit** — a branch stays where it was locked —, and
   content that is not what the lock holds, or a locked commit the repository does not have, is
   refused (`LYS-PKG0008`). What the lock does not hold yet is resolved and added; what the
   program no longer reads is dropped. A lock that is not one is refused (`LYS-PKG0001`).
9. **`lyric-script update [package…]`** (§3 rule 3), in a package's folder, reads every package
   from git anew — or those it names, the others staying at their commits —, fetching first, and
   writes the lock: a branch moves to its head; it runs nothing (`LYS-CLI0006` for a name no
   package read from git has). Under **`--locked`** (§3 rule 4) `run` and `check` take the lock
   as it is and write nothing: a revision the lock does not hold is refused before anything is
   fetched, and so is a lock that holds what the program no longer reads, or none where the
   program reads from git (`LYS-PKG0011`).

## Written (S5c3, versions, overrides, content)

10. **One package of each name** (Lyric 5 §2 rule 6). Versions of one repository are one
    package: a tag that is a semantic version, `v1.2.0` or `1.2.0`, asks for that version or a
    later one of its **line** — the same major version; below 1, the same minor; below 0.1, the
    version alone —, and of all the versions the program asks for, directly or through a version
    read on the way, the toolchain takes the greatest: **minimal version selection**. The lock
    holds the versions chosen and those read on the way. Any other two sources for one name — two
    folders, two repositories, two revisions of one, versions of two lines — are refused
    (`LYS-PKG0005`), unless the root manifest's **`[override] geo = { path = "…" }`** picks one:
    read wherever the program asks for `geo`, and what it replaces is neither read nor fetched;
    an override reads a folder (`LYS-PKG0003` for the git form), and one in another package's
    manifest is not read. No package depends on itself, at once or through others: a cycle is
    refused with its path, `app -> geo -> app` (`LYS-PKG0010`).
11. **A package's content** (Lyric 5 §2 rule 4), what is read and hashed of a package from git:
    its manifest, its files under `src/`, and `README*` and `LICENSE*` at its root.
    `[package] include = […]` names the files instead — the manifest always in —, and
    `exclude = […]` takes files out: a pattern is relative to the package's root, `/` between
    folders, `*` any characters within a folder, `?` one, `**` any number of folders, and a pattern
    that names a folder holds what lies below it (`LYS-PKG0002` for another form). A module outside
    the content is not there (`LYS-RES0003`).
12. **`update` raises a version** (Lyric 5 §3 rule 3): a tag of the root manifest that is a version
    is first raised to the newest tag of its line the repository has — never another major
    version; below 1, never another minor; a pre-release only for a pre-release — and written on
    its line of `lyric-script.toml`, the rest of the file as it was; a branch, a commit, or a tag
    that is no version stays.

## Written (S5d, a script's frontmatter)

13. **A single script's dependencies** ([07 Dep](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md), [09 Hd](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)) stand in its
    **frontmatter**, the TOML between two `---` lines at its start ([01](01-lexical.md)): the
    manifest's subset a script takes — `[dependencies]`, `[override]`, and `toolchain` in
    `[package]`; it names no package (`LYS-PKG0003` for another key), and its dependencies take
    the manifest's forms, a folder relative to the script. The script's own modules keep the path
    rule ([04](04-modules.md) rule 1); an import whose first segment is a dependency's name reaches
    that package. What the frontmatter reads is resolved at the first run and kept as a lock in
    the user's cache under the frontmatter's hash, so that a later run reads the same; **`lyric-script
    lock tool.lyrs`** writes it beside the script, `tool.lyrs.lock`, and a lock there is read
    first. The frontmatter holds no rights ([01 S4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).

## Deviations

- `lyric-script.toml` and `lyric-script.lock`; dependencies in a script's frontmatter; `pack` ([07 Dep, Man](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md), [12 Pk](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).

**Conformance.** `conformance/cases/15-project/` (`since: 1.0.0`), package cases: a folder with
its manifest, its program in `src/main.lyrs` and its dependencies in `deps/`
([the format](../conformance/README.md)); the manifest's fields one by one in the toolchain's
own tests (`tests/package.lyr`).

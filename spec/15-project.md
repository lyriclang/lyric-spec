# 15. Project

**Base.** Lyric 5.0 [§15](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/15-project.md) applies, with the deviations below.

**Status.** The manifest, path and git dependencies written (S5b, S5c1); the lock, version lines
and `[override]` come with S5c2–S5c3, a script's frontmatter with S5d, `[lints]` with S11 — until
then the design documents decide.

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

## Deviations

- `lyric-script.toml` and `lyric-script.lock`; dependencies in a script's frontmatter; `pack` ([07 Dep, Man](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md), [12 Pk](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).

**Conformance.** `conformance/cases/15-project/` (`since: 1.0.0`), package cases: a folder with
its manifest, its program in `src/main.lyrs` and its dependencies in `deps/`
([the format](../conformance/README.md)); the manifest's fields one by one in the toolchain's
own tests (`tests/package.lyr`).

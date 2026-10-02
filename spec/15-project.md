# Projects

> **Partly written.** §1 was written with milestone **M7** of the Lyric 5 plan (slice S1); the
> rest follows with M7, spec-first: each rule lands here with its conformance case before or with
> its implementation. Source of the decisions:
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
   is ([14 §1.1](14-cli.md)). The other parts of a manifest ([11 W2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)) — dependencies,
   binaries, profiles, the native part, lints, the trust rule, the toolchain pin, `include` and
   `exclude` — are refused the same way until this chapter writes them.
5. A package's **program** is its `src/main.lyr`, and its binary is named after the package
   ([14 §1.2](14-cli.md)). Without `src/main.lyr`, the package is a library (P2).

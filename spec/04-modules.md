# Modules and packages

> **Partly written.** §1 was written with milestone **M3** of the Lyric 5 plan (slice S6), §2 and
> §3 with **M7** (slices S1, S2a); the rest follows with M7, spec-first: each rule lands here with
> its conformance case before or with its implementation. Source of the decisions:
> [07 Modules](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md).

## Scope

Module names from paths, visibility (`private`, `internal`, `pub`), imports, the prelude, editions, packages and their resolution; module-level bindings.

## 1. Module-level bindings

A `let` or a `var` at the top of a module
([07 V5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)).

**Conformance.** `conformance/cases/04-modules/`.

1. A module has **no body**: it holds declarations, and importing it runs nothing (G1). A
   module-level `let` or `var` is a declaration with an initializer.
2. The module's bindings are filled **eagerly, before the entry runs**, in declaration order
   within the module (G2): a later binding may read an earlier one, and the initializer is an
   ordinary expression — a call, an object, an array. A `static let` on a type is the same
   mechanism under the type's name. *(The order across modules — imports first, a cycle an
   error — is written with the modules, M7.)*
3. A module-level **`var`** is written from any function that sees it, as a local is; a
   module-level `let` and a `static let` are not (`LYR-SEM0019`) (G5). What a `let` holds
   may still be written where it is a place: the fields of an object it references, the
   elements of an array ([03 §2.2](03-types.md#22-fields-and-places)).
4. A module-level binding is a **root**: what it references lives as long as the binding does
   ([01 L1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)).
5. An initializer does not throw (G3) — with the errors ([06](06-errors.md)) — and there is no
   `init()` hook (G6). `Lazy<T>` is a library ([12](12-stdlib.md)).

## 2. Module names

A module is a file, and its name comes from one source: its path
([07 V1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)). A package gathers modules under one name
([15 §1](15-project.md)).

**Conformance.** `conformance/cases/04-modules/` — a rule about a package as a package case, a
directory ([the format](../conformance/README.md)); what only the command line shows, in the
toolchain's own tests (`tests/Lyric5.Tests`, `PackageTests`).

1. A **package** is a directory with a manifest, `lyric.toml`; its modules are the `.lyr` files
   under its `src/`. A module's **path** is its file's path below `src/` without `.lyr`, with the
   package's name in front: `src/net/http.lyr` in the package `app` is `app.net.http` (M1). The
   package's own modules write the path the same way — there is no second, package-relative
   spelling.
2. A file has **no `module` header**: one is refused (`LYR-RES0008`), and the name is the path's
   alone (M2).
3. A **directory is a namespace, not a module**: `src/net.lyr` beside `src/net/` is the module
   `app.net`, one of its own, and a directory without such a file is no module to import
   (`LYR-RES0003`) (M5).
4. A module path names its file **exactly**, case included, on every platform: `import app.util`
   does not find `src/Util.lyr` (`LYR-RES0003`), also where the file system ignores case (M6).
5. **A file is one module**: a module that several others import is loaded once, and its
   bindings exist once (M4). Imports form no cycle (`LYR-RES0005`).
6. A **single file** outside every package's `src/` is a package of its own, named after the
   file; it imports `std` and nothing else (`LYR-RES0003`)
   ([11 C8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).
7. A program starts at the **`main` of its entry module** — a package's `src/main.lyr`
   ([15 §1](15-project.md)), or the module the command line names ([14 §1](14-cli.md)) (M7a).
   That `main` is `fn main(): void` or `fn main(): int` and may declare `throws`
   ([06](06-errors.md)); it takes no parameters (M7b) — the program's arguments are the
   standard library's ([12](12-stdlib.md)). An entry module without `main`, or with one of
   another form, is refused (`LYR-SEM0021`).
8. A `main` in any other module is an **ordinary function**: a module may be a library and a
   program at once (M7a).

## 3. Visibility

Who may name a declaration ([07 V2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)). *(The members of a type — fields, methods, static
members, variants, the methods of an `extend` block — are written with the next slice of M7.)*

**Conformance.** `conformance/cases/04-modules/`; the routes one by one in the toolchain's own
tests (`tests/Lyric5.Tests`, `VisibilityTests`).

1. A declaration carries at most **one visibility word**, ahead of every other: `pub fn`,
   `internal struct`, `private let`, `pub static fn`, `pub mut fn` ([08 D3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)). A second
   word is refused (`LYR-PAR0053`), and so is a word before an enum's variant, which is as visible
   as its enum.
2. **`private`** — the declaring module alone names it; **`internal`** — every module of the
   declaring package; **`pub`** — every module of every package: it is exported. A declaration
   **without a word is `internal`**. The standard library is a package like any: what it does
   not mark `pub` is its own.
3. Visibility is asked **at every route** a name takes out of its module, by one rule: a
   selective import; a name qualified by a module in an expression (`util.helper()`,
   `util.LIMIT`); a type named through a module in a signature, a field, a constraint, a
   conformance list, an `extend` target or a body; an initializer (`util.Point { … }`); a pattern;
   an interface-qualified call (`util.Walker.walk(x)`). A name that may not be named where it
   stands is refused (`LYR-RES0009`) (S1). Of an overload set, the functions that may not be
   named are not there.
4. **An import is its module's own**: `import std.io { println }` in `util` brings `println`
   into `util`, and no other module reaches it as `util.println` (`LYR-RES0009`) (I4).
5. A **module** itself is visible to every module (B1): what it offers is what its
   declarations' words allow.

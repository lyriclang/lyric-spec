# Modules and packages

> **Partly written.** §1 was written with milestone **M3** of the Lyric 5 plan (slice S6); the
> rest follows with **M7**, spec-first: each rule lands here with its conformance case before or
> with its implementation. Source of the decisions:
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

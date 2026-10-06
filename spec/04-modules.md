# Modules and packages

> **Partly written.** §1 was written with milestone **M3** of the Lyric 5 plan (slice S6), §2 to
> §4 with **M7** (slices S1, S2a–S2c, S3a, S3b), §5 with the review of **M8a** (R3a); the rest follows with M7, spec-first: each rule
> lands here with its conformance case before or with its implementation. Source of the decisions:
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
   ordinary expression — a call, an object, an array. A `static let` on a type that is generic
   in nothing is the same mechanism under the type's name (rule 6 for a generic type's).
   *(The order across modules — imports first, a cycle an
   error — is written with the modules, M7.)*
3. A module-level **`var`** is written from any function that sees it, as a local is; a
   module-level `let` and a `static let` are not (`LYR-SEM0019`) (G5). What a `let` holds
   may still be written where it is a place: the fields of an object it references, the
   elements of an array ([03 §2.2](03-types.md#22-fields-and-places)).
4. A module-level binding is a **root**: what it references lives as long as the binding does
   ([01 L1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)).
5. An initializer does not throw (G3) — with the errors ([06](06-errors.md)) — and there is no
   `init()` hook (G6). `Lazy<T>` is a library ([12](12-stdlib.md)).
6. A **constant of a generic type** — a `static let` in the body of a generic struct, class or
   enum, or in a generic block ([05 §6](05-interfaces.md) rule 2) — is **one per instance** (G2;
   the review's M8a-3): `Crate<int>.empty` and `Crate<string>.empty` are two constants, each
   with its instance's arguments for the type's parameters, `static let empty: ?T = null;`. It
   is read on an instance (`LYR-SEM0063` on the bare name of the type); inside its type also by
   its bare name, the constant of the instance the code runs for; and through a constraint,
   where it answers an interface's ([05 §7](05-interfaces.md) rule 2). Its value is a
   **constant**: a literal, `null`, an empty literal `[]`, another constant — `T.zero` under a
   constraint, a unit variant —, a struct initializer of these. Nothing runs for it before the
   entry, and such constants have **no order**: one may name another that stands later, and
   none names itself. Anything else — a call, an operation, an object of a class — is refused
   (`LYR-SEM0169`): a value that is computed is a `static fn`. *(Richer constant expressions
   come with `comptime`.)*

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

1a. One file is named apart: **`src/lib.lyr` is the package's root module**, and its path is the
   package's name alone — `import geo { Circle }` (the review's M7-1). There is no module
   `geo.lib` (`LYR-RES0003`), and a directory `src/lib/` is a namespace like any other (rule 3).
   The package's own modules import the root module the same way, and it may stand beside
   `src/main.lyr`.
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
9. A **declaration is its module's**: two modules may each declare one name — `app.a.Cat` and
   `app.b.Cat` — and the two are two declarations. Two such types stay two everywhere, also as
   the type arguments of one generic function, block or type: `first([a.Cat { … }])` and
   `first([b.Cat { … }])` call two instances, each with its own type's fields (M1).

## 3. Visibility

Who may name a declaration and a member
([07 V2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)).

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
6. A **member** takes its word as a declaration does (S0): a field, a method, a `static`
   function or `let`; without a word it is `internal`. It is named — read, written, called,
   destructured in a pattern — where its word allows (`LYR-RES0009`), whatever route reached its
   type. Of a member's overload set, what may not be named is not there.
7. A type with a field a module may not name is **built** in no such module: its initializer
   is refused there, and so is a copy with `with` (`LYR-RES0009`) — a factory builds it
   ([04 D11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/04-abstraktion.md), [02 W3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/02-wertmodell.md)).
8. An enum's **variants** are as visible as the enum. An **interface's members** — what it
   requires and its defaults — are as visible as the interface; a word on one is refused
   (`LYR-SEM0118`) (S4). The one exception is **`private fn` with a body**, a helper: the
   interface's defaults call it, on any value of the interface, and nothing else does
   (`LYR-RES0009`) — a child interface's defaults no more than other code; no conformer answers
   it, and a conformer's method of its name is the conformer's own, which the defaults do not
   call. A `private` member without a body is refused (`LYR-SEM0118`).
9. An **`extend` block's** word is the default of the methods in it: `private extend Point { … }`
   keeps them to its module; a method's own word wins. A method of a block that a module may not
   name is not there for it (S5).
10. A **conformance** — `extend Point :: [Shape] { … }` — is visible wherever its type and its
    interface are, its methods with it; a word on the block or on one of its methods is refused
    (`LYR-SEM0150`) (S5).

10a. A member that **answers an interface** for its type from outside a conformance block — a
    method, a static function or a constant in the type's body, or in a block of rule 9 — is
    written at least as visible as the conformance, the narrower of its type's word and its
    interface's (`LYR-SEM0167`; the review's M7-2): in `pub struct Sq :: [Shape]` with a `pub`
    interface `Shape` it is `pub fn area()`; where the type or the interface is `internal`, no
    word is enough, and `private` is not. A conformance cannot be narrowed (rule 10), so a member
    written narrower would be called through the interface by code its own name refuses.
11. A declaration is **no more visible than the types it names** (S2): a function's parameters,
    result, thrown types and constraints, a field's type, an alias's, a variant's payload, a
    module binding's or a `static let`'s type — written or inferred —, a type's constraints and an
    interface's parents. A `pub fn` whose result is an `internal` type, an `internal fn` taking a
    `private` one, is refused (`LYR-SEM0151`): another module could reach it and not name what
    it hands out. A member counts as its own word narrowed to its type's.
12. A member whose **written** word is wider than its type's — `pub x` in an `internal struct` — is
    allowed and warned (`LYR-SEM0152`): it is exported only once the type is (S3). A member
    without a word follows its type and is not warned. The same holds in a block of rule 9: for
    a member's own word, and for the block's — said once, at the block, for its members.

## 4. Imports

How a module names what other modules declare ([07 V3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md)).

**Conformance.** `conformance/cases/04-modules/`; the forms one by one in the toolchain's own
tests (`tests/Lyric5.Tests`, `ImportTests`).

1. An import takes one of **three forms** (I1): **selective**, `import app.util { answer, Point }`,
   binds the names it lists; **qualified**, `import app.util;`, binds the module under its last
   segment — `util.answer()`; **aliased**, `import app.util as u;`, under another name. A
   selective item may be **renamed**: `{ answer as reply }` binds `reply`, and `answer` is not
   bound (I2). There is no import of everything (I3).
2. **`pub import`** passes on what it binds (I4): `pub import app.util { answer };` in `app.facade`
   makes `answer` a `pub` member of `app.facade` — imported from there, named as `facade.answer`,
   under the name it was renamed to; a module imported qualified or aliased is passed on as a
   namespace (`facade.util.answer()`). It passes on what is `pub` and nothing narrower
   (`LYR-RES0010`). No other word stands before `import` (`LYR-PAR0053`); without `pub`, an
   import is its module's own (§3 rule 4). A package's root module (§2 rule 1a) is where a
   library passes on what its modules declare: `pub import geo.shapes { rect };` in `src/lib.lyr`
   makes `import geo { rect }` of it.
3. An import a module never uses is **warned**, in every form (`LYR-SEM0072`) (I5): a qualified
   import is used when its module is named, or one of its extension methods called. A `pub
   import` is used by being passed on.
4. The **prelude**, the module `std.prelude`, is named in every module without an import (I8;
   [10 B2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)): `panic`, `assert`, `unreachable`, `todo`, `same`, `sequence`; `Error`, `Exception`, `Box`,
   `Ordering`, `Range`, `RangeInclusive`, `RangeFrom`, `RangeTo`, `RangeFull`; `Equatable`,
   `Hashable`, `Ordered`, `TotalOrder`, `Display`, `Debug`, `Default`, `Clone`, `Closeable`,
   `Num`, `Integer`, `Float`, `Iterator`, `Iterable`, `Index`, `IndexSet`; `List`, `Map`, `Set`,
   the collections' vocabulary — what signatures and the language need, not effects: `println`
   is `std.io`'s. The rest of the
   standard library is imported, `std.core`'s operator interfaces (`Add` …) and `Any`
   among it. The prelude grows with the library ([12](12-stdlib.md)).
5. A name a module declares or imports hides the prelude's of that name in the module, and is
   warned (`LYR-SEM0153`) (K6). An import of the very symbol the prelude passes on hides nothing.
   A block of a module the prelude takes names from stands in every module, as `std.core`'s do:
   `Map<K, V>.new()` is reached wherever `Map` is.
6. A **builtin type's** name — `int`, `string`, `bool` … — is no declaration's (`LYR-RES0011`)
   (K5).
7. A name a module declares or imports is **not also one of its submodules**: `app.net` declaring
   `http` beside the module `app.net.http` is refused (`LYR-RES0012`) (K1, K3). The question is
   asked of the package's files, not of what a program imports: a submodule nobody imported is
   one all the same. The root module's names stand beside every module of its package —
   `geo` declaring `shapes` beside `src/shapes.lyr` — but not beside its own file: there is no
   module `geo.lib`. An import that binds a module under its own name — `pub import geo.shapes;`
   in `geo` — is that module, and one meaning. `std` is the
   standard library's name: a single file `std.lyr` is refused (`LYR-RES0013`) (D1).

## 5. A type's members by their bare names

What a bare name means between the braces of a type
([07 V6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/07-module.md), the review's M6-30).

**Conformance.** `conformance/cases/04-modules/`.

1. The body of a struct, a class, an enum or an interface is a **scope inside its module's**: in
   the bodies of its methods a member's name hides a module's, an import's and the prelude's of
   that name, and a local or a parameter hides the member, whole. An `extend` block is such a
   scope for the members it declares itself; the members of the type's body are not named bare
   there.
2. A **static** member is reached by its bare name there — `of(2)`, `step` — as it is through
   the type.
3. A member **of an instance** — a field, a method that is not `static` — is reached through its
   receiver: `this.label`, `this.size()`. Its bare name is refused (`LYR-SEM0055`). So is a
   variant's, in its enum's own methods too: a variant is written `.Red` or `Color.Red`, as in a
   pattern ([09](09-patterns.md)).
4. In a **call**, `label(…)`, a field counts only when it can be called — when its type is a
   function type, or an optional one: a field `label: string` does not hide the function `label`
   there, and the call means the function. A field that can be called is what the call means
   (rule 3). Where a field that cannot be called is all the name means, the call is refused as
   one of something that is no function (`LYR-SEM0013`).

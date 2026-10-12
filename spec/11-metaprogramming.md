# Metaprogramming

> **Partly written.** §1 was begun with milestone **M8a** of the Lyric 5 plan (`@Test`), §2–§4 with
> **M9a** (`comptime`, `@When`, `std.meta`); the rest comes with **M9b**, spec-first: each rule lands here with its conformance case before or
> with its implementation. Source of the decisions:
> [09 Metaprogramming](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/09-metaprogrammierung.md).

## Scope

Attributes (data, compiler instructions, macros), `comptime`, `std.meta`, conditional compilation with `@When`, macros over `std.syntax`.

## 1. Attributes

([09 A1–A3, A11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/09-metaprogrammierung.md))

**Conformance.** `conformance/cases/11-metaprogramming/`; what `lyric test` makes of a test, the
toolchain's own tests (`tests/Lyric5.Tests`, `TestCommandTests`).

1. An attribute is a struct that declares a **marker** for where it may sit (rule 4), and a use
   writes its fields: `@Test { skip = "needs a network" }`. An attribute with exactly one field
   without a default also takes that field's value in parentheses, `@Retry(3)`; with any other
   number the form is refused (`LYR-SEM0094`). The compiler reads the attributes of a closed
   list in `std.core` by their identity: `@Test` is `std.core.Test` — a struct of the program's
   own named `Test` is data, nothing the compiler reads.
2. **`@Test`** — in the prelude — marks a test, which `lyric test` runs ([14 §3](14-cli.md)): a
   function that takes no parameters, returns `void` and is not `private` (`LYR-SEM0154`), and
   is not generic (`LYR-SEM0067`, as for every attribute but the compiler instructions of rule 7).
   It may throw: an error that leaves it
   fails the test. `skip` says why the test is not run, `timeout` how many seconds it may take
   (60 unless it says; 0 for no limit).
3. **`@callerExpr(p)`** — in the prelude — sits on a parameter: where a call leaves that
   parameter out, it gets the text the call wrote for `p`, another parameter of the function —
   `assertEq(xs.length(), 3)` hands the assertion the words `xs.length()` — as it is written,
   the parentheses in it and around it included: `(1..5).sum()`, `(a + b)`. The parameter is a
   `string` and has a default, which a call that writes the argument itself keeps; the attribute
   names its parameter by name (`LYR-SEM0155`). Beside it a parameter takes what its marker
   admits there (rule 4).
4. **Every declaration takes attributes** (09 T7): the module header (`module;`, §3 rule 4), a function, a method, a
   field, a `static let`, a variant, a parameter, a struct, a class, an enum, an interface, an
   alias, an `extend` block, a module-level binding, an associated type. A marker names one kind
   or a set of them (09 F1): `OnModule`; `OnFunction` (a function at the top level), `OnMethod`,
   `OnField`, `OnParameter`, `OnVariant`; `OnType` (a struct, a class, an enum), `OnInterface`,
   `OnAlias`, `OnExtend`; and the sets `OnCallable` (a function, a method), `OnMember` (a method,
   a field, a `static let`, a variant, an associated type), `OnTypeLike` (a struct, a class, an
   enum, an interface, an alias), `OnTopLevel` (what stands at a module's top level), `OnDecl`
   (every named declaration) and `OnAny` (every place). The markers inherit nothing from each
   other. An attribute none of whose markers admits the declaration it stands on is refused
   (`LYR-SEM0065`).
5. **An attribute's value is computed while the program compiles** (09 F4): its fields are
   values as a `comptime` site's are (§2) — literals, `let`s, calls: `@Test { timeout = LIMIT }`.
   The value is the struct the use writes, its defaults filled, and what the compiler and the
   tools read is that value. A field of a type no literal makes is refused (`LYR-SEM0100`); a
   panic while computing it is `LYR-CT0001`.
6. An attribute makes nothing reachable (01 B13): a function only an attribute marks is not
   built. A test is reached from the program `lyric test` writes.
7. **The compiler instructions** — in the prelude — are the closed list of `std.core` the compiler
   reads (09 A11, T2): `@Test` (rule 2), `@callerExpr` (rule 3), `@callerLine` and `@callerFile`
   (rule 8), `@Deprecated` (rule 9), `@AlwaysInline`, `@NoInline` and `@Cold` (rule 10),
   `@MustUse` (rule 11), `@NonExhaustive` (rule 12), `@Allow` (rule 13), `@Shared` (rule 14) and `@When` (§3). What one says holds for
   every instance, so beside `@Test` they sit on a generic declaration too, where data may not
   (`LYR-SEM0067`).
8. **`@callerLine`** on an `int` parameter and **`@callerFile`** on a `string` one: where a call
   leaves the parameter out, it gets the line the call begins on, or the file the call stands in —
   the package's name, then the path within the package, with `/` on every system:
   `app/src/main.lyr`. A call through an interface gets them as a direct call does. The parameter
   has a default, which a call that writes the argument keeps (`LYR-SEM0155`, as for another type).
9. **`@Deprecated { message, until, replacement }`** sits on what a use names: a module, what
   stands at a module's top level, a member — not a parameter (`LYR-SEM0065`); on an `extend`
   block it deprecates the block's members. Every use outside a deprecated declaration warns
   (`LYR-SEM0076`) with `message`, and names `replacement` as what to write instead. `until` names
   the release that removes the declaration: a toolchain that claims that version or a later one
   refuses the attribute (`LYR-SEM0081`), as it refuses an `until` that is no version, `"5.1"` or
   `"5.1.2"`. Each field is a value computed as rule 5 says.
10. **`@AlwaysInline`**, **`@NoInline`** and **`@Cold`** on a function or a method are hints to the
    C compiler — `always_inline`, `noinline`, `cold` —, no promise: the program computes what it
    computes without them. `@NoInline` keeps the compiler's own inlining away too. A function takes
    `@AlwaysInline` or `@NoInline`, not both (`LYR-SEM0177`).
11. **`@MustUse`** on a function or a type: an expression statement that drops what such a function
    gives, or a value of such a type, warns (`LYR-SEM0178`); `let _ = …` drops a value on purpose,
    and a `void` call gives nothing to use. In the standard library `Result` carries it, and
    `std.task.spawn`, whose handle alone carries the task's error.
12. **`@NonExhaustive`** on an enum or a sealed interface: outside the package that declares it, a
    `match` covers it with a `_` or binding arm alone (`LYR-SEM0050`; [09 §3](09-patterns.md)) — a
    later version may add to it; inside, its variants or conformers cover it.
    `std.io.IoErrorKind` carries it.
13. **`@Allow("LYR-SEM0071")`** takes back the warnings with that code within the declaration it
    sits on, or in the module whose header carries it; **`[lints] allow`** in a package's manifest
    takes them back in the package's files ([15 §1](15-project.md)) — two places, one mechanism.
    An error is never taken back. An `@Allow` that takes back nothing warns (`LYR-SEM0180`), and a
    value that is no code is refused (`LYR-SEM0179`): the lints' names come with
    [16](16-diagnostics.md).
14. **`@Shared`** on a field: the `clone()` a `Clone` synthesis writes copies the field instead of
    cloning it ([05 §14](05-interfaces.md#14-conformance-synthesis) rule 2) — the reference, where
    the field holds one. A `clone()` the type writes itself is its own.

## 2. `comptime`

([09 A4, Q1–Q7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/09-metaprogrammierung.md))

**Conformance.** `conformance/cases/11-metaprogramming/`, the cases on `comptime`; that a site
computes what the binary computes — the number tower, the texts of numbers, strings, containers,
the error paths — in the toolchain's own tests (`tests/Lyric5.Tests`, `ComptimeTests`).

1. **`comptime e`** evaluates `e` while the program is compiled, and the site stands for the value,
   a literal of its type. The value is of any **value type**: a scalar, a `string`, and an array,
   an inline array, a tuple, an optional, a struct, an enum or a `Box` of such. An array is the
   program's to write: every evaluation of the site gives a fresh one, as an array literal does.
   An object of a class, a view, a function value, a coroutine and an interface value are no
   literal (`LYR-SEM0100`, with the reason).
   `e` sees what the module level sees and what it binds itself: it names no local or parameter of
   the function it stands in and no `this`, and assigns nothing it did not bind — a module's
   variable is the run's, not the build's (`LYR-SEM0100`).
2. **The code evaluated is pure** (Q3): `e` calls functions, which then run at compile time, and
   builds values of any type on its way. A call that reaches the world — the console, files, the
   network, the clock, randomness, processes, threads and tasks — is an error at the site
   (`LYR-CT0003`) that names the call and the calls that led to it.
3. **A panic** of the evaluation is an error at the site (`LYR-CT0001`). It names the run-time code
   the program would have ended with and shows the frames of the evaluation, innermost first (Q6).
4. **The value is the binary's** (Q7): `e` computes as the compiled program does, in the profile it
   is built in — an overflow panics where the profile checks ([03 T2](03-types.md)) and wraps where
   it does not —, and alike on every platform the compiler runs on.
5. **Each site has a budget** of steps (Q5): the toolchain's, or `comptimeBudget` of the root
   manifest ([15 §1](15-project.md) rule 7). A site that takes more is an error at the site
   (`LYR-CT0002`) that names the budget. What one step is belongs to the implementation. The
   standard library's sites take the toolchain's budget whatever the manifest says: a program's
   budget is its own code's, and std's tables are no part of it.
6. **`comptime { … }`** is a block evaluated whole, its last expression the value. It binds,
   assigns, loops and builds lambdas as any block does.
7. **`comptime if (c) { … } else { … }`** chooses while compiling: `c` is a site of type `bool`, and
   an `else if` after it chooses the same way. Every branch is checked; only the chosen one is part
   of the program, so a function only another branch calls is not built. A `let` condition is
   refused (`LYR-SEM0100`).
8. **`comptime for (x in w) { … }`** unrolls: `w` is a site holding an array, and the body, checked
   once, stands once per element, with `x` that element's value. A `continue` goes on with the
   next round, a `break` past the last. A pattern in place of `x`, or a `w` that is no array, is
   refused (`LYR-SEM0100`).
9. **`embed(path)`** (`std.core`) gives the bytes of a file as a `uint8[]`, read while the program
   compiles (Q4). `path` is relative to the module that calls, and the file lies within the
   package's directory; a module of no package is held to its own directory. A file outside, or
   none, is `LYR-CT0004`. It is the one thing code run at compile time reads from outside the
   program, and a build reads the file again when it changes. A `comptime` site, or what one calls,
   makes the call; a call the program would make at run time is refused (`LYR-CT0004`).


## 3. Target, profile, `@When`

([09 A6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/09-metaprogrammierung.md), [11 W2 P11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md))

**Conformance.** `conformance/cases/11-metaprogramming/`; what a cross-build emits, the toolchain's
own tests (`tests/Lyric5.Tests`, `TargetTests`).

1. **`target`** and **`profile`** — `std.core`, in the prelude — are constants of the build (B4):
   `target.os` (`Platform`: `Linux`, `MacOS`, `Windows`, `Other`), `target.arch` (`Arch`: `X86_64`,
   `Aarch64`, `Other`) and `target.pointerWidth` (in bits) are the target's — a cross-build's, not
   the host's —, and `profile.debug` holds where the profile is the built-in `debug` or inherits
   from it ([15 §4](15-project.md)). A program that reads neither carries neither.
2. **`comptime if (target.os == .Windows)`** chooses by them while compiling (§2 rule 7): every
   branch is checked, the chosen one is built.
3. **`@When(cond)`** — in the prelude — on what stands at a module's top level, or on the module
   (rule 4): `cond` is a `bool` computed while compiling (§1 rule 5), over `target` and `profile`.
   Where it holds, the declaration is built. Where it does not, the declaration is checked as every
   other, its `comptime` sites are not evaluated, and nothing of it is built. A use the program would
   run of what a build leaves out is refused (`LYR-CT0006`); a use within what it leaves out, or in
   the branch a `comptime if` does not take, is none. `@When` chooses no name: two declarations of
   one name stay refused (`LYR-RES0001`, `LYR-SEM0085`), and `comptime if` chooses between names.
4. **The module header** `module;` names nothing — the path names the module
   ([04 §2](04-modules.md) rule 2) — and carries the module's attributes:
   `@When(target.os == .Windows) module;` leaves the whole module out of every other build. One
   module per target is a file per target, chosen between with `comptime if`.

## 4. Type information

([09 A5, A7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/09-metaprogrammierung.md), [10 B13 M1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md))

**Conformance.** `conformance/cases/11-metaprogramming/`.

1. **`std.meta`** answers questions about a type as constants (R1): `fields<T>()`, a
   `FieldInfo { name, type, index, visibility, isVar }` per field of a struct or a class, in
   declaration order, `index` its place in the answer; `variants<E>()`, a
   `VariantInfo { name, index, payload }` per variant, the payload's fields named by their position
   where they have no names; `members<T>()`, a `MemberInfo { name, visibility, isStatic, isMut }` per
   function of the type's own body; `conformances<T>()` and `hasConformance<T, I>()`;
   `typeName<T>()`; `isStruct`, `isClass`, `isEnum`, `isInterface<T>()`. A `Type` holds its name.
   Each answer is a constant of the type at the instance it is asked at — in a generic function or a
   default, of each instance (R3). Nothing is reflected at run time (R6): a program reads a type
   through such constants alone.
2. **What a question sees** (R7) is what the code that asks may name: the module of the function
   it stands in, the interface's for a default. Another package's field is listed where it is
   `pub`, one of the package where it is not `private`, one of the module always; members alike.
3. **`comptime for (f in fields<T>())`** walks the answer (§2), its body once per field. Where `T`
   is a type the loop's place knows — a written type, or `Self` in a default (rule 5) — each round
   has the body as its own: `f` is that field's info, a constant a `comptime` site of the round may
   read (`comptime if (f.isVar)`), and **`e.[f]`** is the field of `e` that `f` names, of the
   field's own type — read, written and a place as `e.name` is (R2). `e` is a value of the type `f`
   walks the fields of (`LYR-SEM0185`). Where `T` is known only per instance — a type parameter of
   a generic function — the rounds share one body, checked once: `f` is a `FieldInfo`, and no field
   is read through it (`LYR-SEM0185`).
4. **`attribute<A>(f)`** is the attribute of type `A` that the field `f` names carries, its value,
   or `null` (R4); `f` is a round's variable (`LYR-SEM0185`). **`typeAttribute<T, A>()`** is the
   one `T`'s declaration carries.
5. **A default that walks `Self`'s fields is set in place for each conformer that takes it** (A5):
   checked as the conformer's — `Self` and `this` the conformer, its names those of the
   interface's module —, each round's `this.[f]` of the conformer's field's type. What is wrong
   there is said at the line written once, with the field and the conformer named. A call through
   a value of the interface reaches it; a conformer that writes the member itself takes nothing
   ([05 §14](05-interfaces.md) rule 1). A generic conformer's field of a parameter's type has what
   the parameter's constraints give it: `struct Pair<T :: [ToJson]> :: [ToJson]` is written out,
   `Pair<T>` without the constraint is refused at the default's line.
6. A `comptime` site is evaluated once: one that asks `std.meta` about a type known only per
   instance within a larger expression is refused (`LYR-SEM0100`); asked alone,
   `comptime fields<T>()`, the question is answered per instance.
7. **`comptime for (v in variants<E>())`** walks an enum's variants (M9a S10), its body once per
   variant where `E` is a type the loop's place knows, `v` that variant's info. In such a round
   **`e is v`** is `true` where the enum value `e` holds the variant — a test of the run, a `bool`
   —; **`E.[v]`** is the value of a unit variant; **`E.[v](…)`** builds a variant with a tuple
   payload and **`E.[v] { … }`** one with a struct payload, its fields by name or by info (rule 8);
   **`comptime for (p in v.payload)`** walks the payload's fields, its body once per field with
   `p` that field's info, and **`e.[v, p]`** is that field of `e`, of the field's own type — read,
   written and a place as `e.name` is. `e.[v, p]` where `e` holds another variant is a panic. Each
   form outside such rounds, or over a type known only per instance, is `LYR-SEM0185`.
8. **An initializer over infos.** In an initializer of a struct or a class — a written type
   without type arguments, or `Self` in a default — **`[f] = e`** sets the field the round's
   variable `f` names, and **`comptime for (f in fields<T>()) [f] = e`** sets one field per round,
   `e` checked with `f` that field's info and against the field's type. The fields set are the
   written ones (`LYR-SEM0070` twice, `LYR-SEM0015` none such, an omitted one as for a written
   initializer); the rounds walk the fields of the type built (`LYR-SEM0185` otherwise). The same
   items build a variant's struct payload in `E.[v] { … }`, over `v.payload`.
9. **A `comptime if` a round decides** checks the chosen branch alone — against [§2](#2-comptime)
   rule 7, which checks every branch: the other may name what this field's type has not, a
   `clone()` of a `@Shared` field. A round decides a condition made of its variables' `isVar`,
   `index` and `name`, a variant's `index` and `name`, `attribute<A>(f)` against `null`,
   `isEnum<T>()` and its kin of a known type, literals, and `==`, `!=`, `<`, `<=`, `>`, `>=`, `!`,
   `&&` and `||` over them. **`comptime if (c) a else b` is a value** too: where a round decides
   `c`, the chosen arm alone is checked and is the value; otherwise both arms, of one type
   (`LYR-SEM0100`), and the site chooses.
10. **The family asks with the conformer's module.** The defaults of `Equatable`, `Hashable`,
   `Ordered`, `TotalOrder` and `Clone` in std.core ([05 §14](05-interfaces.md)) see every field
   of the conformer, whatever its word: a type's internal and private fields compare, hash and
   clone as its `pub` ones do. Every other interface's default sees what rule 2 gives it. What
   is wrong in one of the family's is said at the conformer's entry ([05 §14](05-interfaces.md)
   rule 6). A write through an info, `this.[f] = …`, answers to the field's word and the
   function's `mut` as a write to the field by name does (`LYR-SEM0019`).

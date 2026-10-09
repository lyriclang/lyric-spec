# Metaprogramming

> **Partly written.** §1 was begun with milestone **M8a** of the Lyric 5 plan (`@Test`), §2 with
> **M9a** (`comptime`); the rest comes with **M9a/M9b**, spec-first: each rule lands here with its conformance case before or
> with its implementation. Source of the decisions:
> [09 Metaprogramming](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/09-metaprogrammierung.md).

## Scope

Attributes (data, compiler instructions, macros), `comptime`, `std.meta`, conditional compilation with `@When`, macros over `std.syntax`.

## 1. Attributes

([09 A1–A3, A11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/09-metaprogrammierung.md))

**Conformance.** `conformance/cases/11-metaprogramming/`; what `lyric test` makes of a test, the
toolchain's own tests (`tests/Lyric5.Tests`, `TestCommandTests`).

1. An attribute is a struct that says where it may sit — `std.core`'s `OnModule`, `OnType` or
   `OnFunction` — and a use writes its fields: `@Test { skip = "needs a network" }`. The
   compiler reads the attributes of a closed list in `std.core` by their identity: `@Test` is
   `std.core.Test` — a struct of the program's own named `Test` is data, nothing the compiler
   reads.
2. **`@Test`** — in the prelude — marks a test, which `lyric test` runs ([14 §3](14-cli.md)): a
   function that takes no parameters, returns `void` and is not `private` (`LYR-SEM0154`), and
   is not generic (`LYR-SEM0067`, as for every attribute). It may throw: an error that leaves it
   fails the test. `skip` says why the test is not run, `timeout` how many seconds it may take
   (60 unless it says; 0 for no limit).
3. **`@callerExpr(p)`** — in the prelude — sits on a parameter: where a call leaves that
   parameter out, it gets the text the call wrote for `p`, another parameter of the function —
   `assertEq(xs.length(), 3)` hands the assertion the words `xs.length()` — as it is written,
   the parentheses in it and around it included: `(1..5).sum()`, `(a + b)`. The parameter is a
   `string` and has a default, which a call that writes the argument itself keeps; the attribute
   names its parameter by name (`LYR-SEM0155`). It is the one attribute a parameter takes
   (`LYR-SEM0065`).

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
   (`LYR-CT0002`) that names the budget. What one step is belongs to the implementation.
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

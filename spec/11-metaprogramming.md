# Metaprogramming

> **Partly written.** §1 was begun with milestone **M8a** of the Lyric 5 plan (`@Test`); the rest
> comes with **M9a/M9b**, spec-first: each rule lands here with its conformance case before or
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
   fails the test. `skip` says why the test is not run.

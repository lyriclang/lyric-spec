# Expressions

> **Skeleton.** Written with milestone **M2/M3** of the Lyric 5 plan, spec-first: each rule lands
> here with its conformance case before or with its implementation. Source of the decisions:
> [08 Syntax](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md), [04 Abstraction D6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/04-abstraktion.md).

## Scope

Precedence, evaluation order, assignment as an expression, `++`/`--`, wrapping operators, `??`, `if` and `match` as values, lambdas and trailing blocks, `with`.

## 1. Calls

A call names a function and gives it arguments
([04 D4, D5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/04-abstraktion.md),
[08 Y9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)).

**Conformance.** `conformance/cases/08-expressions/`.

### 1.1 Arguments

1. An argument is **positional**, in parameter order, or **named**, `connect(host: "h", port: 80)`:
   the name is the parameter's own, every parameter has one, and a parameter's name is therefore
   part of the function's public form (D5 F5). Positional arguments come first, named ones after
   them in any order (F6); a positional argument after a named one, a name given twice or for a
   parameter already set positionally, and a name no parameter has are refused (`LYR-SEM0119`).
   A **variadic** parameter, `nums: int...`, takes the remaining positional arguments as an
   array of what it names, `int[]`, and is not named (F8). It stands last and has no default — a
   call without its arguments passes the empty array; a single remaining argument of the array's
   own type passes as the whole array, so that one variadic function hands its arguments on to
   another, `fn logged(xs: int...): int { return sum(xs); }`. Lyric 4's `params xs: int[]` is
   gone (`LYR-SEM0024`).
2. A parameter may carry a **default**, `fn connect(host: string, port: int = 80)`, at any
   position (F3): a call that leaves it out gets the default, and a default in the middle is
   left out by naming what follows. The default is evaluated **per call, in the function's
   scope**, after the arguments before it, and may read the parameters declared before it —
   `fn span(from: int, to: int = from + 10)`; a later parameter is not in its scope, and
   neither is `this` (`LYR-SEM0120`) — the receiver is nobody's before the call (F2). A
   parameter without a default that a call gives nothing for is refused (`LYR-SEM0014`).
3. A call through a function value is positional only: the value's parameters have no names
   (`LYR-SEM0119`).
4. **`&x`** marks the argument of a place parameter ([03 §2.3a](03-types.md)): the place `x`,
   not its value. The mark covers the whole argument and stands at an argument and nowhere else
   (`LYR-PAR0054`).

### 1.2 One name, several counts

1. Functions and methods of one scope may share a name when they take **different numbers of
   arguments** — `of(hex)` beside `of(r, g, b)` — and never otherwise (D4): a call counts its
   arguments and finds one candidate, with no ranking and no conversion of any kind; none that
   takes that many is refused (`LYR-SEM0087`). The names of the arguments decide nothing (F7).
   A type's members are one scope with its blocks' ([05 §13](05-interfaces.md)): a method and a
   static reached through the type's name count among them alike — `int8.parse(s)` beside
   `int8.parse(s, 16)`.
2. Two declarations of one name whose counts overlap for any number — a default widens a
   count to a range — are a redeclaration (`LYR-SEM0085`), at the declaration and never at a
   call. An interface declares a member once (`LYR-SEM0088`).
3. The bare name of a shared one is a value only where the position says which, by its
   function type (`LYR-SEM0089`).
4. `Point(1, 2)` is `Point.new(1, 2)` (Y9): `new` is an ordinary static function, so `Point(4)`
   reaches a one-argument factory declared beside the two-argument one.

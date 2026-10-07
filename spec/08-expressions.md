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
   A trailing block ([03 §8.2](03-types.md)) is a positional argument, the call's last: behind
   named ones it is refused like any other.
   A **variadic** parameter, `nums: int...`, takes the remaining positional arguments as an
   array of what it names, `int[]`, and is not named (F8). It stands last and has no default — a
   call without its arguments passes the empty array. Each remaining argument is **one
   element**, an array too: `sum(xs)` with `xs: int[]` hands `sum` one argument that is no `int`
   (`LYR-SEM0001`), and where the element type takes an array — `Any...`, a type parameter's
   `T...` — the array is that one element. **`xs...`** spreads an array over the parameter
   instead: the argument is the rest — the one argument the call spreads, alone in the rest,
   of the parameter's array type, at a parameter that is variadic (`LYR-SEM0166`) — and the
   parameter *is* that array, nothing is copied. So one variadic function hands its arguments
   on to another, `fn logged(xs: int...): int { return sum(xs...); }`. Lyric 4's
   `params xs: int[]` is gone (`LYR-SEM0024`).
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
5. **The order.** A call through a receiver evaluates the receiver first, then the arguments
   (04 D6: left to right everywhere) — for a member a block gives as for a type's own (M8a S15:
   a block's evaluated its arguments first).

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

## 2. `if` and `match` as values

1. **`if (c) a else b`** is an expression: `c` is a `bool`, the `else` is required
   (`LYR-PAR0036`), and exactly one branch is evaluated. A branch is an expression or a **value
   block** ([07 §3](07-statements.md#3-value-blocks)): `if (c) { …; a } else { …; b }`; the two
   forms mix, and `else if` goes on. A block ends its branch — an operator behind it takes the
   whole `if`, `if (c) { 1 } else { 2 } + 3` is a sum — where a branch without braces takes
   everything to its right.
2. **Its type.** Where the position wants a type, each branch meets it and the `if` has it;
   otherwise the branches unify, as arms do (`LYR-SEM0016`), a `null` branch making the other
   optional. A branch worth `never` — one that leaves — contributes nothing: `if (x < 0)
   { continue; } else { x }` is `x`'s type. Both branches worth `never`: so is the `if`. Both
   worth nothing — two calls that give none, two blocks without a tail — and so is the `if`: it
   stands where nobody takes a value, `(c) => if (c) yes() else no()`.
3. **`x ?? { … }`**: the right of `??` may be a value block, evaluated only when `x` is absent —
   `let n = v ?? { return 0; };`, `v ?? { let d = base(); d + 1 }`.
4. **`match (e) { p => v, p => { …; v } }`** is worth the arm that is taken. An arm's body is an
   expression or a value block; the arms unify as the branches of an `if` do, or each meets the
   type the position wants. A block arm that leaves — `return`, `throw`, and a **`break` or
   `continue`** of the loop around the `match` — contributes nothing; a `match` whose arms all
   leave is worth `never`, and one whose arms are all worth nothing is worth nothing. A block
   arm that runs to its end without a tail beside an arm that gives a value, or where the
   position wants one, is refused (`LYR-SEM0033`).
5. **Definite assignment** ([07 §1](07-statements.md#1-loop-and-the-jumps) rule 5) treats the
   branches of an `if` expression as an `if` statement's: behind it a variable is assigned when
   every branch that completes assigned it.

## 3. Assignment

An assignment is an expression
([04 D6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/04-abstraktion.md):
left to right everywhere, the target before the value).

1. **The target before the value.** What leads to the place — the receiver, then the index or
   the key — is evaluated first, left to right and once; then the value; then the store.
   `xs[next()] = next()` stores the second count at the first — in an array as through a type's
   own index ([05 §12](05-interfaces.md) rule 9).
2. **A compound assignment** `t op= v`, and `t++` and `t--`, evaluate what leads to the place
   once, read it, compute, and write it: `xs[next()] += 1` calls `next` once.
3. **Its value** is the value stored, at the type of the place: `o = v` where `o` holds a `?T`
   or an interface is worth that `?T` or that interface. A compound assignment is worth the
   new value; `t++` the old one, `++t` the new.

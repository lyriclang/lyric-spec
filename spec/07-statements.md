# 7. Statements, bindings, and flow

## 7.1 Bindings

`let` binds immutably, `var` mutably; both infer the type from the initializer when no
annotation stands. Immutability is per binding: a `let` of a class value still permits `mut`
method calls through it — the REFERENCE is immutable, the object is the object's business.
Destructuring `let (a, b) = pair;` binds tuple elements — names, `_`, and nested tuple
patterns; no form that can fail, and an initializer is required. `_` names a deliberately
unused binding and silences the unused warning.

## 7.1a Parameters: defaults and `params`

A parameter may carry a default (`fn f(n: int = 0)`), and the LAST parameter may be `params`
with an array type, collecting surplus arguments. Both are **call-site** transformations
resolved against the callee's declaration — which is why a function VALUE has neither: its
type says arity and nothing more.

## 7.2 Loops and `for-in`

`while`, `do-while`, and `for (x in e)` with `break`/`continue`. `for-in` accepts exactly:
a range (`a..b` exclusive, `a..=b` inclusive), an array, a string (yielding `char` code
points), a value satisfying `Iterable<T>` (a fresh cursor per loop), or an `Iterator<T>` value
directly. Iterator conformance reached through an interface chain counts. Anything else is
`LYR-SEM0007`.

## 7.3 `return`, coverage, and lambdas

A non-void function must return or throw on every path (`LYR-SEM0017`); the coverage analysis
is structural (no CFG is specified — a conforming implementation may be smarter, never
laxer... and never stricter on the cases the conformance suite fixes).

Lambdas infer bidirectionally: unannotated parameters take the context function type; an
expression body contributes its type outward. A **block** lambda without annotation or context
infers its return type from its `return` statements, unified like match arms — `return null;`
widens to the optional, disagreeing returns are one error at the lambda, and a non-void
inferred lambda still needs coverage (`LYR-SEM0046`). A valueless block lambda is `void`.
Closures capture variables by reference; a captured `var` mutates through the closure.

## 7.4 Flow narrowing

Inside a region where an optional is proven present, its type IS `T`, not `?T`:

- `if (o != null) { … }` narrows `o` in the then-branch; `if (o == null) { return; }` narrows
  after the guard;
- a `match` with a `null` arm narrows the non-null arms;
- narrowing follows the negation and early exits (`return`, `break`, `continue`, `throw`,
  `panic` — `panic` returns `never` and ends the path).

Narrowing keys on the comparison operators themselves. A function call cannot narrow — after
`if (isSome(o))` the type is still `?T` — which is why the standard library deliberately has no
`isSome`.

## 7.5 `defer`

`defer stmt;` schedules the statement for scope exit, in reverse declaration order, on every
exit path including `throw`. `std.os.exit` runs no defers.

## 7.6 `match`

`match` arms carry patterns: `_`; literals (integer, float, string, char, bool, `null`);
bindings; enum variants with nested payload patterns (`Some(x)`, `Point { x }` — a shorthand
field pattern binds the field to its own name and is exempt from the unused-binding warning by
decision); tuple patterns; **or-patterns** (`a | b`); and **range patterns**
(`1..5`, `'a'..='z'`). An arm may carry a guard: `Pattern if expr => …`.

Exhaustiveness is checked where the scrutinee is enumerable — enum variants, `bool`, and the
two states of a `?T` — and a gap is an error naming what is missing (`LYR-SEM0050`). Open
types (`int`, `string`, …) require a `_` or binding arm. A guarded arm does not count toward
exhaustiveness.

# 7. Statements, bindings, and flow

## 7.1 Bindings

`let` binds immutably, `var` mutably; both infer the type from the initializer when no
annotation stands. Immutability is per binding: a `let` of a class value still permits `mut`
method calls through it — the REFERENCE is immutable, the object is the object's business.
Deferred initialization is a `var` affair: `var n: int;` may be assigned later (definite
assignment guards the reads, §7.7), while ANY assignment to a `let` — first or otherwise — is
`LYR-SEM0019`. A binding with neither a type nor an initializer is `LYR-SEM0010` — and so is
one whose initializer fixes no type: `null` and `[]` carry none of their own, so
`let x = null;` and `let xs = [];` need an annotation (`let x: ?int = null;`).
Destructuring `let (a, b) = pair;` binds tuple elements — names, `_`, and nested tuple
patterns; no form that can fail, and an initializer is required. `_` names a deliberately
unused binding and silences the unused warning.

## 7.1a Parameters: defaults and `params`

A parameter may carry a default (`fn f(n: int = 0)`), and the LAST parameter may be `params`
with an array type, collecting surplus arguments. Both are **call-site** transformations
resolved against the callee's declaration — which is why a function VALUE has neither: its
type says arity and nothing more.

At the variadic position an argument's own type decides element versus whole array (there is
no `T`/`T[]` conversion, so the two never collide). Since 3.0 a name may carry a variadic and a
non-variadic form at once; the non-variadic one wins wherever both fit, which is rule 4 of
§4.3a. One consequence of the
context propagation of §3.1: an ARRAY LITERAL standing there receives no expectation — the
propagated element type would force the element reading — while every other argument keeps
the element type as its context (which is what names `Opt.Some(1)`'s instance in a
`params Opt<int>[]`).

## 7.2 Loops and `for-in`

`while`, `do-while`, and `for (x in e)` with `break`/`continue`. `for-in` accepts exactly:
a range (`a..b` exclusive, `a..=b` inclusive), an array, a string (yielding `char` code
points), a value satisfying `Iterable<T>` (a fresh cursor per loop), or an `Iterator<T>` value
directly. Iterator conformance reached through an interface chain counts. Anything else is
`LYR-SEM0007`.

Range shapes, exactly: a range with `lo > hi` is empty, `a..a` is empty, `a..=a` is one
element — and `a..=hi` where `hi` is the bound type's MAXIMUM iterates to and including `hi`
and terminates. That last sentence is the contract against the classic desugaring trap
(`..=hi` as `..hi+1`, which wraps): an implementation may desugar however it likes, but the
loop runs `hi - a + 1` times.

## 7.3 `return`, coverage, and lambdas

A non-void function must return or throw on every path (`LYR-SEM0017`); the coverage analysis
is structural (no CFG is specified — a conforming implementation may be smarter, never
laxer... and never stricter on the cases the conformance suite fixes).

Lambdas infer bidirectionally: unannotated parameters take the context function type; an
expression body contributes its type outward. A **block** lambda without annotation or context
infers its return type from its `return` statements, unified like match arms — `return null;`
widens to the optional, disagreeing returns are one error at the lambda, and a non-void
inferred lambda still needs coverage (`LYR-SEM0046`). A valueless block lambda is `void`.

Captures happen **at lambda creation**: a `let` is captured as its value, a `var` as the
variable itself — the enclosing scope and the closure share one cell, and mutations are
visible both ways. (For a `let` the two readings cannot be told apart; the cell is the
observable part.) A lambda without captures allocates no environment.

## 7.4 Flow narrowing

Inside a region where an optional is proven present, its type IS `T`, not `?T`.

**What proves a fact.** Exactly one form: a direct `==`/`!=` comparison between a local or
parameter **identifier** of declared optional type and the `null` literal, in either operand
order. Nothing else narrows — not a field, not an index, not a function call. After
`if (isSome(o))` the type is still `?T`, which is why the standard library deliberately has no
`isSome`.

**Where the fact holds.**

- The matching branch of an `if` statement and of an if-**expression**: `o != null` narrows
  the then-branch, `o == null` the else-branch.
- The body of a `while` — sound because the condition is re-checked before every iteration.
  `do-while` gets nothing: its body runs before the first check.
- The right operand of a short-circuit operator: in `o != null && o > 0` the right side sees
  `o` as `T`; in `o == null || o > 0` likewise — `&&` propagates what the left side proves
  when true, `||` what it proves when false.
- After an `if` whose branch **always exits** — `return`, `throw`, `break`, `continue`, or a
  call to `panic` all end the path — the opposite fact holds for the rest of the enclosing
  block: `if (o == null) { return -1; }` narrows everything after it.

**Composition.** For `a && b` the then-direction collects what BOTH sides prove (the branch
runs only when both are true); the else-direction collects nothing (either side may have
failed). For `||` it is exactly mirrored.

**Invalidation.** An assignment to the variable ends its narrowing from that point on. A
narrowing established by an early exit ends with the enclosing block.

**`match` does not narrow the scrutinee.** A `match` on `?T` with a `null` arm types the
BINDING pattern of the other arms at `T` — `n => n + 1` works; `_ => x + 1` on the original
variable does not. The proof travels through the binding, never back into the matched name.

**Lambdas and staleness.** A lambda body is checked under the narrowing in force at its
creation. A read of a narrowed variable compiles to a **checked unwrap**: if the proof is
stale by the time the body runs — a captured `var` set back to `null` after the lambda was
made — the read panics as `LYR-VM0007`, exactly like `!` on an empty optional. The guarantee
narrowing gives is memory safety, not proof persistence.

## 7.5 `defer`

`defer stmt;` schedules the statement for **the enclosing block's exit**, on every exit path —
falling off the end, `return`, `throw`, `break`, `continue`. Scheduled statements run in
reverse scheduling order, and each EXECUTION of a `defer` statement schedules one run: a
`defer` in a loop body runs once per iteration, at that iteration's end. Two things run no
defers: `std.os.exit`, and a **panic** — a panic aborts, it does not unwind.

In a coroutine the same rule holds against the body's own control flow: a `defer` fires when
the body leaves its scope, which for the outermost scope is the `resume` that drives the body
past its last statement (before the exhaustion panic of a further `resume`). A coroutine
abandoned mid-flight never runs its defers — suspension is not an exit.

## 7.6 `match`

`match` arms carry patterns: `_`; literals (integer, float, string, char, bool, `null`);
bindings; enum variants with nested payload patterns (`Some(x)`, `Point { x }` — a shorthand
field pattern binds the field to its own name and is exempt from the unused-binding warning by
decision); tuple patterns; **or-patterns** (`a | b`); and **range patterns**
(`1..5`, `'a'..='z'`). An arm may carry a guard: `Pattern if expr => …`.

Arms are tried in declaration order and the FIRST match wins — `0 | 1` before `1..5` sends a
`1` to the first arm; an arm made unreachable by an earlier one is not an error. A guard runs
only when its pattern matched, with the pattern's bindings in scope.

Exhaustiveness is checked where the scrutinee is enumerable — enum variants, `bool`, and the
two states of a `?T` — and a gap is an error naming what is missing (`LYR-SEM0050`). Open
types (`int`, `string`, …) require a `_` or binding arm. A guarded arm does not count toward
exhaustiveness.

## 7.7 Definite assignment

A local or parameter must be assigned on every path before every read; a possibly-unassigned
read is `LYR-SEM0018`. The analysis is structural and deliberately conservative — a
conforming implementation may be smarter, never laxer:

- Parameters are assigned. A binding with an initializer is assigned; without one it is
  declared and unassigned — necessarily a `var`, since a `let` cannot be assigned later
  (§7.1). A destructuring binding assigns every bound name (its initializer is mandatory).
- After `if`/`else`, what BOTH branches assign counts; a branch that always returns or throws
  is excluded (the continuation follows the other). An `if` without `else` contributes
  nothing.
- A `while` or `for-in` body may not run: nothing it assigns counts afterwards. A `do-while`
  body runs at least once: its assignments do count. The `for-in` loop variable is assigned
  inside the body.
- A `try` contributes nothing afterwards — the body may have thrown mid-way. The catch
  binding is assigned inside its clause.
- An **exhaustive** `match` statement runs exactly one arm: what ALL continuing arms assign
  (arms that always leave excluded, pattern bindings included) is assigned afterwards. A
  non-exhaustive match contributes nothing.
- A compound assignment (`x += 1`) reads first: on an unassigned variable it is the same
  error.
- A lambda body is analyzed against the assignment state **at its creation site** — a capture
  must be definitely assigned when the lambda is made, and assignments inside the body leak
  nothing out.

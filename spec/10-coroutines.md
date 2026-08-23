# 10. Coroutines

A function whose return type is `Coroutine<T>` is a coroutine: calling it runs NOTHING and
yields a suspended computation; `resume co` runs the body to its next `yield` and produces that
value, of type `T`. State between two yields — locals, loop positions — survives. There is no
other concurrency in the language: a coroutine is a value you drive, not a thread.

Rules:

- `yield e;` is only legal in a coroutine (`LYR-SEM0038`); the value checks against `T`, and
  `Coroutine<void>` yields bare;
- a coroutine ends with a bare `return;` — it cannot return a value (`LYR-SEM0039`). Ending
  early this way is exactly the run-through exit: the next pull sees an exhausted coroutine;
- **`resume` on an exhausted coroutine is a panic**, arriving through
  `std.core.coroutineEnded`. `resume` itself has no `null` protocol: a caller either knows how
  many values exist, drives an infinite coroutine and stops itself, or pulls with `next()`;
- **`co.next()` is the safe form of the same pull** (since 2.2.0): it advances the coroutine
  exactly like `resume` and answers `?T` — the value, or `null` once the body has run to its
  end, and `null` on every call after that. Leniency belongs to the call, not the state:
  `resume` on the same exhausted coroutine still panics. Two yield types change the answer's
  form: a `Coroutine<void>` has no value to wrap, so its `next()` answers `bool` — did it
  advance? — and a `Coroutine<?T>` refuses the form (`LYR-SEM0080`), because `null` would mean
  both "yielded null" and "done". `next` is a built-in member, not a method a type declares —
  the same standing as `length` on an array — and it exists only as a call;
- there is deliberately NO query that answers "done" without pulling: whether another value
  comes is decided by the body running, so such a query cannot be answered without advancing —
  the reason no generator API (Python, JavaScript, C#) has one;
- **a coroutine body may `throw`**, and the exception leaves the `resume` or `next()` that was
  running it, in the frame that drove the pull — an enclosing `try` there catches it like any
  other. `next()` is lenient about EXHAUSTION, not about throwing;
- send values (`resume co, v`) do not exist;
- a lambda is never a coroutine;
- at runtime a `Coroutine<T>` IS a function value that remembers where it left off — which is
  why `resume` behaves as a call. Since 2.2.0 it carries one parameter, the lenient flag
  distinguishing the two pull forms; exhaustion is read back through the compiler-bound
  `std.core.coroutineIsDone` (§4.4, §11).

## Throwability of a pull

Since 3.0 it belongs to the **type**: `Coroutine<int> throws Exception` is a different type from
`Coroutine<int>`, and it stays one through a field, an optional, a parameter and a return.

- A coroutine function's `throws` clause describes the coroutine it returns, not its call:
  `fn gen(): Coroutine<int> throws Exception` produces a `Coroutine<int> throws Exception`. The
  call itself demands nothing, because it runs no body — it builds a suspended frame.
- A **pull** — `resume` or `next()` — of a coroutine whose type throws is a throw site like any
  call to a `throws` function: an enclosing `try` handles it, or the enclosing function declares
  it (`LYR-SEM0034` otherwise). `next()` is lenient about exhaustion, never about throwing.
- Written elsewhere, the throwability is a type suffix (§2): `co: ?Coroutine<int> throws Exception`
  as a field, a parameter, a binding. `throws` without a type means any `Throwable`. The suffix is
  valid on a coroutine type and nowhere else (`LYR-SEM0084`).
- Assignment is one-directional: a coroutine that cannot throw fits where one that may is
  expected, and not the other way round. The refused direction is the one that used to drop the
  demand silently.

*(Before 3.0 the demand was attached to the CALL — the one event that cannot throw — so it
appeared to follow the local variable and vanished at the first indirection, and the exception
left the entry point as `LYR-VM0010`. The three alternatives weighed then and refused: treating
every pull as throwing taxes every ordinary coroutine; refusing a throwing coroutine a field
punishes programs that are already correct; tracking the origin at the pull closes the optional
and not the field. Only the type carries it everywhere.)*

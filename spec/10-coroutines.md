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
- send values (`resume co, v`) do not exist;
- a lambda is never a coroutine;
- at runtime a `Coroutine<T>` IS a function value that remembers where it left off — which is
  why `resume` behaves as a call. Since 2.2.0 it carries one parameter, the lenient flag
  distinguishing the two pull forms; exhaustion is read back through the compiler-bound
  `std.core.coroutineIsDone` (§4.4, §11).

# 10. Coroutines

A function whose return type is `Coroutine<T>` is a coroutine: calling it runs NOTHING and
yields a suspended computation; `resume co` runs to the next `yield` and produces `?T` — the
yielded value, or `null` when the body finished. There is no other concurrency in the language:
a coroutine is a value you drive, not a thread.

Rules:

- `yield e;` is only legal in a coroutine (`LYR-SEM0038`); the value checks against `T`, and
  `Coroutine<void>` yields bare;
- a coroutine ends with a bare `return;` — it cannot return a value (`LYR-SEM0039`);
- resuming a finished coroutine panics (through `std.core.coroutineEnded`);
- a lambda is never a coroutine;
- at runtime a `Coroutine<T>` IS a parameterless function value that remembers where it left
  off — which is why `resume` behaves as a call.

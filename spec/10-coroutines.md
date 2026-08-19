# 10. Coroutines

A function whose return type is `Coroutine<T>` is a coroutine: calling it runs NOTHING and
yields a suspended computation; `resume co` runs the body to its next `yield` and produces that
value, of type `T`. State between two yields — locals, loop positions — survives. There is no
other concurrency in the language: a coroutine is a value you drive, not a thread.

Rules:

- `yield e;` is only legal in a coroutine (`LYR-SEM0038`); the value checks against `T`, and
  `Coroutine<void>` yields bare;
- a coroutine ends with a bare `return;` — it cannot return a value (`LYR-SEM0039`);
- **`resume` on an exhausted coroutine is a panic.** There is no `null` protocol and no
  `hasNext`: a caller either knows how many values exist, or drives an infinite coroutine and
  stops itself. The panic arrives through `std.core.coroutineEnded`;
- send values (`resume co, v`) do not exist;
- a lambda is never a coroutine;
- at runtime a `Coroutine<T>` IS a parameterless function value that remembers where it left
  off — which is why `resume` behaves as a call.

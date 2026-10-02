# Concurrency

> **Skeleton.** Written with milestone **M6** of the Lyric 5 plan, spec-first: each rule lands
> here with its conformance case before or with its implementation. Source of the decisions:
> [06 Concurrency](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md), [01 Runtime L4/L6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md).

## Scope

Coroutines and generators, tasks and `TaskScope`, parking, threads with one scheduler each, channels and synchronization, the memory model.

## 1. Coroutines and generators

1. A function whose declared result is **`Coroutine<Y, R>`** is a coroutine function;
   `Coroutine<Y>` is `Coroutine<Y, void>` (06 A1). A call of it runs nothing of its body: it
   returns a **coroutine**, suspended before the body's first statement and holding the call's
   arguments — a method's receiver among them. A coroutine runs only when it is pulled. A
   coroutine function may be a method and may be generic; an instance is instantiated as any
   generic function is.
2. **`yield v;`** hands `v` to the puller and suspends the body until the next pull; `v` is
   checked against `Y` (`LYR-SEM0001`). `yield;` without a value belongs to a `Coroutine<void>`
   and is refused in any other coroutine (`LYR-SEM0038`). The body's locals live across its
   yields.
3. The body's **`return`** gives the coroutine's **result**: `return v;` checks `v` against `R`
   and is refused where `R` is `void` (`LYR-SEM0039`); a bare `return;` is refused where `R` is
   not `void` (`LYR-SEM0001`). Where `R` is not `void`, every way out of the body returns a
   value (`LYR-SEM0017`) — a body that never ends needs none.
4. **`next()`** runs the coroutine to its next `yield` or to the end of its body and answers
   **`?Y`**: the value the yield handed over, or `null` once the body has ended — on that pull and
   on every pull after it. A `Coroutine<?T>`'s `next()` answers `??T`, so a yielded `null` is told
   apart from the end ([03 §3.1](03-types.md#31-the-type)). A `Coroutine<void>`'s `next()`
   answers **`bool`**: whether the body stopped at a `yield`.
5. **`result()`** answers **`?R`**: what the body returned, `null` until it has returned; a
   coroutine whose `R` is `void` has no `result()` (`LYR-SEM0012`). **`isDone()`** answers whether
   the body has ended, without pulling. Whether a value follows only the body knows, by running:
   there is no `hasNext`.
6. A coroutine function's **`throws`** clause belongs to the coroutine's type —
   `Coroutine<Y, R> throws E` — and so to its pulls, not to the call that makes the coroutine,
   which throws nothing: a `next()` of a throwing coroutine is marked like a call of a throwing
   function ([06 §3](06-errors.md#3-the-try-mark-and-coverage), `LYR-SEM0138`). An error the body
   does not catch ends the body and comes out of the `next()` that ran into it. The coroutine is
   done then: its `result()` stays `null`, and every later `next()` answers `null` and throws
   nothing.
7. A coroutine runs on a stack of its own, on the thread that first pulled it
   ([13 §1.6](13-abi.md#16-coroutines)). Pulling a coroutine that runs — from its own body, or
   from a coroutine it pulled — or one that runs on another thread panics with `LYR-RT0014`. A
   suspended coroutine that nothing references any more is collected with its stack, and nothing
   of its body runs again.
8. `resume` is no word of the language: Lyric 4's `resume co` is `co.next()!`, and `resume` is a
   name like any other.
9. **`close()`** ends a coroutine (06 A5). One that is done, or was never pulled, ends without
   running anything. One suspended at a `yield` of its body is continued to be unwound: that
   `yield` throws **`Cancelled`** — `std.task`'s, an `Error` — so the body's `defer`s and `using`s
   run on the way out ([06 §5](06-errors.md#5-the-error-path)). The `Cancelled` ends at the
   close: `close()` does not throw it on. A body that catches it may still end with a result, but
   a `yield` after it panics with `LYR-RT0014`. What else escapes the body comes out of `close()`,
   which belongs to the coroutine's `throws` clause like its pulls: the `close()` of a throwing
   coroutine is marked (`LYR-SEM0138`). The coroutine is done afterwards; closing a coroutine that
   runs — itself, or one waiting on a coroutine it pulled — panics with `LYR-RT0014`.
10. A coroutine is **`Closeable`**: `using let c = gen();` closes it when the scope is left
    ([06 §7](06-errors.md#7-closing-using)). Unlike another `Closeable` it may also be dropped
    unclosed, without a warning: a suspended coroutine that nothing references any more runs
    nothing more — not its `defer`s either (rule 7) — and the debug profile reports one whose
    body has a `defer` or a `using` when the collector takes it.

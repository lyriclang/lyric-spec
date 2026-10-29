# 10. Concurrency

**Base.** Lyric 5.0 [§10](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/10-concurrency.md) applies, with the deviations below.

**Status.** Tasks and the top level's scope written (S6a), coroutines (S6b1); generator lambdas,
`sequence`, `close()` and `for` over a coroutine (S6b2), cancellation and scopes, channels, `select`
and time, and I/O come with S6b2–S6e — until then the design documents decide.

## Written (S6a, tasks)

1. **Tasks** (Lyric 5 §2; [07 N4, N8](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). `spawn { … }` starts a task of the
   block — a closure without parameters — and gives a `Task<T>`, `T` the block's value. Tasks run
   one at a time, cooperatively: the spawner goes on, and a task runs until it ends, waits for a
   task that is still running, or gives way with `yieldNow()`; the next to run is the one that
   has waited longest. `t.await()` gives the task's value once it has ended; the error it ended
   with is thrown again where it is awaited, any `Error`; a panic in it panics the task that
   awaits it. `t.status()` is a `TaskStatus` of the prelude: `Running`, `Done`, `Failed`,
   `Panicked`, `Cancelled` — so far without the value, the error or the panic's `PanicInfo` that
   Lyric 5 §2 rule 11 gives them; those come with S6c, and `isDone()` (§2 rule 10) with them.
2. **The top level is a task scope** ([07 End](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); Lyric 5 §4 rules 1–2, §5 rule 3). Its
   end — after `fn main` where `main` is the entry — waits until every task of the run has
   ended. The first task to fail, by the order they ended — with an error or a panic alike —
   then ends the run with it: an error exits 1, also where it was awaited and caught; a panic
   101. A task that fails after it is none of the scope's. Until S6c the others are not
   cancelled: they run to their end.
3. Where every task waits for another and none can go on, the run panics (`LYS-RT0018`) — the
   end Lyric 5 §2 rule 12 comes to as well, where the oldest waiting task panics and what awaits
   it panics again.

## Written (S6b1, coroutines)

4. **Coroutines** (Lyric 5 §1 rules 1–5; [07 N2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). A function whose declared result is
   `Coroutine<Y, R>` — `Coroutine<Y>` is `Coroutine<Y, void>` — and whose body has a `yield` of its
   own, outside every lambda in it, or returns no value is a **coroutine function**: a call runs
   nothing of its body and gives a coroutine that holds the call's arguments, its receiver among
   them; one that returns a value is an ordinary function. `yield v` hands `v` to the puller,
   checked against `Y`; a bare `yield` belongs to a `Coroutine<void>` (`LYS-SEM0038`). `return v`
   gives the result, checked against `R` and refused where `R` is `void` (`LYS-SEM0039`); where
   `R` is not `void`, every way out of the body returns (`LYS-SEM0017`). `next()` runs the
   coroutine to its next yield or its end and gives `?Y` — `null` once the body has ended, on
   that pull and every pull after; `bool` for a `Coroutine<void>`, whether it stopped at a
   yield; `??T` for a `Coroutine<?T>`, so a yielded `null` is no end. `result()` gives `?R`,
   `null` until the body has returned, and a `Coroutine<Y>` has none (`LYS-SEM0012`);
   `isDone()` says whether the body has ended. A coroutine function may be generic and a method.
5. An error the body does not catch ends it and comes out of the `next()` that ran into it; the
   coroutine has ended then, with no result. A pull throws any `Error`. A panic in the body
   panics the task that pulls it.
6. A coroutine runs within the task that pulls it, on registers of its own: a wait in its body
   parks that task, and once the task runs again the coroutine goes on where it waited (Lyric 5
   §2 rule 6; [07 N3](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). Pulling a coroutine that runs — from its own body, or from one it
   pulled — panics (`LYS-RT0014`).

## Deviations

- No threads, `Mutex` or `Atomic`; one scheduler per instance; `Semaphore` guards sections across waits ([02 W](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [07](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).
- The top-level code is a `TaskScope` ([07 End](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)): `spawn` starts a task of it, so the
  program does not end before its tasks (Lyric 5 §2 rule 1), and a statement that drops the
  handle does not warn — the scope awaits it (§2 rule 8's `unused-task`).
- `Task<T>` carries no `throws`: `await()` throws any `Error` ([07 N4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); 03: no errors in
  function types). Nor does `Coroutine<Y, R>`: a pull throws any `Error` (Lyric 5 §1 rule 6
  puts the coroutine function's clause on the type).

**Conformance.** `conformance/cases/10-concurrency/` (`since: 1.0.0`).

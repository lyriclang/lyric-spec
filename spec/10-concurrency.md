# 10. Concurrency

**Base.** Lyric 5.0 [§10](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/10-concurrency.md) applies, with the deviations below.

**Status.** Tasks and the top level's scope written (S6a); coroutines, cancellation and scopes,
channels, `select` and time, and I/O come with S6b–S6e — until then the design documents decide.

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

## Deviations

- No threads, `Mutex` or `Atomic`; one scheduler per instance; `Semaphore` guards sections across waits ([02 W](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [07](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).
- The top-level code is a `TaskScope` ([07 End](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)): `spawn` starts a task of it, so the
  program does not end before its tasks (Lyric 5 §2 rule 1), and a statement that drops the
  handle does not warn — the scope awaits it (§2 rule 8's `unused-task`).
- `Task<T>` carries no `throws`: `await()` throws any `Error` ([07 N4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); 03: no errors in
  function types).

**Conformance.** `conformance/cases/10-concurrency/` (`since: 1.0.0`).

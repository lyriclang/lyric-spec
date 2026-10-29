# 10. Concurrency

**Base.** Lyric 5.0 [§10](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/10-concurrency.md) applies, with the deviations below.

**Status.** Tasks and the top level's scope written (S6a), coroutines (S6b1), generator lambdas,
`sequence` and `for` over a coroutine (S6b2), `close()` and a `yield` in a called function (S6b3),
cancellation (S6c1), task scopes (S6c2), a task's status with its values (S6c3), channels and
semaphores (S6d1), `select` (S6d2), time (S6d3), a native that waits (S6e).

## Written (S6a, tasks)

1. **Tasks** (Lyric 5 §2; [07 N4, N8](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). `spawn { … }` starts a task of the
   block — a closure without parameters — and gives a `Task<T>`, `T` the block's value. Tasks run
   one at a time, cooperatively: the spawner goes on, and a task runs until it ends, waits for a
   task that is still running, or gives way with `yieldNow()`; the next to run is the one that
   has waited longest. `t.await()` gives the task's value once it has ended; the error it ended
   with is thrown again where it is awaited, any `Error`; a panic in it panics the task that
   awaits it. `t.status()` says where the task stands, without a wait: a `TaskStatus<T>` of the
   prelude — `Running`; `Done(value)`; `Failed(error)`, an `Error`; `Cancelled`; or
   `Panicked(info)`, a `PanicInfo` with the panic's `code`, `message` and `trace`. It is no
   `Equatable`: a status is matched, not compared (`LYS-SEM0059`). `t.isDone()` says whether the
   task has ended (Lyric 5 §2 rules 10–11, §5 rule 2).
2. **The top level is a task scope** ([07 End](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); Lyric 5 §4 rules 1–2, §5 rule 3). Its
   end — after `fn main` where `main` is the entry — waits until every task of the run has
   ended. The first task to fail, by the order they ended — with an error or a panic alike —
   then ends the run with it: an error exits 1, also where it was awaited and caught; a panic
   101. A task that fails after it is none of the scope's; the first cancels the others
   (rule 12).
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

## Written (S6b2, generators and loops)

7. **Generator lambdas** (Lyric 5 §1 rules 11–12). A lambda whose block has a `yield` of its own is
   a generator lambda: its type is `fn(…) -> Coroutine<Y, R>`, and each call gives a coroutine over
   the call's arguments and the lambda's captures, which runs nothing until it is pulled. The
   lambda's written result type, or the type the place it stands in expects, gives `Y` and `R`;
   without one, the types of the yields unify into `Y` and those of the returns into `R`, or
   `void` where it returns none (`LYS-SEM0016`). Where `R` is not `void`, every path that ends the
   body returns (`LYS-SEM0046`). **`sequence { … }`** is a coroutine of a block that yields, its
   `Y` the place's or the yields', its result none; a block that does not yield is refused
   (`LYS-SEM0001`).
8. **`for` over a coroutine.** `for (x in c)` pulls `c` — evaluated once — until a pull gives
   `null`, binding each value to `x`; `break`, `continue` and a label act as in any loop, and an
   error out of a pull leaves the loop. A `Coroutine<void>` gives nothing to bind
   (`LYS-SEM0007`). *(Informative: `Coroutine :: Iterator`, and `for` over any iterable, come with
   the collections, S7.)*

## Written (S6b3, closing and called yields)

9. **`close()`** (Lyric 5 §1 rules 9–10, 14). A coroutine never pulled, or ended, ends without
   running anything. One parked at a yield runs on from it with that yield throwing `Cancelled`, an
   `Error` of the prelude, so its `defer`s and `using`s run on the way out; the `Cancelled` ends at
   the close. What a `defer` threw on the way out was suppressed into it: `close()` throws the
   first of those, the rest suppressed into it. A body that catches the `Cancelled` may still end
   with a result, and a yield after it panics (`LYS-RT0014`); what else escapes the body comes out
   of `close()`, which throws any `Error`. The coroutine has ended afterwards; closing one that
   runs panics (`LYS-RT0014`). A coroutine is `Closeable` — `using let c = gen()` closes it when
   the scope is left — and, unlike another `Closeable`, may be dropped unclosed without a warning:
   nothing of it runs any more. A coroutine is an `Identity`: `==` asks whether two are one.
10. **A yield in a function a coroutine calls** (§1 rule 13) suspends the coroutine that runs,
    whoever called the function: its value is typed as what it is and meets the coroutine's `Y`
    where it runs — a value of another type, or such a yield where no coroutine runs, panics
    (`LYS-RT0014`). Every yield throws `Cancelled` where its coroutine is closed, so a function with
    a written `throws` covers it (`LYS-SEM0034`).

## Written (S6c1, cancellation)

11. **Cancellation** (Lyric 5 §3 rules 1–3; [07 N9](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). `t.cancel()` marks the task
    cancelled: from then on every wait in it — `await()`, `yieldNow()` — throws `Cancelled`, the
    wait it stands in at once, every later one before it waits, also after one was caught. A task
    that never waits is not cancelled; one that has ended stays as it ended. The `Cancelled`
    unwinds the task as any error does; a task that ends with it is `Cancelled` — its `await()`
    throws it again — and no failure of its scope. A wait in a coroutine the task pulls throws
    there (rule 6). A wait throws `Cancelled`, so a function with a written `throws` that waits
    covers it (`LYS-SEM0034`); the top level covers it itself.
12. **The top level cancels** ([07 End](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); §4 rule 2, §5 rule 3): the first task to fail cancels
    the others, and the end waits for them before it ends the run with that failure.
    **`spawnDetached { … }`** (§2 rule 3) starts a task nobody waits for — the top level's end
    neither — whose block may throw `Cancelled` alone: any other error it handles itself
    (`LYS-SEM0034`). A panic in it ends the run (§5 rule 4).

## Written (S6c2, task scopes)

13. **Task scopes** (Lyric 5 §4, §5 rule 3). `TaskScope.new()` makes a scope; `scope.spawn { … }`
    starts a task of it and gives its `Task<T>`. `close()` waits until every task of the scope has
    ended; the first of them to fail — with an error other than `Cancelled`, or a panic — cancels
    the others, and once they have all ended `close()` throws that error, any `Error`, or panics
    again with that panic. A scope is `Closeable`: under `using let scope = TaskScope.new()` no
    task of it outlives the block. `scope.cancel()` cancels every task of it that has not ended. A
    task cancelled while it waits in `close()` cancels the scope's tasks and still waits for them;
    then `close()` returns or throws as before. A closed scope takes no task: `scope.spawn` after
    `close()` panics (`LYS-RT0008`). A scope is no interface value either (deviations).

## Written (S6d1, channels and semaphores)

14. **Channels** (Lyric 5 §6; [07 N5](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). `Channel<T>.new(capacity)` — `0`, the default, for an
    unbuffered one — carries values from `send` to `recv` in the order they were sent. `send(v)`
    hands `v` to a task waiting in `recv`, or puts it into the buffer while there is room; otherwise
    the sender waits until a receiver takes it. On a closed channel, or when the channel closes
    while it waits, it throws `ChannelClosed`, an `Error` of the prelude. `recv()` gives the next
    value, `?T`: from the buffer — a waiting sender's value then takes the freed place —, or from a
    waiting sender; otherwise the receiver waits for one; `null` once the channel is closed and
    nothing is left in it. `close()` closes it: the tasks waiting in `recv` get `null`, those
    waiting in `send` throw `ChannelClosed`, what is buffered can still be received; closing a
    closed channel does nothing. `send` and `recv` are waits (rule 11). A negative capacity panics
    (`LYS-RT0008`).
15. **Semaphores** (Lyric 5 §10 rule 7; [07 N5](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md): no `Mutex`). `Semaphore.new(n)` holds `n`
    permits — a negative `n` panics (`LYS-RT0008`). `acquire()` takes one, waiting while none is
    left — a wait (rule 11); `tryAcquire()` takes one where one is left and says whether it did;
    `release()` gives one back, to the task that has waited longest; `available()` is the count.
    A value or a permit handed over already belongs to the task a cancel finds waking: the cancel
    acts at its next wait.

## Written (S6d2, select)

16. **Select** (Lyric 5 §7 rules 1–2, 4; [07 N5](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). A select waits on several channels at
    once. It is library — the prelude's source, as Lyric 5's `std.task` writes it: `Select.on(c) { v
    => … }` begins one, a `Selection`, whose `.on(c) { v => … }` adds a case and `.run()` runs it. A
    case receives from its channel: its body gets what `recv()` would give, the value or `null`
    once the channel is closed and empty. `run()` runs the first case, in the order they were
    added, whose channel can be received from without a wait — a value in it, a sender waiting, or
    closed; is there none, the task waits on all of them, and the first channel to get something
    or to close runs its case. One body runs, once. `run()` is a wait (rule 11) and throws what the
    body that runs throws. *(Informative: a select is biased to its first case.)*

## Written (S6d3, time)

17. **Time** (Lyric 5 §2 rule 5, §3 rule 4, §7 rules 3, 5; [07 N5, N9](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). A `Duration` of the
    prelude is a span of whole nanoseconds, made by `Duration.ofNanos`, `ofMicros`, `ofMillis`,
    `ofSecs`, `ofMinutes`, `ofHours` and read by `nanos()`, `millis()`, `secs()`. `sleep(d)` parks
    the task until at least `d` has passed on the run's monotonic clock — a wait (rule 11); the
    sleepers whose time came wake in the order of their deadlines, behind the tasks already ready,
    and a sleep of zero or less lets the ready tasks run first. Where no task is ready, the run
    waits for its earliest timer. `Timer.after(d)` gives a `Channel<void>` that closes once `d` has
    passed: a `recv()` from it answers `null` and a select's case on it runs; the run does not
    wait for a timer. A select's `.timeout(d) { … }` runs its body when no case could go on before
    `d` passed — at once for zero or less. `withTimeout(d) { … }` runs the block as a task of its
    own and gives its value or throws its error, unless `d` passes first: then the block is
    cancelled, and once it has ended `TimedOut` is thrown; whenever it returns, the block has ended,
    and its failure comes out of `withTimeout` alone, no failure of the top level's scope.

## Written (S6e, natives that wait)

18. **A native that waits** ([07 N6](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); Lyric-Script 11 Co) runs on a task of the host while the
    script's task waits, and the other tasks run meanwhile — a task that only gives way does not
    hold it up. `readLine()` of the prelude is the first: the next line of standard input without
    its line end, `null` at its end; an error reading the input ends it as well, until `std.io`
    brings `IoError` (S7). A read is a wait (rule 11): a cancel ends it, and a line its reader
    brings after the cancel is dropped.

## Not yet written

- `Coroutine :: Iterator` and a `for` over any iterable, signals as a channel (Lyric 5 §12; the
  right `os`), and `IoError` for `readLine`: with the std core (S7). A host's waits — `call`,
  `start`, `step` — and the instance's halt on its budget with its tasks: with the embedding (S8).

## Deviations

- No threads, pools, `Mutex`, `RwLock`, `Once` or atomics (Lyric 5 §8–§11); one scheduler per
  instance; `Semaphore` guards sections across waits ([02 W](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [07](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).
- The top-level code is a `TaskScope` ([07 End](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)): `spawn` starts a task of it, so the
  program does not end before its tasks (Lyric 5 §2 rule 1), and a statement that drops the
  handle does not warn — the scope awaits it (§2 rule 8's `unused-task`).
- `Task<T>` carries no `throws`: `await()` throws any `Error` ([07 N4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); 03: no errors in
  function types). Nor does `Coroutine<Y, R>`: a pull throws any `Error` (Lyric 5 §1 rule 6
  puts the coroutine function's clause on the type).
- A task, a coroutine, a task scope, a channel or a semaphore is no interface value — not of `Closeable`, not of `Any` — until they
  have descriptors at run time, with the collections (S7); `using` and `==` take them as they are.

**Conformance.** `conformance/cases/10-concurrency/` (`since: 1.0.0`).

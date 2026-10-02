# Concurrency

> **Skeleton.** Written with milestone **M6** of the Lyric 5 plan, spec-first: each rule lands
> here with its conformance case before or with its implementation. Source of the decisions:
> [06 Concurrency](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md), [01 Runtime L4/L6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md).

## Scope

Coroutines and generators, tasks and `TaskScope`, parking, threads with one scheduler each, channels, select and timers, synchronization, the memory model.

## 1. Coroutines and generators

1. A function whose declared result is **`Coroutine<Y, R>`** and whose body has a `yield` of its
   own — one outside every lambda in it — is a **coroutine function** (08 D11);
   `Coroutine<Y>` is `Coroutine<Y, void>` (06 A1). A call of it runs nothing of its body: it
   returns a **coroutine**, suspended before the body's first statement and holding the call's
   arguments — a method's receiver among them. A coroutine runs only when it is pulled. A
   coroutine function may be a method and may be generic; an instance is instantiated as any
   generic function is. A function that returns a coroutine without yielding is an ordinary
   function: it returns a coroutine value as it returns any value.
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
11. A lambda whose body has a `yield` of its own is a **generator lambda** (08 F5): its type is
    `fn(…) -> Coroutine<Y, R>`, and calling it makes a coroutine over its arguments and its
    captures that runs nothing until it is pulled (rule 1). A context that expects a coroutine —
    the lambda's written result type, or the type of the place it is passed to — gives `Y` and `R`
    and checks the yields and the returns against them (`LYR-SEM0001`); without one, the types of
    the yields unify into `Y` (`LYR-SEM0016`), and those of the returns into `R`, or `void` where it
    returns none. A generator lambda whose `R` is not `void` returns on every path that ends its
    body (`LYR-SEM0046`). What its body throws belongs to its coroutine's pulls, as a coroutine
    function's clause does (rule 6): the set it writes, the one its context expects, or what
    escapes its body. A yield in a lambda nested in it belongs to that lambda.
12. **`sequence { … }`** (08 Y11) is `std.core`'s `fn sequence<T>(body: fn() -> Coroutine<T>):
    Coroutine<T>`, called with a trailing generator lambda — no syntax of its own.
13. A `yield` outside a coroutine's own body — in a function a coroutine calls (06 §10a) —
    suspends the coroutine that runs, whoever called the function. Its value is typed as what it is
    and meets that coroutine's `Y` at run time: a value of another type panics with `LYR-RT0014`,
    as does such a yield where no generator runs — on a thread's own stack, or in a task (§2). It
    throws `Cancelled` at `close()` as a body's
    yield does (rule 9), so its function covers it — `throws Cancelled`, or a clause
    (`LYR-SEM0034`) — and a coroutine's body covers it for the functions it calls, as it does for
    its own yields. A yield in a lambda is not of this kind: it makes the lambda a generator
    (rule 11).

## 2. Tasks

A **task** is a body that the scheduler of its thread runs on a stack of its own
([06 N3–N6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md)). Unlike a generator it yields nothing: it **waits**. A wait parks
the task at its thread's scheduler wherever it stands ([13 §1.6](13-abi.md) rule 7), and the
scheduler runs another task meanwhile. The functions this section names are `std.task`'s.

1. **`main` is a task**, on the main thread's scheduler (06 T6). The program ends when `main`'s
   body returns: the tasks still ready or asleep then never run again, and none of their
   `defer`s runs. *(Informative: a program that never waits runs `main` on the thread's own
   stack; it cannot tell the difference.)*
2. A thread runs one of its tasks at a time, each until it waits (06 N8): the code between two
   waits runs with no other task of its thread in between. The tasks that are ready run in the
   order they became ready.
3. **`spawnDetached(body)`** makes `body` a task of the running thread, ready behind the tasks
   ready before it (06 T5). Nobody waits for it, and nothing it throws reaches anyone: its type,
   `fn() -> void throws Cancelled`, lets only a cancellation end it early, so it handles every
   other error itself (`LYR-SEM0034`).
4. **`yieldNow()`** puts the running task behind the tasks that are ready: they run before it
   goes on (06 N8).
5. **`sleep(d)`** parks the running task until at least `d` has passed on the monotonic clock
   (06 K3; [13 §1.6](13-abi.md) rule 8). `d` is a `std.time.Duration`, a span of whole
   nanoseconds (10 Q1). The sleepers whose time came wake in the order of their deadlines — of
   one deadline, in the order they fell asleep — behind the tasks already ready. A sleep of
   zero or less lets the ready tasks run first.
6. A wait parks the whole task, also from within a generator the task pulls: once the task runs
   again, the generator goes on where it waited and yields to its puller as before.
7. The waits — `sleep`, `yieldNow`, `await` — **throw `Cancelled`** where their task is
   cancelled (06 N9 X1): a function that waits covers it, with `throws Cancelled` or a clause
   (`LYR-SEM0034`).
8. **`spawn(body)`** makes `body` a task of the running thread, ready behind the tasks ready
   before it, and gives its **handle**, a `Task<T> throws E` (06 T1): `T` is what the body
   returns — `void` too ([03 §9.1](03-types.md) rule 7) — and `E` what it throws. The handle's
   type carries the error as a coroutine's carries what its pulls throw (05 E10); `Task<T>`
   throws nothing, and fits where a `Task<T> throws E` is expected, but not the reverse
   (`LYR-SEM0001`). `throws` after any other type than a coroutine or a task is refused
   (`LYR-SEM0084`), and after a function's return type it is the function's own: a function
   that returns a throwing task writes `(Task<T> throws E)`.
9. **`task.await()`** waits until the body has ended (06 T2) and gives its value, or throws its
   error: it throws what the handle's type says and, as every wait, `Cancelled` — marked and
   covered as any call that throws (`LYR-SEM0138`, `LYR-SEM0034`). The tasks waiting for one
   task run again in the order they began to wait.
10. **`task.isDone()`** says whether the body has ended, with its value or its error (06 T3).
11. **`task.status()`** says where the task stands, without waiting (06 T3): a `TaskStatus<T>` —
    `Running`; `Done(value)`; `Failed(error)`, the error an `Error`; `Cancelled`, when it ended
    with `Cancelled`; or `Panicked(info)` (§5), `info` a `PanicInfo` with the panic's `code`,
    `message` and `trace`.

## 3. Cancellation

A task is cancelled cooperatively ([06 N9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md)): a cancel marks it, and its waits
throw.

1. **`task.cancel()`** marks the task cancelled (X1). From then on every wait in it throws
   `Cancelled`: the wait it is in ends at once, and every later wait throws before it waits (X5)
   — a task that catches `Cancelled` and waits again gets it again. A task that never waits is
   not cancelled (X2); a task that has ended stays as it ended.
2. `Cancelled` unwinds the task as any error does — its `defer`s and `using`s run — and the task
   ends with it unless its body catches it; `await()` on the handle then throws `Cancelled` (X1).
3. A wait inside a generator the task pulls throws there: the generator unwinds and ends, its
   pull answers that it has ended, and the task's next wait throws `Cancelled` in turn.
4. **`withTimeout(d, body)`** (X4) runs `body` as a task of its own and gives its value or throws
   its error — unless `d` passes first: then the body is cancelled, and once it has ended,
   `TimedOut` is thrown. It throws what the body throws, `TimedOut` and `Cancelled`
   (`LYR-SEM0034`). Whenever it returns, the body has ended: a cancel of the caller cancels the
   body, and waits for it.

## 4. Task scopes

The tasks of a scope end before the scope does ([06 T5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md)): structured
concurrency.

1. A **`TaskScope`**, made by `TaskScope.new()`, starts tasks with **`scope.spawn(body)`** — a
   `spawn` (§2 rule 8) whose task belongs to the scope. A scope is `Closeable`
   ([06 §7](06-errors.md)): its `close()` waits until every task of the scope has ended, so
   under `using let scope = TaskScope.new();` no task of it outlives the block.
2. The first task of the scope that ends with an error other than `Cancelled` cancels the scope's
   other tasks (06 N9 X3), and `close()` throws that error once they have all ended; a task that
   ends with `Cancelled` is no failure of the scope. What `close()` throws is an `Error`, as
   `Closeable` says (`LYR-SEM0034`).
3. **`scope.cancel()`** cancels every task of the scope that has not ended.
4. A task cancelled while it waits in `close()` cancels the scope's tasks and still waits for
   them to end; then `close()` returns or throws as before.

## 5. Panics in tasks

A panic leaves the coroutine it happens in, without unwinding ([05 E8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/05-fehler.md);
[13 §1.6](13-abi.md) rule 10), and the task it belongs to takes it ([06 T4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md)).

1. A panic in a task started by `spawn` — a scope's included — ends that task, not the program:
   the task is **panicked**, nothing more of it runs — no `defer`, no `using` — and the tasks
   waiting for it run again. A panic in a generator the task pulls passes to the task.
2. `await()` on a panicked task panics again, with the panic's code, message and frames: a panic
   stays a bug. `status()` (§2 rule 11) looks without panicking.
3. A task of a scope that panics cancels the scope's other tasks, as a failure does (§4 rule 2),
   and `close()` panics again with it once they have all ended.
4. A panic in `main`, or in a task started by `spawnDetached` — which nobody can look at — ends
   the program with its report ([13 §1.4](13-abi.md)).

## 6. Channels

A channel carries values from one task to another ([06 N5 K1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md)).

1. A **`Channel<T>`**, made by `Channel<T>.new(capacity)` — `0`, the default, for an unbuffered
   one — carries values from `send` to `recv`, in the order they were sent.
2. **`send(value)`** hands the value to a task waiting in `recv`, or puts it into the buffer while
   there is room; otherwise the sending task waits until a receiver takes it. On a closed channel,
   or when the channel closes while it waits, it throws `ChannelClosed`.
3. **`recv()`** gives the next value: from the buffer — where the value of a waiting sender then
   takes the freed place — or from a task waiting in `send`; otherwise the receiving task waits
   for one. It answers `null` once the channel is closed and nothing is left in it.
4. **`close()`** closes the channel: the tasks waiting in `recv` get `null`, those waiting in
   `send` throw `ChannelClosed`, and what is buffered can still be received. Closing a closed
   channel does nothing.
5. `send` and `recv` are waits: in a cancelled task they throw `Cancelled`, and a cancel ends them
   (§3).

## 7. Select and timers

A select waits on several channels at once and goes on with the first that has something
([06 N5 K2–K3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md)). It is library, no statement: `std.task`'s `Select.on(c) { … }`
begins one, a `Selection`, whose `.on(c) { … }` adds a case, `.timeout(d) { … }` a timeout, and
`.run()` runs it. The bodies are trailing lambdas ([03 §8.2](03-types.md)) or any function
values of their types.

1. A **case** `on(c, body)` receives from the channel `c`: `body`, a `fn(?T) -> void throws
   Error` for a `Channel<T>`, gets what `recv()` would give (§6 rule 3) — the value, or `null`
   once `c` is closed and nothing is left in it.
2. **`run()`** runs the first case, in the order they were added, whose channel has a value or
   is closed: a receive from it would not wait. Is there none, the running task waits on all of
   them, and the first channel to get a value or to close runs its case. One body runs, once,
   and only its case receives: the other channels keep what they get for later receives.
3. **`timeout(d, body)`** (K3): `body` runs when no case could go on before `d` passed. A `d` of
   zero or less runs it at once where no case can go on at once.
4. `run()` is a wait: in a cancelled task it throws `Cancelled`, and a cancel ends it (§3). It
   throws what the body that runs throws; its type says `Error`, which its caller covers
   (`LYR-SEM0034`).
5. **`Timer.after(d)`** gives a `Channel<void>` that fires once, when `d` has passed: then it
   closes, so a `recv()` from it answers `null` and a case on it runs. The program does not wait
   for a timer (§2 rule 1).

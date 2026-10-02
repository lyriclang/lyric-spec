# ABI and embedding

> **Partly written.** §1 was written with milestone **M1** of the Lyric 5 plan, §1.6 and §1.7 with **M6**; the rest comes
> with **M14**, spec-first: each rule lands here with its conformance case before or with its
> implementation. Source of the decisions:
> [01 Runtime](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md), [11 Tooling and interop W4/W5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md).

## Scope

The C ABI as the one foreign boundary: the type table, `@Layout(C)`, pointers, callbacks, exports, and the embedding API (`lyr_init`, exports as tasks, `LyrStatus`). Replaces the 4.x bytecode chapter.

## 1. The runtime contract, stage 0

What compiled code and the runtime agree on, whatever collector sits behind the runtime. The
collector is staged ([01 L1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)):
a later stage replaces the one before without changing this section. The C declarations are the
runtime's headers, `runtime/include/lyr/` in the toolchain repository.

**Conformance.** Until compiled Lyric code can observe these rules (M2), the runtime's own test
programs are their conformance: `runtime/tests/` in the toolchain repository, run for every
Tier 1 target by `tests/Lyric5.Tests`.

### 1.1 Objects

1. Every heap object begins with one pointer-sized word, its **header**: the address of the
   object's type descriptor. Two objects have the same type exactly when their headers are equal.
2. A **type descriptor** is static and never changes. It gives:
   - `size` — the bytes of a fixed-size object, header included; for a string or an array, the
     bytes before its first element;
   - `flags` — `HAS_REFS` (some word of the object, or of an element, is a reference), `ARRAY`,
     `STRING`;
   - `elem_size` — for an array, the bytes of one element;
   - `refmap` — a bit set: bit *i* set means word *i* is a reference. For a fixed-size object the
     words are the object's own, word 0 being the header, whose bit is always clear; for an
     array they are the words of one element;
   - `name` — the type's qualified name, `module.Type`;
   - the interface tables ([05](05-interfaces.md)).
3. An object whose descriptor lacks `HAS_REFS` holds no reference. The collector may skip it.
4. Allocation yields memory set to zero with the header in place. It never yields a null
   pointer: when no memory is left — including beyond a configured heap limit (§1.5) — the
   allocation panics with `LYR-RT0005` (§1.4).
5. Compiled code stores every reference into a heap object through the runtime's write barrier
   (`LYR_WRITE_BARRIER`), from the first stage on, whatever the barrier does in the current stage.

### 1.2 Strings

A string is an object of this layout:

| Offset | Size | Content |
|---|---|---|
| 0 | 8 | header |
| 8 | 8 | the length in bytes, a signed 64-bit integer, never negative |
| 16 | length + 1 | the bytes (UTF-8), then one NUL byte that the length does not count |

A string never changes after it is built. The trailing NUL lets a string reach C as a
`const char *` without a copy.

### 1.3 Arrays

An array is an object of this layout:

| Offset | Size | Content |
|---|---|---|
| 0 | 8 | header |
| 8 | 8 | the number of elements, a signed 64-bit integer, never negative |
| 16 | count × `elem_size` | the elements, inline and contiguous |

The first element sits at offset 16, aligned to 16 bytes.

### 1.4 Panics and crashes

1. A **panic** ([05 E8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/05-fehler.md))
   writes a report to the error output and ends the process with exit code **101**. No `defer`
   and no `using` runs.
2. The report's first line is `panic [CODE]: message`. The lines after it are the frames of the
   panicking thread, innermost first, each starting with `    at ` (four spaces). A frame names
   its function and, where the debug information has it, its source position:
   `    at function (file:line)`. The runtime's own frames on the way to the report are not shown,
   and neither is anything below the program's entry. *(Informative: consecutive equal frames are
   shown once, followed by `    ... the frame above repeats N more times`; a trace cut at its depth
   limit ends with `    ... deeper frames not shown`.)*
3. A panic on any thread ends the whole process, with one report. A panic on another thread
   meanwhile waits for that end and writes nothing. A second panic on the panicking thread
   itself — while its report is written or the hook runs (item 5) — ends the process at once
   with the line `panic while panicking [CODE]: message`, still with 101.
4. The runtime's panic codes:

   | Code | Cause |
   |---|---|
   | `LYR-RT0001` | integer division by zero |
   | `LYR-RT0002` | integer overflow, including `MIN / -1`, `MIN % -1` and a shift by a count the type cannot take ([03 §1.6](03-types.md)) |
   | `LYR-RT0003` | an index outside its sequence |
   | `LYR-RT0004` | unwrapping a null value |
   | `LYR-RT0005` | no memory left, or the heap limit reached |
   | `LYR-RT0006` | stack overflow |
   | `LYR-RT0007` | a precondition of a runtime operation stated by the program text (a negative length) |
   | `LYR-RT0008` | `panic(message)`: the program's own message, as written |
   | `LYR-RT0009` | `as char` of a value that is no Unicode scalar value ([03 §1.4](03-types.md)) |
   | `LYR-RT0010` | `try!` on an error: `'try!' on an error: <message>` ([06 §6](06-errors.md#6-the-expression-forms)) |
   | `LYR-RT0011` | `assert(condition, message)` with a false condition: the message as given ([06 §9](06-errors.md#9-panics-and-never)) |
   | `LYR-RT0012` | `unreachable(message)` reached: the message as given |
   | `LYR-RT0013` | `todo(message)` reached: the message as given |
   | `LYR-RT0014` | a coroutine resumed while it runs, after its body returned or on a thread other than its own; a yield or a park with no coroutine running; a yield of another type than the running coroutine yields ([10 §1.13](10-concurrency.md)); a yield while the coroutine is being closed; a close of one that runs or is parked (§1.6) |
   | `LYR-RT0015` | the system refused the runtime what it needs to go on: a poller, or a wait on one (§1.7) |

5. A host may set one **panic hook**. It is called once per process, after the report is
   written, on the panicking thread, with the code, the message and the frames as written. It
   cannot prevent the end: when it returns, the process exits with 101.
6. A **crash** is not a panic: an invalid memory access, an illegal instruction, an arithmetic
   fault or an abort. When the runtime installed its handlers (§1.5), it writes `crash: ` and a
   description, then the frames from the faulting one outward, in the form of item 2; then the
   process ends the way the operating system ends it for that fault — not with 101.
7. A stack overflow is a panic (`LYR-RT0006`), not a crash.

### 1.5 Program start and end

1. A standalone program starts the runtime with its defaults, which install the handlers of
   §1.4 item 6. Its exit code is the value `main` returns, masked to `0..255`
   ([11 C5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).
2. A host starts the runtime itself (`lyr_init`), once per process: a second start is refused and
   changes nothing. The host chooses the program's arguments, a heap limit (0: none), whether the
   runtime installs its fault handlers (a host owns its signals, so an embedding host says no),
   and where the runtime's standard and error output go.

### 1.6 Coroutines

A coroutine runs a body on a stack of its own
([01 L4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[06 N2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md)). The
runtime gives the primitives only — create, resume, yield, park, close, status, the running
coroutine (`lyr/coro.h`); generators, tasks and channels are built on them
([10](10-concurrency.md)).

1. A coroutine is created around a body and an argument, and does not run until it is first
   **resumed**. A resume runs it until it **yields** or its body returns; then the resumer goes
   on. A yield goes back to the coroutine's resumer — the thread's own stack, or the coroutine
   that resumed it — and nowhere else (asymmetric), and nothing interrupts a coroutine between a
   resume and its next yield (cooperative).
2. A coroutine's stack is reserved at its first resume — 256 KiB unless its creation says
   otherwise — and costs memory only as its pages are reached. A guard page below it makes
   running out of it a stack overflow (`LYR-RT0006`), as on a thread's stack.
3. A coroutine runs on the thread that first resumed it, and only there.
4. A coroutine is an object. While it is suspended, what its frames hold lives as long as the
   coroutine: one that nothing references any more is collected with its stack, and nothing on
   that stack runs again — no `defer`, no `using`.
5. Resuming a coroutine that runs — itself, or one that waits for a coroutine it resumed — or one
   whose body returned, or one that runs on another thread, and yielding where no coroutine runs,
   is a panic (`LYR-RT0014`).
6. C frames may lie on a coroutine's stack between a resume and a yield — a callback from C that
   yields ([01 K4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)).
   The runtime counts them for each coroutine: a stack with C frames on it cannot be unwound.
7. A **park** stops the coroutine that runs where it stands and hands control back to the thread's
   own stack — where a scheduler runs — past every coroutine between
   ([06 N3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md)):
   the outermost coroutine of the chain, the one resumed from there, is **parked**, and those in
   between go on waiting for the ones they resumed. Resuming the parked one continues the
   coroutine that parked, where it parked; when that one yields, it yields to its own resumer,
   as before. A park where no coroutine runs, and a close of a parked coroutine, is a panic
   (`LYR-RT0014`).
8. The runtime has a **monotonic clock**: nanoseconds that only move forward, from an unspecified
   start — for intervals and deadlines, not for the time of day.

### 1.7 Waiting

A thread's scheduler waits on the thread's **poller**
([06 N6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md)) —
blocking the thread until another thread wakes it or a deadline passes (`lyr/poll.h`).

1. Every thread has one poller, made when it is first asked for. A **wait** on it blocks the
   thread until the poller is woken or the wait's timeout passes; a timeout of zero asks without
   blocking, and a wait may have no timeout at all.
2. Any thread may **wake** a poller. A wake while no wait runs is kept for the next wait, which
   returns at once; the wakes before one wait count as one.
3. A wait never ends early: its timeout runs on the monotonic clock (§1.6 item 8), and a signal
   that interrupts it — the collector's, which stops threads with signals on some platforms —
   does not end it.
4. A poller the system refuses — no descriptors left, say — or a wait the system fails is a
   panic (`LYR-RT0015`).

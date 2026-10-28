# ABI and embedding

> **Partly written.** §1 was written with milestone **M1** of the Lyric 5 plan, §1.6 and §1.7 with **M6**, §2 with **M7**, §3 with **M14**; the rest comes
> with **M14**, spec-first: each rule lands here with its conformance case before or with its
> implementation. Source of the decisions:
> [01 Runtime](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md), [11 Tooling and interop W4/W5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md).

## Scope

The C ABI as the one foreign boundary: the type table, `@Layout(C)`, pointers, callbacks, exports, the embedding API (`lyr_init`, exports as tasks, `LyrStatus`), and libraries loaded while a program runs. Replaces the 4.x bytecode chapter.

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
   writes a report to the error output and ends the process with exit code **101** — unless it
   happens in a coroutine, which it leaves (§1.6 rule 10). No `defer` and no `using` runs.
2. The report's first line is `panic [CODE]: message`. The lines after it are the frames of the
   panicking thread, innermost first, each starting with `    at ` (four spaces). A frame names
   its function and, where the debug information has it, its source position:
   `    at function (file:line)`. In the release profile a frame may be missing: that of a function
   inlined into its caller, and that of a function whose last act is a call, which hands its frame
   to the callee; the debug profile shows every frame (design 01, review 2026-10-07). The
   program's frames are those of its text, whatever its packages and modules are called; the
   runtime's own frames on the way to the report — the function that raised it among them — are
   not shown,
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
   | `LYR-RT0011` | `assert(condition, message)` with a false condition: `assertion failed: `, the condition as written, then the message where one is given ([06 §9](06-errors.md#9-panics-and-never)) |
   | `LYR-RT0012` | `unreachable(message)` reached: `unreachable`, then the message where one is given |
   | `LYR-RT0013` | `todo(message)` reached: `not implemented`, then the message where one is given |
   | `LYR-RT0014` | a close of a coroutine with C frames on its stack (§1.6 rule 6); a coroutine resumed while it runs, after its body returned or on a thread other than its own; a yield or a park with no coroutine running; a yield of another type than the running coroutine yields ([10 §1.13](10-concurrency.md)), or in a task where no generator runs; a yield while the coroutine is being closed; a close of one that runs or is parked (§1.6) |
   | `LYR-RT0015` | the system refused the runtime what it needs to go on: a poller, or a wait on one (§1.7); random bytes ([12](12-stdlib.md)) |
   | `LYR-RT0016` | a collection of the library changed while it was walked: `List: changed while it was walked` — a list, a map, a set, a deque ([12](12-stdlib.md)) |
   | `LYR-RT0017` | control reached a place the implementation holds unreachable — behind a call that does not return, behind a `match` that covers every case. No program causes it: it is a defect of the implementation, reported instead of acted on. A build that optimizes may end as a crash there instead (item 6): at once, and never by going on |
   | `LYR-RT0018` | every task of a thread waits, none sleeps, and no other thread lives that could wake one: `deadlock: every task waits, and nothing can wake one`, raised in one of the waiting tasks ([10 §2](10-concurrency.md) rule 12) |
   | `LYR-RT0019` | `lock`, `read`, `write` or `run` on a lock a task panicked while it held: `lock poisoned by a panic: <code>: <message>`, the first panic named ([10 §10](10-concurrency.md) rule 6) |
   | `LYR-RT0021` | a C function returned, for an enum with `@Layout`, an integer no variant stands for: `C returned <n>, which is no variant of <enum> (it has <count>)` (§3 rule 5) |
   | `LYR-RT0023` | a `GcHandle` read as a handle of another class than its object's, or of none (§3 rule 12) |
   | `LYR-RT0022` | C called a Lyric function through its pointer on a thread Lyric does not run: `C called a Lyric function on a thread Lyric does not run …` — but for a Callback's that returns nothing, which goes to its thread (§3 rules 9, 13); or an export before the runtime started: `C called an export before lyr_init started the runtime` (§4 rule 6) |

5. A host may set one **panic hook**. It is called once per process, after the report is
   written, on the panicking thread, with the code, the message and the frames as written. It
   cannot prevent the end: when it returns, the process exits with 101.
6. A **crash** is not a panic: an invalid memory access, an illegal instruction, a trap, an
   arithmetic fault or an abort. When the runtime installed its handlers (§1.5), it writes `crash: ` and a
   description, then the frames from the faulting one outward, in the form of item 2; then the
   process ends the way the operating system ends it for that fault — not with 101.
7. A stack overflow is a panic (`LYR-RT0006`), not a crash. A compiled function finds it at its
   entry, before it writes its frame: below the stack's end it keeps a reserve the panic runs in
   ([01 S3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)). In a
   coroutine the panic leaves it as any panic does (§1.6 rule 10) — a task that overflows ends
   alone —, and what the output holds is written before the report, as for any panic. A guard
   page below each stack is the net under frames that do not check — the runtime's own and
   foreign code —: running into it ends the process with the same report.

### 1.5 Program start and end

1. A standalone program starts the runtime with its defaults, which install the handlers of
   §1.4 item 6. Its exit code is the value `main` returns, masked to `0..255`
   ([11 C5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).
2. A host starts the runtime itself (`lyr_init`, §5 rule 1), once per process: a second start is
   refused and changes nothing. The host chooses the program's arguments, a heap limit (0: none), whether the
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
2. A coroutine's stack is reserved at its first resume — 256 KiB in the release profile and
   2 MiB in the others, whose unoptimized frames are some four times as large, unless its
   creation says otherwise (the sweep after M10, W5) — and costs memory only as its pages are
   reached. Running out of it is a stack overflow (`LYR-RT0006`, §1.4 item 7), as on a thread's
   stack.
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
   Closing such a coroutine is a panic (`LYR-RT0014`); one that nothing references any more is not
   collected — its stack stays, as C may still point into it, and the runtime says so once on the
   error output — and nothing on it runs again.
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
9. A **task's context** ([10 §2](10-concurrency.md)) is a coroutine around a function value
   `fn() -> void`, called with its environment and no error slot. Nothing yields to its resumer:
   a yield in it, outside every generator, is a panic (`LYR-RT0014`). Where `main` is a task,
   the program's start makes main's context — on a stack of 8 MiB — and hands it to the
   scheduler of `std.task`, which runs until that context is done; the exit code is main's
   value as before (§1.5).
10. A panic in a coroutine **leaves** it ([05 E8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/05-fehler.md)):
    nothing on its stack runs again — no `defer`, no `using` — and its resumer finds it
    **panicked**, with the report: the code, the message, and the frames where the panic
    happened. A resume passes the panic on: the resumer panics again, with that report — so a
    panic climbs the coroutines that resumed one another until a task's scheduler takes it
    ([10 §5](10-concurrency.md)), or until it reaches a thread's own stack and ends the process
    with the report (§1.4). A coroutine with foreign frames on its stack (rule 6), and a panic
    for want of memory (`LYR-RT0005`), end the process at once.

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

## 2. C functions, stage 1

A C function the program calls, declared in Lyric and found by the linker in a package's native
part ([15 §5](15-project.md)) or a library ([11 W4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)). Stage 1 carries the
scalars C has as they are; pointers, strings, structs and enums are the type table's second
stage (§3); callbacks and exports come later (M14).

**Conformance.** `conformance/cases/13-abi/`, package cases with a native part; the toolchain's
own tests (`tests/Lyric5.Tests`, `NativeTests`).

1. `extern "C" fn add(a: int, b: int): int;` declares the C function `add`; `= "c_add"` after the
   signature names its symbol instead, a C identifier (`LYR-SEM0099` for another). The ABI is
   `"C"`, the one foreign boundary there is (`LYR-SEM0099` for another). The declaration has no
   body, no type parameters and no `throws` — a C function throws nothing (`LYR-SEM0099`).
2. What crosses: `int8` to `int64` and `uint8` to `uint64` as the C integer of their width,
   `int`/`uint` as the 64-bit ones; `float32` as `float`, `float` as `double`; `bool` as C's
   `bool`, 0 or 1; `char` as `uint32_t`, its scalar value; and `void` as a return. Each by value:
   a place parameter (`&x: T`, [03 §2.3a](03-types.md)) is an address and does not cross. What
   §3 adds crosses too; every other type is refused, as a parameter and as a result
   (`LYR-SEM0099`). *(Informative: the standard library calls its runtime the same way, by
   `extern "C"`; its declarations alone also pass the runtime's own objects — a `string`, an
   array, an object of a class, a coroutine, or the optional of one — as the runtime's pointers,
   since the runtime is the one C that knows them. The table of what crosses is the same check
   with that row more.)*
3. A call is a direct call in the target platform's C ABI. A symbol nothing defines fails the link
   (exit 2, [14 §1.3](14-cli.md)). The program's own declaration is the one it calls by: a header
   of the system's that declares the same function with other types does not meet it.
4. `extern "C" { fn …; fn …; }` declares the functions of one ABI together: each is the
   declaration it would be alone, with its symbol and its `;`. A visibility word before `extern`
   is that of each function inside without its own. An attribute stands on a function inside,
   not on the block (`LYR-PAR0042`); a block without a function is refused (`LYR-PAR0032`).

## 3. The type table, stage 2

What crosses into C beside the scalars of §2: pointers, C's strings, structs by value and enums
as integers ([11 X2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).
The pointer types are `std.ffi`'s; `@Layout` is a compiler instruction of the prelude
([11 §1](11-metaprogramming.md) rule 16).

**Conformance.** `conformance/cases/13-abi/`; the toolchain's own tests (`NativeTests`).

1. **`Ptr<T>`** is an address C gave, never null: C's `T *`. Lyric does not read or write through
   it here, and makes none of its own; `T` says what it points at, which C alone holds to.
   **`?Ptr<T>`** is a pointer that may be null: `null` crosses as C's null, and a null pointer C
   returns comes back as `null`.
2. **`CStr`** is C's `const char *`: bytes up to a NUL, which C owns. Its `length()` counts the
   bytes before the NUL; its `toString()` copies them into a `string`, and throws `Utf8Error`
   where they are no well-formed UTF-8. **`?CStr`** may be null, as `?Ptr<T>`.
3. A `string` argument where a C function's parameter is `CStr` — or `?CStr`, which a string
   never leaves null — crosses as the string's bytes, with the NUL every string holds (§1.2),
   without a copy. They are C's for the call: C does not
   keep the address past its return.
4. A struct with **`@Layout(C)`** is laid out as C lays out a struct of the same fields in the same
   order on the target platform, and crosses by value, as a parameter and as a result. Its fields
   are what C holds: the scalars of §2, `char`, `Ptr<T>`, `CStr`, another `@Layout(C)` struct, and an
   inline array `T[N]` of one of them. A field of another type — an optional, an enum, a string —
   is refused (`LYR-SEM0099`). A struct without `@Layout(C)` is the compiler's to lay out and does
   not cross (`LYR-SEM0099`).
5. An enum with **`@Layout(C)`** is C's `enum`, an `int`; with **`@Layout(uint8)`** — or any other
   integer type of §2 — it is that integer. Its variants carry no payload (`LYR-SEM0099`). The
   first variant written is 0, the next 1, in the order they are written, and the count must fit
   the integer (`LYR-SEM0099`). It crosses as a parameter and as a result; an integer C returns that
   no variant stands for is a panic (`LYR-RT0021`), before any `match` meets it. An enum without
   `@Layout` does not cross (`LYR-SEM0099`).
6. `@Layout` takes `C` or an integer type, written as a name: `@Layout(C)`, `@Layout(uint8)`. It
   sits on a struct or an enum that is not generic; on a class, on a generic type, on a struct
   with an integer type, or in another form it is refused (`LYR-SEM0099`).
7. **C's variadic arguments**: a bare `...` after the last parameter of a C function,
   `extern "C" fn printf(format: CStr, ...): int32;`, takes any number of arguments beyond the
   parameters. A parameter stands before it (`LYR-SEM0099`), and only a C function has it
   (`LYR-PAR0026`) — a Lyric function's variadic parameter, `xs: T...`
   ([03](03-types.md)), is another thing and unchanged. Each argument beyond the parameters is
   of a type that crosses as a parameter does (`LYR-SEM0099`), a `string` as its bytes as into a
   `CStr` (rule 3); a spread `xs...` does not hand an array over them. They cross as C's default
   argument promotions make them: a `float32` as `double`, an integer narrower than C's `int` — a
   `bool` and an enum of such an integer among them — as `int`; every other as itself. *(Informative:
   what the callee reads is its format's to say; an `int` is C's `int64_t`, which `%lld` reads,
   not `%d`.)*
8. **Memory and `unsafe`**: `unsafe { … }` — the word contextual, a statement — is a block
   within which `std.ffi`'s memory operations may be called: a pointer's `read()`, `write(v)`,
   `offset(n)` and `cast<U>()`, `alloc<T>(n)` and `free(p)`. Called outside one, each is refused
   (`LYR-SEM0233`), as `GcHandle.from` is (rule 12); the block is lexical, a lambda written within it is within it. Nothing else
   about the block differs, and calling a C function is not unsafe.
   - `read()` is the `T` at the pointer's address, `write(v)` puts one there; `T` is what a field
     of a `@Layout(C)` struct may be (rule 4, `LYR-SEM0099`), and the memory's layout is C's.
   - `offset(n)` is the address `n` values of `T` further — before it for a negative `n`;
     `cast<U>()` the same address as a `Ptr<U>`.
   - `alloc<T>(n)` is `n` values of `T` from C's heap, set to zero, never null: a negative `n`
     panics (`LYR-RT0007`), and so does a heap with no memory left (`LYR-RT0005`); `T` is as for
     `read`. `free(p)` gives it back.
   - What the program holds to in the block — that the memory is there, holds a `T` and is not
     freed twice — is the program's word; the implementation does not check it, and breaking it
     is undefined.
   - `xs.asPtr()` of an array or a slice — safe — is the address of its first element, the
     elements one after another as in a C array. The pointer does not keep the array alive, and
     points at nothing where it is empty.
9. **C function pointers**: `extern "C" fn(int) -> int` is the type of a pointer to a C function,
   crossing as C's function pointer wherever C holds one — a parameter, a result, a field. Its
   parameters and result are what a C function's are (rules 1–5, `LYR-SEM0099`); it throws
   nothing and takes no place (`LYR-SEM0099`); its ABI is `"C"` (`LYR-SEM0099`). A Lyric function
   type, `fn(int) -> int`, is a closure and does not cross (`LYR-SEM0099`). `?extern "C" fn(…)`
   is a pointer that may be null, as a parameter and as a result: `null` crosses as C's null, and a
   null pointer C returns comes back as `null` — not as a field, as for `?Ptr<T>` (rule 4).
   - Where such a type is expected, a function given by its name — free or static, with a body,
     without type parameters — or a lambda that captures nothing becomes the pointer, when its
     parameters and result are the type's and it throws nothing. Any other function value is
     refused (`LYR-SEM0001`): a closure's state has no place in C's pointer.
   - C calls such a function on the thread it runs on, through a trampoline that takes C's values
     as Lyric's (rules 1–5) and gives the result back as C's. The coroutine it runs in counts the
     C frames below it (§1.6 rule 6): the function may park and yield, and a panic in it ends the
     process with its report (§1.6 rule 10) — C's frames cannot be unwound. On a thread Lyric
     does not run — one C started itself — the call ends the process with `LYR-RT0022`, but for
     a `Callback`'s that returns nothing (rule 13).
   - A value of the type is called as a function is: a call of the C function it points at, each
     value crossing as for an `extern "C"` declaration.
10. **Closures C calls**: `std.ffi`'s `Callback<C>` holds a closure — a Lyric function value with
    its state — for C, which hands back a `void *userdata` beside its function pointer.
    - `C` is the C function's type as C calls it, an `extern "C" fn(…)` (`LYR-SEM0099` for another),
      whose first or last parameter is the userdata, a `Ptr<void>`; with none there, or with one
      at either end, it is refused (`LYR-SEM0099`).
    - `Callback<C>.new(closure)` takes a function of `C`'s other parameters, in their order, with
      `C`'s result, that throws nothing; a closure of another shape is refused as any argument of
      the wrong type is.
    - `cb.function`, of type `C`, is what C calls: it finds the closure through the userdata and
      calls it, as a function C calls is called (rule 9) — on the thread Lyric runs on, its C
      frames counted. `cb.userdata` is what C hands back to it.
    - The closure lives until `cb.release()`; C must not call `cb.function` afterwards. A second
      `release()` is a panic (`LYR-RT0008`).
11. **Errors across C**: a function C calls throws nothing (rule 9); its error crosses as
    `std.ffi.stash(e)`, which keeps `e` for the code around the C call, and `std.ffi.takeStashed()`
    there, which returns it and forgets it — `null` where none waits.
    - What is kept is the running task's own ([10 §2](10-concurrency.md)): a callback that parked
      leaves it for its task, not for whichever runs next. Where no task runs, it is the program's.
    - One error waits at a time: a second `stash`, before the first is taken, is dropped — the
      first went wrong first.
12. **Objects held for C**: `std.ffi.GcHandle<T>` holds an object of a class for C.
    - `GcHandle.pin(object)` holds it: the collector keeps it, wherever C keeps the handle, until
      `release()`; `T` is a class (`LYR-SEM0099`). `get()` is the object.
    - `asPtr()` is the `Ptr<void>` C keeps and hands back, the same for every handle of the object;
      `GcHandle<T>.from(pointer)` is a handle of it again. `from` is a memory operation of rule 8
      (`LYR-SEM0233` outside an `unsafe` block): the pointer is one `asPtr()` gave and that is not
      released. Reading a handle whose object is of another class than `T` is a panic
      (`LYR-RT0023`).
    - `release()` lets the object go; reading or releasing that handle again is a panic
      (`LYR-RT0008`). Reading another handle of a released object is undefined.
13. **Callbacks from C's threads**: a `Callback` belongs to the thread that made it. Called on a
    thread Lyric does not run, one whose type returns nothing does not run there: the call — what C
    passed, copied — goes to its thread, which runs it in its scheduler's next turn
    ([10 §2](10-concurrency.md)), in the order C's calls came; C's thread goes on at once.
    - One whose type returns a value would have C's thread wait for its own: the process ends
      (`LYR-RT0022`), as it does where the thread that made the Callback runs no scheduler.
    - While a thread's Callbacks are not released, its scheduler is not deadlocked when every task
      waits (10 §2 rule 12): a call from C may come and wake one.

## 4. Exports and libraries

A Lyric function C calls by a symbol, and the library `lyric build --lib` makes of a package for
a C program to link ([11 X8, H1–H3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).
A call of an export is C's call of a Lyric function on the thread Lyric runs on, as through a
C function's pointer (§3 rule 9).

**Conformance.** `conformance/cases/13-abi/`; that a C program links the library — the archive
and the shared one — and calls its exports, in the toolchain's own tests (`tests/Lyric5.Tests`,
`ExportTests`).

1. **`@Export("geo_area")`** on a function — a compiler instruction of the prelude
   ([11 §1](11-metaprogramming.md) rule 17) — makes it C's to call as the function `geo_area`; a
   bare `@Export` names it as the function is named. The symbol is written out as a string, or
   not at all (`LYR-SEM0099`); it is a C identifier, does not begin with `lyr_` or `LYR_` — the
   runtime's names —, and is one function's in the program (`LYR-SEM0099` for each).
2. What is exported is a free function with a body, `pub`, without type parameters, neither
   `inline` nor a macro (`LYR-SEM0099`). On a method the attribute stands out of its place
   (`LYR-SEM0065`).
3. Its parameters and its result cross as a C function's do (§2 rule 2, §3), the other way: C
   hands the parameters and takes the result. A `string` is no parameter — C hands its text as a
   `CStr`, which `toString()` copies —, a place is none, and every type that does not cross is
   refused, as a parameter and as a result (`LYR-SEM0099`).
4. An export that **throws** is C's `LyrStatus name(parameters…, R *out)`: `LYR_OK` with its
   result written through `out`, `LYR_ERROR` where it threw, `out` left as it was. Without a
   result there is no `out`. The error stays behind for `lyr_take_error` (§5 rule 4).
5. An export is a **root** of every build: of a program's — a C function of its native part
   ([15 §5](15-project.md)) may call it — and of a library's.
6. C calls an export after the runtime started (§1.5 rule 2) — before it the process ends with its
   report (`LYR-RT0022`) —, on any thread (§5 rule 5). The first call into a library fills the
   library's module-level bindings, once, as a program's start does before `main`
   ([04 §1](04-modules.md) rule 2); in a program `main`'s start filled them. How the function
   runs is §5's: as a task of its own, or in the task that runs where Lyric called the C that
   calls it.
7. **`lyric build --lib`** ([14 §1.1](14-cli.md) rule 9) builds the package's **library**: its root
   module `src/lib.lyr` and the modules it reaches by import, as a program is its entry module's
   ([04 §2](04-modules.md)) — without a `main` to start from; one there is an ordinary function.
   Under `out/<profile>/<target>/` it writes **`lib<name>.a`**, the archive that holds the library
   and the runtime, and the header **`<name>.h`**. With `--shared` a shared library takes the
   archive's place: `lib<name>.so`, `lib<name>.dylib`, or `<name>.dll` beside its import library
   `<name>.lib`.
8. The **header** declares, in this order:
   - the runtime's API (§5): `LyrStatus` with `LYR_OK`, `LYR_ERROR`, `LYR_PANIC`, `LyrConfig`,
     `lyr_init`, `lyr_shutdown`, `LyrError`, `lyr_take_error`, `lyr_step`, `lyr_run`,
     `lyr_detach_thread`;
   - the `@Layout` types the exports name, each before the first that needs it, named by its
     module's path and its own name joined by `_` — `geo.Point` is `geo_Point` —: a struct as C's
     `struct` of the same fields in their order, an enum with `@Layout(C)` as C's `enum`, one with
     an integer type as that integer with a constant per variant (`geo_Shape_Square = 0`, on in
     the order written);
   - the exports, each as C declares it: the integers by their widths (`int64_t` for `int`),
     `double` and `float`, `bool`, a `char` as `uint32_t`, a `Ptr<T>` as `T *` — `void *` where C
     has no name for `T` —, a `CStr` as `const char *`, an optional pointer as the pointer, a C
     function's pointer in C's form. A parameter is named as in Lyric, with a `_` after a name C
     reserves.
9. A shared library gives the system's loader its exports and the runtime's API of rule 8, and no
   other symbol. A C program that links the archive links the libraries the runtime calls too — on
   Linux `-lpthread -lm`, with zig cc `-lunwind`; on Windows `-lshell32 -lws2_32` — and those the
   packages' native parts name ([15 §5](15-project.md)), which a shared library is linked against
   itself. *(Written ahead of M14b:)* the **archives** of the native parts
   ([15 §5.2](15-project.md#52-linking)) lie inside `lib<name>.a` with the library and the runtime,
   so a C program links that one file; what it links beside it — the libraries by name and from
   `pkgConfig`, the frameworks, the runtime's — `build --lib` says after the archive, as the
   arguments of a C compiler in the order they are linked (`note: link it with -lpthread -lm …`),
   and its `--json` form gives them as the artifact's `linkArgs`
   ([16 §4](16-diagnostics.md)). They are the target's: another target has others.

## 5. Embedding

A C program that embeds Lyric: the runtime started, the exports called as tasks, the tasks they
leave pumped, a failure as a status
([11 H1–H6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).

**Conformance.** `conformance/cases/13-abi/`; that a C program embeds a library with threads and
output of its own — `examples/embedded-host` —, in the toolchain's own tests (`tests/Lyric5.Tests`,
`EmbeddingTests`).

1. **`lyr_init(config)`** starts the runtime, once per process, and answers `LYR_OK`; a second call
   answers `LYR_ERROR` and changes nothing. `config` — `NULL` for zeros — gives the program's
   arguments, a heap limit, whether the runtime installs its fault handlers (§1.4 item 6), and the
   writers its standard output and error go to instead of the process's (`stdout_write`,
   `stderr_write`, with `write_context`). **`lyr_shutdown()`** writes out what the program wrote and
   stops the runtime.
2. An export C calls where no Lyric runs below the call on the thread **runs as a task** on the
   thread's scheduler ([10](10-concurrency.md)): it may wait, the thread's other tasks run
   meanwhile, and the call returns to C when the task is done. What the task wrote is written out
   before the call returns.
3. A task an export starts with `spawnDetached` goes on after the export: in the thread's next
   export calls, in **`lyr_step()`** — one turn where a task is ready or due, without waiting;
   `true` while tasks remain on the thread — and in **`lyr_run()`**, which runs them to their end,
   waiting as they wait. On a thread where no export ran, and called from Lyric's C, neither does
   anything (`lyr_step` answers `false`).
4. A **panic** of an export's task (rule 2) is **`LYR_PANIC`** where the export throws (§4 rule 4):
   the runtime goes on as after any task's panic, and the next call runs. Where the export does
   not throw, the panic ends the process with its report, as in a program.
   **`lyr_take_error(&error)`** takes what the thread's last export that answered `LYR_ERROR` or
   `LYR_PANIC` left, and answers its status — `LYR_OK`, with `error` zeroed, where nothing waits,
   as after a take. For an error: its type as Lyric names it (`std.core.Exception`), its message,
   and the error that caused it as `cause`, on down to `NULL`; for a panic: its code as the type
   (`LYR-RT0008`), its message, and its frames as `trace`. The strings are the runtime's until the
   thread's next `lyr_take_error`.
5. A thread that never ran Lyric becomes Lyric's at its **first export** — attached to the
   collector, with a scheduler of its own ([10](10-concurrency.md)) —, and **`lyr_detach_thread()`**
   gives it back: its tasks that remain never run again. On the thread that called `lyr_init`, and
   on one Lyric started, it does nothing.
6. Where Lyric runs below the call on the thread — Lyric called C, which calls the export — the
   export runs in the task that runs, as a Lyric function C calls through its pointer does (§3
   rule 9): its C frames are counted, it may park, and a panic in it ends the process with its
   report. Calls nest as deep as the stack lets them, without a count of their own.

## 6. Loading a library

A shared library a program loads while it runs, and the C functions in it found by their names
([11 H7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md)).
A library of Lyric's own loaded this way — a second runtime in the process — is not covered.

**Conformance.** `conformance/cases/13-abi/`; that a program loads a library built apart and calls
what it finds — `examples/ffi` —, in the toolchain's own tests (`tests/Lyric5.Tests`,
`ExampleTests`).

1. **`std.ffi.Library.open(path)`** loads the shared library at `path` — a `.so`, `.dylib` or
   `.dll` —, as the system's loader does (`dlopen`, `LoadLibraryW`); a name without a directory goes
   where the loader looks. Where the loader refuses it, `open` throws `std.io`'s `IoError` of kind
   `NotFound`, with the path, and the loader's words as its detail.
2. **`lib.symbol<F>(name)`** is the symbol `name` of the library as a value of `F`, which is a C
   function's type, `extern "C" fn(…) -> …` — any other type is refused (`LYR-SEM0099`) —, and
   `null` where the library has no such symbol. The value is called as any C function's pointer
   (§3 rule 9). The type is the program's word: the loader knows a name, not a signature, and
   nothing checks the one against the other.
3. A `Library` is `Closeable` ([12](12-stdlib.md)): **`close()`** gives it back to the system, and
   a second close does nothing. A function found in it is not called after the close; `symbol` on a
   closed library panics.
4. A program that loads a library links the system's loader with it: on Linux `-ldl`, where the C
   library keeps `dlopen` apart.

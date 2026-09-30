# ABI and embedding

> **Partly written.** §1 was written with milestone **M1** of the Lyric 5 plan; the rest comes
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
   | `LYR-RT0002` | integer overflow, including `MIN / -1` ([03 T2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)) |
   | `LYR-RT0003` | an index outside its sequence |
   | `LYR-RT0004` | unwrapping a null value |
   | `LYR-RT0005` | no memory left, or the heap limit reached |
   | `LYR-RT0006` | stack overflow |
   | `LYR-RT0007` | a precondition of a runtime operation stated by the program text (a negative length) |

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

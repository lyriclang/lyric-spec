# 9. Errors: throw, catch, panic

Lyric separates three failure shapes, and the separation is the design:

1. **A state of the world** — a missing file, an unparsable string — is a RETURN VALUE (`?T` or
   `bool`).
2. **A recoverable exception** travels through `throw`/`try`/`catch`.
3. **A programming error** is a `panic`: not catchable, ends the program with a backtrace.

## 9.0 The library doctrine: a value answers WHETHER, a throw answers WHY

The two recoverable shapes divide by the question, not by the operation (since 3.7):

- **`?T` and `bool` answer "is it there? did it happen?"** — absence and non-occurrence as
  values. Where that answer is the WHOLE truth — an unset environment variable has no further
  story — the silent form stands alone.
- **A throw answers "why not?"** Where a failure carries a REASON a caller could act on or
  report — which file operation failed and how, where in a document the syntax broke — the
  library offers a throwing form beside the silent one, named with the suffix **`OrThrow`**,
  declaring a module-specific error type (`throws IoError`, `throws JsonError`) whose fields
  carry the reason.

**Both forms answer from ONE implementation**: the silent form is `null`/`false` exactly where
the throwing one throws, derived from it in source — never a second implementation that could
drift. Which form a program calls states what it will do with a failure: fall back, or handle
the reason.

The error types themselves are library surface (§11): their fields evolve under the
deprecation policy, and a reason ENUM behind a carrier class may gain variants without
breaking a `match` — the carrier-plus-kind shape exists exactly so that adding a reason is
not a break. What this section fixes is the doctrine, not the types.

## 9.1 Throwables

Only class values whose type reaches `Throwable` — directly, through an extend, or through an
interface chain — may be thrown, caught, or named in `throws` (`LYR-SEM0030`). `Throwable` is a
**builtin interface**, visible without any import, requiring `fn message(): string`;
`std.core.Exception` is the ready-made carrier class. Structs do not throw: a catch binds a
reference.

## 9.2 `throws` clauses

`fn f(): T throws E` declares what may escape: nothing (no clause), a specific throwable type,
or `throws` bare for "any throwable". The checker enforces the subset direction — a function
may throw less than it declares, never more — and conformance requires an implementation's
clause to be a subset of the interface's (§5.1). The exception analysis is part of the
language: an uncaught, undeclared throw is a compile error at the function that leaks it.

The ENTRY POINT declares nothing: a `throws` clause on `main` is refused (`LYR-SEM0021`, the
signature rule) — which is what makes an exception escaping the program (`LYR-VM0010`) a
hand-built-module affair rather than something source can produce.

## 9.3 `try` / `catch`

`try { … } catch (e: E) { … }` — the first matching clause wins. Three binding forms exist:
`catch (e: E)` with a class type matches exactly that class; `catch (e)` and `catch (_)` catch
everything, the former binding `e` as `Throwable`; and `catch (e: Throwable)` is the catch-all
written out. Within a clause the binding has the declared type. `defer` blocks run while
unwinding.

*Implementation limit (diagnosed, `LYR-IR0001`):* a clause naming an interface OTHER than
`Throwable` is refused — matching it would need a conformance test during unwinding, which the
reference runtime's handler table cannot express yet.

## 9.4 `panic`

`panic(message)` returns `never`: flow analysis treats everything after it as unreachable, and
an `if`-branch ending in panic narrows the other branch. Panics carry a backtrace with function
names, and line numbers when the module has a source map. Assertion helpers (`assert`, `todo`,
`unreachable`) are `panic` with a statement about who got it wrong — deliberately `void`, so
they never replace a `return`. Runtime panics of the machine itself: division by zero
(`LYR-VM0002`), `!` on an empty optional (`LYR-VM0007`), index out of range, call-depth
exhaustion, `resume` on a finished coroutine.

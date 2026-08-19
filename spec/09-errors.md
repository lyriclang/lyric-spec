# 9. Errors: throw, catch, panic

Lyric separates three failure shapes, and the separation is the design:

1. **A state of the world** — a missing file, an unparsable string — is a RETURN VALUE (`?T` or
   `bool`). The standard library holds this line everywhere.
2. **A recoverable exception** travels through `throw`/`try`/`catch`.
3. **A programming error** is a `panic`: not catchable, ends the program with a backtrace.

## 9.1 Throwables

Only class values whose type reaches `Throwable` (`std.core`) — directly, through an extend, or
through an interface chain — may be thrown, caught, or named in `throws` (`LYR-SEM0030`).
`Throwable` requires `fn message(): string`; `std.core.Exception` is the ready-made carrier.
Structs do not throw: a catch binds a reference.

## 9.2 `throws` clauses

`fn f(): T throws E` declares what may escape: nothing (no clause), a specific throwable type,
or `throws` bare for "any throwable". The checker enforces the subset direction — a function
may throw less than it declares, never more — and conformance requires an implementation's
clause to be a subset of the interface's (§5.1). The exception analysis is part of the
language: an uncaught, undeclared throw is a compile error at the function that leaks it.

## 9.3 `try` / `catch`

`try { … } catch (e: E) { … }` — the first matching clause wins. A clause matches when the
thrown value's type IS the declared type or conforms to it; a clause may declare an interface
(`Throwable` itself included) and then catches everything reaching it. Within the clause the
binding has the declared type. `defer` blocks run while unwinding.

## 9.4 `panic`

`panic(message)` returns `never`: flow analysis treats everything after it as unreachable, and
an `if`-branch ending in panic narrows the other branch. Panics carry a backtrace with function
names, and line numbers when the module has a source map. Assertion helpers (`assert`, `todo`,
`unreachable`) are `panic` with a statement about who got it wrong — deliberately `void`, so
they never replace a `return`. Runtime panics of the machine itself: division by zero
(`LYR-VM0002`), `!` on an empty optional (`LYR-VM0007`), index out of range, call-depth
exhaustion, `resume` on a finished coroutine.

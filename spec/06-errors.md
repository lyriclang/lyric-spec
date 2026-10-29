# 6. Errors

**Base.** Lyric 5.0 [§6](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/06-errors.md) applies, with the deviations below.

**Status.** Written for what S4a builds: what is thrown, `throw`, the `try` block with typed
clauses and the clause without a type, the error path through the frames and the report of an
error that leaves the script. The thrown sets (S4c), the expression forms, the set clause and
the rules among clauses (S4d), `defer` and `using` with the suppressed errors (S4e), panics and
`never` as a return type (S4f) are written with the slices that build them; until then the
design documents decide.

## Written (S4)

1. **What is thrown** (§1 rules 1–4). `Error` and `Exception` are names of the prelude in
   Lyric-Script (Lyric 5 declares them in `std.core`): `interface Error { fn message(): string
   fn cause(): ?Error }`, `cause` `null` unless a type says otherwise; `Exception("…")`, and
   `Exception("…", cause: e)` for the error it wraps, its fields `text` and `inner`. A value is
   thrown when its type conforms to `Error` — a struct, a class or an enum, an interface that
   extends `Error`, a type parameter constrained to it —; anything else is refused
   (`LYS-SEM0030`). `throw e` is a statement, and an expression of type `never` where a value
   stands (`x ?? throw NotFound { key }`); `never` fits every type.
2. **The `try` block** (§4 rules 1–4). The clauses are asked in order, and the first that
   covers the error takes it: `catch (e: T)` an error whose type is `T` or conforms to it, bound
   as a `T` — its fields and variants there to read —; `catch (e)` and `catch (_)` every error,
   `e` an `Error`. A clause's type conforms to `Error` (`LYS-SEM0030`); a block without a
   clause is refused (`LYS-SEM0036`). What no clause takes goes on as though the `try` were not
   there; a clause is not inside its own `try`, so what it throws goes to the `try` around. A
   clause may run after any part of the body: it knows assigned only what was assigned before
   the `try`, and after the `try` a binding is assigned where the body and every clause assign
   it ([07](07-statements.md) rule 3).
3. **The error path** (§5 rules 1 and 3). An error leaves frame after frame, each a return
   without a value, until a clause takes it; in a caller the call stands where it was thrown.
   One that leaves the script's code ends the run with exit code 1: `error: <message>` on the
   error stream, then `  caused by: <message>` for each `cause()` in the chain, then the frames
   it was thrown from in a panic's trace form. A chain is followed for at most 64 causes, so a
   cycle in it ends; an error whose `message()` throws is named by its type.
4. *Informative.* A function's code carries a table of regions, innermost first, each sending
   the errors of its instructions to its clauses' tests — one test of the value's descriptor
   each, as `is` makes it. An error looks for the first region that covers it, in its frame and
   then at each caller's call; a throw that no clause takes costs the returns it makes. The
   report asks the error for its message and its causes in the same run, where the script's
   globals still are.

## Deviations

- Thrown sets are inferred; a written `throws` is a checked contract; `try` is accepted without effect; lint `unmarked-throw` ([02 K2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [05 Th](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- Function types carry no `throws`; iterators have no error type ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- An error that escapes the top level ends the script with exit 1; embedded it is `.Error` at the host ([05 E6](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md), [01 S11](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).
- The report always ends with the frames, as a panic's does: a script keeps them (Lyric 5 keeps them in the debug profile only, §5 rule 3).

**Conformance.** `conformance/cases/06-errors/` (`since: 1.0.0`).

# 6. Errors

**Base.** Lyric 5.0 [§6](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/06-errors.md) applies, with the deviations below.

**Status.** Written for what S4a–S4c build: what is thrown, `throw`, the `try` block with typed
clauses and the clause without a type, the record of where an error was first thrown, the error
path through the frames and the report of an error that leaves the script, the thrown sets
inferred and a written `throws` held against them, the mark `try`. The expression forms, the
set clause and the rules among clauses (S4d), `defer` and `using` with the suppressed errors
(S4e), panics and `never` as a return type (S4f) are written with the slices that build them,
`e.suppressed()` with the arrays (S7), the lint `unmarked-throw` with the lints (S11); until
then the design documents decide.

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
3. **The error's record** (§4 rule 4). An error keeps where it was first thrown: its frames,
   innermost first, a line `    at <function> (line <n>)` each — the **trace form**, a panic's
   too; the script's code is `<script>`, a method `<Type>.<name>`, a caller stands at its call.
   A clause's binding tells of it: `e.backtrace()` is a `?Backtrace` of the prelude whose
   `show()` is that text. It is asked of the binding itself, in its clause; an error passed on,
   stored or captured by a lambda is a value like any other and has none (`LYS-SEM0012`), and
   where the binding's type has a member of the name, the name is that member. `throw e` of the
   binding in its clause is the same error going on and keeps its record, as an error no clause
   takes does; any other throw starts a record of its own.
4. **The error path** (§5 rules 1 and 3). An error leaves frame after frame, each a return
   without a value, until a clause takes it; in a caller the call stands where it was thrown.
   One that leaves the script's code ends the run with exit code 1: `error: <message>` on the
   error stream, then `  caused by: <message>` for each `cause()` in the chain, then the frames
   of its record (rule 3). A chain is followed for at most 64 causes, so a cycle in it ends; an
   error whose `message()` throws is named by its type.
5. **Thrown sets** (§2, §3 rules 3–5; [05 K, K7](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
   What a function may throw — its **set** — is inferred from its body: the types its `throw`s
   throw and the sets of what it calls, less what the clauses of its `try`s take; a recursion
   is closed by a fixpoint. A call through a function value may throw anything, an `Error`:
   a function type carries no set ([02 K2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md)).
   A call through an interface member throws what the member writes in its `throws` (rule 6),
   or else what its implementations in the script throw. A clause's `throw e` of its binding
   throws what reached the clause — the clause's type, for the clause without a type what the
   body throws past the clauses above it (the precise rethrow). A generic's set is in its
   call's terms: `fail<T :: [Error]>(e: T) throws T` called with an `A` throws `A`.
6. **A written `throws`** (§2 rules 1–4; 05 Th) is a contract the set is held against:
   `throws E`, `throws [A, B]` — several in brackets (`LYS-PAR0049`) —, or the bare `throws`,
   which is `throws Error`; each type an `Error` (`LYS-SEM0030`), named once (`LYS-SEM0137`).
   Every type the function may throw is covered by it — the type itself, an interface the type
   conforms to, or `Error` (§3 rule 4) —, or the function is refused at its `throws`, the
   diagnostic naming each type and the line it comes from (`LYS-SEM0034`). An implementation of
   an interface member that writes `throws` throws at most that (`LYS-SEM0042`); a call through
   the member throws what it writes.
7. **The mark `try e`** (§3 rules 1–2) is accepted and changes nothing: it covers what stands to
   its right — `a + try b * c` marks `b * c` —, and a call need not stand under it.
8. *Informative.* A function's code carries a table of regions, innermost first, each sending
   the errors of its instructions to its clauses' tests — one test of the value's descriptor
   each, as `is` makes it. An error looks for the first region that covers it, in its frame and
   then at each caller's call; a throw that no clause takes costs the returns it makes. The
   record is the frames' functions and instructions, made at each `throw` and carried by a
   region's second register and `rethrow`; its text is made only when asked. The report asks the
   error for its message and its causes in the same run, where the script's globals still are.

## Deviations

- Thrown sets are inferred (rule 5); a written `throws` is a checked contract (rule 6); `try` is accepted without effect (rule 7); lint `unmarked-throw` ([02 K2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [05 Th](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)). A call through an interface member that writes no `throws` throws what the member's implementations in the script throw; Lyric 5 declares every set.
- Function types carry no `throws`; iterators have no error type ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- An error that escapes the top level ends the script with exit 1; embedded it is `.Error` at the host ([05 E6](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md), [01 S11](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).
- A script keeps an error's frames: the report always ends with them, as a panic's does, and `e.backtrace()` is never `null` (Lyric 5 keeps them in the debug profile only, §4 rule 4, §5 rule 3). The trace form names no file; with modules (S5) it will.

**Conformance.** `conformance/cases/06-errors/` (`since: 1.0.0`).

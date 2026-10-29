# 6. Errors

**Base.** Lyric 5.0 [§6](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/06-errors.md) applies, with the deviations below.

**Status.** Written for what S4a–S4e build: what is thrown, `throw`, the `try` block and its
clauses with the rules among them, the record of where an error was first thrown, the error path
through the frames and the report of an error that leaves the script, the thrown sets inferred
and a written `throws` held against them, the mark `try`, the expression forms `try?`, `try!`
and `try … catch`, `defer` and `using` with the suppressed errors. Panics and `never` as a return
type (S4f) are written with the slice that builds them, `e.suppressed()` with the arrays (S7),
the lint `unmarked-throw` and the `let` half of `LYS-SEM0144` with the lints (S11); until then
the design documents decide.

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
   error stream, then `  caused by: <message>` for each `cause()` in the chain and
   `  suppressed: <message>` for each error a defer threw while it was in flight (rule 10), then
   the frames of its record (rule 3). A chain is followed for at most 64 causes, so a cycle in it ends; an
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
8. **The expression forms** (§6). `try? e` is `e`'s value as an optional, or `null` where
   something under it throws; it is not flattened — over a `?int` a `??int`. Over what gives no
   value it stands as a statement, where it only drops the error (`LYS-SEM0140`). `try! e` is
   `e`'s value; where something under it throws, the script ends with the panic `LYS-RT0010`,
   `'try!' on an error: <message>`, exit code 101. The sign is written against the keyword:
   `try !done()` is the mark over a negation. `try e catch (x: A) v catch (y) w` is `e`'s value,
   or the value of the clause that took the error, its clauses asked as a block's are; a
   clause's value is an expression or a value block, and the parts give one type as a match's
   arms do (`LYS-SEM0016`); as a statement they give none. A clause belongs to the nearest `try`
   on its left — `try f() catch (_: A) try g() catch (_: B) 0` gives the clause for `B` to `g` —
   and parentheses give it to the outer one. These three forms stand at the start of what they
   cover, not right of an operator (`LYS-PAR0050`); `try?` and `try!` take no clause
   (`LYS-PAR0051`).
9. **Among clauses** (§4 rules 2, 5–6; 05 K7). `catch (e in [A, B])` takes a value of any of its
   types — one alone, `catch (e in A)`, is the typed clause —, and `e` is an `Error`. A type is
   caught once per `try`, within a set too (`LYS-SEM0141`); a clause whose type a type caught
   above covers is refused, no error reaching it (`LYS-SEM0142`); the clause without a type
   stands last (`LYS-SEM0035`), and below it its own error is the one said. The binding of a set
   clause or of the clause without a type carries the set that reaches the clause (rule 5): a
   `match (e)` whose type patterns cover that set needs no `_` (`LYS-SEM0050` names a type no arm
   takes, and where anything may reach the clause only `_` covers it).
10. **`defer`** (§5 rules 2–5). `defer { … }` or `defer e` runs its body when its scope is left —
    the end of the block, a `return`, a `break`, a `continue`, an error — on every way out but a
    panic, the last registered first; a value block is a scope too. A `return`'s value is taken
    before the defers run. On the error path the defers run and the error goes on. A defer that
    throws on a normal exit ends that exit: its error leaves like any other, and the defers
    registered before it run all the same. One that throws while an error is in flight does not
    replace it: the first wins, the second goes with it as **suppressed** (rule 4), and the
    remaining defers run. A defer runs where it was registered — under the `try`s around its
    scope, not those inside it. A `return`, or a `break` or `continue` to a loop outside it,
    does not stand in a defer's body (`LYS-SEM0904`).
11. **`using let f = e`** (§7) binds `f` like a `let` and closes it — calls `f.close()` — when
    its scope is left, in the scope's one list with its defers: `using let a = …; defer d;
    using let b = …` closes `b`, runs `d`, closes `a`. What it binds is a `Closeable`, the
    prelude's `interface Closeable { fn close() }` (`LYS-SEM0143`); `using var`, or a `using`
    without one name and a value, is refused (`LYS-PAR0052`). An error of `close()` is a defer's.
    A `Closeable` an expression statement makes and drops is warned about (`LYS-SEM0144`).
12. *Informative.* A function's code carries a table of regions, innermost first, each sending
   the errors of its instructions to its clauses' tests — one test of the value's descriptor
   each, as `is` makes it. An error looks for the first region that covers it, in its frame and
   then at each caller's call; a throw that no clause takes costs the returns it makes. The
   record is the frames' functions and instructions, made at each `throw` and carried by a
   region's second register and `rethrow`; its text is made only when asked. A defer is placed
   on every way out by the compiler: the rest of its scope is a region whose handler runs the
   defer and throws on; a `return`, a `break` or a `continue` through it runs the defer's copy
   outside the region, which has a gap there. The report asks the
   error for its message and its causes in the same run, where the script's globals still are.

## Deviations

- Thrown sets are inferred (rule 5); a written `throws` is a checked contract (rule 6); `try` is accepted without effect (rule 7); lint `unmarked-throw` ([02 K2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [05 Th](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)). A call through an interface member that writes no `throws` throws what the member's implementations in the script throw; Lyric 5 declares every set.
- Function types carry no `throws`; iterators have no error type ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- An error that escapes the top level ends the script with exit 1; embedded it is `.Error` at the host ([05 E6](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md), [01 S11](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).
- A jump out of a defer's body is refused (`LYS-SEM0904`); Lyric 5 does not say what one does.
- The binding of a set clause or of the clause without a type is an `Error` even where one type reaches the clause (Lyric 5 binds that type, review M5-6): the sets are inferred after the bodies are checked. A `match` over it with type patterns reaches the type.
- A script keeps an error's frames: the report always ends with them, as a panic's does, and `e.backtrace()` is never `null` (Lyric 5 keeps them in the debug profile only, §4 rule 4, §5 rule 3). The trace form names no file; with modules (S5) it will.

**Conformance.** `conformance/cases/06-errors/` (`since: 1.0.0`).

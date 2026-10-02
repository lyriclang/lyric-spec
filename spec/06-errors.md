# 6. Errors

A function that can fail says so in its signature, a call of it is marked where it stands, and
what it throws is caught or passed on by a function that says so in turn — two channels, the
value and the error, each in plain sight
([05 E1–E12](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/05-fehler.md),
[01 L5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[08 D9, D18, Y4, Y5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)).

## Scope

What is thrown, the `throws` set, the `try` mark and what covers a thrown type (S1a); the `try`
block with its clauses and the error path at run time — propagation, `defer` on the way out,
`main`'s report (S1b); the expression forms `try?`, `try!` and `try … catch` (S2a); a clause over
several types, the set a binding carries and the refusal of a clause no error can reach (S2b); a
`defer` that throws (S3a); `using` and `Exception` (S3b); where an error was thrown, and a rethrow
that keeps it (S3c); the thrown set of a function type (S4a); panics and `never` (S4b). Written
with M5. What is not written here yet is decided in the design documents, not here.

**Conformance.** `conformance/cases/06-errors/`.

## 1. What is thrown

1. **`Error`** of `std.core` is the root of everything thrown, caught and declared:
   `interface Error { fn message(): string; fn cause(): ?Error { return null; } }` (05 E6 O1).
   `cause` names the error this one wraps; the wrapping is the type's own field (O2).
2. A value is **throwable** when its type conforms to `Error` (E3): a struct, a class or an enum
   that conforms, an interface value of `Error` or of an interface extending it, a type
   parameter constrained to it. An enum is the natural form —
   `enum ParseError :: [Error] { Empty, BadDigit(char, int); … }`. Anything else — a number, a
   string, an array, an optional — is not (`LYR-SEM0030`).
3. `throw e` throws `e`; it is a statement, or an expression of type `never` wherever an
   expression may stand (`x ?? throw NotFound { }`). `e` is throwable (`LYR-SEM0030`).
4. **`Exception`** of `std.core` is the ready-made error for a message:
   `throw Exception { text = "…" }`, with `inner` for the error it wraps — what its `cause()`
   gives (12 E06). The field is `text`: a type's members share one name space, and `message` is
   `Error`'s method.

## 2. The `throws` set

1. A function that may throw declares it after its return type: **`throws E`** for one type,
   **`throws [A, B]`** for several — a **set**, in brackets from two on like every list
   ([08 D5/D6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)); two
   without the brackets are refused (`LYR-PAR0049`). The order means nothing; a type named
   twice is refused (`LYR-SEM0137`). Every element is throwable (`LYR-SEM0030`).
2. The bare **`throws`** is `throws Error`: anything may be thrown, and the caller learns what by
   testing the value's type. The list is the form to prefer.
3. The set is **declared, never inferred**, for a named function (K3). A function without a
   clause throws nothing.
4. An implementation of an interface member throws **at most** what the member declares: every
   type of its set is covered by the member's ([§3](#3-the-try-mark-and-coverage) rule 4, K6) —
   `LYR-SEM0042` otherwise.
5. `fn main()` may declare `throws` ([08 D18](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)),
   like any function; its return type is `int` or `void`, with or without `args: string[]`
   (`LYR-SEM0021`).
6. A **function type** has a set too, `fn(string) -> int throws ParseError`: a function value and
   a lambda throw what their type says ([§8](#8-function-values-that-throw)).

## 3. The `try` mark and coverage

1. Every call of a throwing function is **marked**: it stands under **`try`** — the prefix
   `try e`, `try? e` or `try! e` ([§6](#6-the-expression-forms)), or the body of a `try { … }`
   block — of its own function (`LYR-SEM0138`). A
   refactoring that makes a function throw shows at every caller instead of passing through
   unseen (E1). A lambda's body is a function of its own: a `try` around the lambda does not mark
   what its body calls.
2. `try` **covers everything to its right**: `try a + b` is `try (a + b)` and marks every call in
   it ([08 Y4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)). It
   therefore stands at the **start** of the expression it covers — a binding's value, an
   argument, a `return`, the right of an `=` — and to the right of another operator it is
   refused (`LYR-PAR0050`): `1 + try f()` is written `try 1 + f()`. The value and the type are
   the expression's. A `try` no error reaches is warned about (`LYR-SEM0139`): nothing under it
   throws, or a `try` inside it takes all of it.
3. Every type a site may throw — a marked call, or a `throw` — is **covered** (K8): by a `try?`
   or `try!` around the site, by a `catch` clause of a `try` around it
   ([§4](#4-the-try-block-and-its-clauses), [§6](#6-the-expression-forms)), or by the `throws` set
   of the function the site stands in (`LYR-SEM0034`). A global's initializer and a default cover
   nothing.
4. An element **covers** a thrown type when it **is** that type — on the instance: `Box<int>`
   does not cover `Box<string>` (K5) — or when it is an interface the type conforms to. `Error`
   covers everything thrown.
5. A call throws its function's set **in the instance's terms**: a method of `Box<int>` declared
   `throws Wrong<T>` throws `Wrong<int>`.

## 4. The `try` block and its clauses

1. `try { … } catch (e: T) { … } catch (e) { … }` runs the body; when something in it throws,
   the clauses are asked **in order**, and the first whose type covers the thrown value's type
   ([§3](#3-the-try-mark-and-coverage) rule 4) takes it: the error is handled, its clause runs, and
   execution continues after the `try`. A block without a clause is refused (`LYR-SEM0036`).
2. A typed clause binds the value under its own type — a class's object, a struct's or an
   enum's value, an interface value of the clause's interface — so its fields and its variants
   are there to read and match. The **set form** `catch (e in [A, B])` takes a value of any of its
   types — one alone without the brackets, `catch (e in A)`, several in them, the list rule
   (`LYR-PAR0049`) — and `e` is an `Error` that carries the set (rule 6). `catch (e)` and
   `catch (_)` take everything; `e` is an `Error`. A clause without a type stands last
   (`LYR-SEM0035`). A clause's types conform to `Error` (`LYR-SEM0030`).
3. When no clause covers the value, it goes on as though the `try` were not there: to the
   clauses of a `try` around this one, or out of the function ([§5](#5-the-error-path)).
4. A clause is not inside its own `try`: what it throws goes past its sister clauses to the next
   `try` around, or out of the function (E9 C6). `throw e` in a clause throws the value it took;
   where `e` is the clause's own binding, thrown in the clause itself, it is **the same error
   going on** (05 E6 O3): the errors suppressed into it stay with it
   ([§5](#5-the-error-path) rule 5), and so, in the debug profile, does where it was first thrown
   (§5 rule 3). Any other `throw` — the value under another name, or from a lambda — starts an
   error of its own.
5. A type is caught **once** per `try` (`LYR-SEM0141`, E9 C1), and a clause no value can reach is
   refused (`LYR-SEM0142`, C2): a type of it is covered ([§3](#3-the-try-mark-and-coverage) rule 4)
   by a type caught before it — `catch (e: IoError)` above `catch (e: Disk)`, or `Error` above
   anything. Within a set the same holds from left to right. Below the clause without a type,
   rule 2's `LYR-SEM0035` is the one error.
6. The binding of a set clause, or of a clause without a type, **carries a set** (05 E2 K7): the
   set's types; for the clause without a type, what reaches it — every type the body throws past
   the `try`s inside it, less the types the clauses above cover. `throw e` throws exactly that set
   (precise rethrow): `catch (_: NotFound) { … } catch (e) { throw e; }` in a function that
   declares `throws Parse` is covered when the body throws `[NotFound, Parse]`. A `match (e)`
   whose type patterns cover the set needs no default (`LYR-SEM0050` names a missing type). The
   set is the binding's alone: stored elsewhere, the value is an `Error`.
7. *(Informative.)* Since the value travels with its type, the clause test is one comparison of
   the value's type descriptor, an interface clause a search of the type's short conformance
   list.

## 5. The error path

1. A throw site that is not caught where it stands **leaves**: the function returns to its caller
   at once, without a value, and the caller's marked call is now the site — caught there, or
   leaving in turn (E1). No frame is skipped; a throw costs what a return costs (01 L5).
2. On the way out of every scope it leaves, an error runs the scope's **`defer`s**, the last
   registered first, innermost scope first — the same bodies a normal exit runs — before a
   clause of an enclosing `try` takes it (E7).
3. An error that leaves **`main`** ends the program: `error: <message>` on the error stream, then
   `  caused by: <message>` for each `cause()` in the chain and `  suppressed: <message>` for each
   error appended to it (rule 5), and the **exit code 1** (05 E6 O4) — a panic's is 101. In the
   **debug profile** the report goes on with where the error was thrown, its frames in a panic's
   trace form (01 E8); the release profile keeps no trace of an error.
4. A `defer` body runs **where its `defer` was registered**: under the `try`s around that scope,
   not those inside it. A `defer` registered outside a `try` and run by a `return` inside it is
   not that `try`'s to catch; one registered in a `try`'s body is. What the body throws is a site
   of that scope ([§3](#3-the-try-mark-and-coverage)).
5. A `defer` that **throws on a normal exit** — the end of its scope, a `return`, a `break`, a
   `continue` — ends that exit: the error leaves like any other, and the `defer`s registered
   before it run all the same. One that **throws while an error is in flight** does not replace
   it: the **first error wins**, the second is appended to it as **suppressed**, and the remaining
   `defer`s run (05 E7). Of two that throw on a normal exit, the first that ran wins.

## 6. The expression forms

1. **`try? e`** is worth `?T` for an `e` of type `T`: the value, or **`null`** when something
   under it throws — the error is dropped. It is **not flattened**: for an `e` of type `?int` it
   is `??int`, so "the call failed" stays apart from "the call gave `null`" (05 E4). Over an
   expression without a value `try?` stands as a statement, where it only drops the error;
   anywhere else it is refused (`LYR-SEM0140`).
2. **`try! e`** is worth `e`'s value; when something under it throws, the program ends with a
   **panic** — `panic [LYR-RT0010]: 'try!' on an error: <message>`, exit code 101 — and no
   `defer` runs past it (05 E8).
3. `try?` and `try!` take every error under them themselves: they mark the calls they cover
   ([§3](#3-the-try-mark-and-coverage) rule 1) and cover what those throw (rule 3). The sign is
   written against the keyword — `try !done()` is the mark over a negation — and the form stands
   at the start of what it covers, as the mark does (`LYR-PAR0050`).
4. **`try e catch (x: A) v catch (y) w`** is the expression form of the block (05 E4): its
   clauses are asked as a block's are ([§4](#4-the-try-block-and-its-clauses)), and the
   expression is worth `e`'s value, or the value of the clause that took the error. A clause's
   body is an expression, or a value block `{ …; v }`; a value block without a tail leaves on
   every path — `return`, `throw`, `break`, `continue` — unless the expression has no value
   (`LYR-SEM0033`). The parts unify like the arms of a `match`, or each meets the context where
   there is one (`LYR-SEM0016`). The rules of §4 hold: the clause without a type last
   (`LYR-SEM0035`), a clause not inside its own `try`. `throw` as a clause's body throws with
   context — `try read(p) catch (e: IoError) throw ConfigError { inner = e }`.
5. A clause belongs to the **nearest `try` on its left** ([08 Y4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)): in
   `try f() catch (_: A) try g() catch (_: B) 0` the clause for `B` is `g`'s, and parentheses
   give it to the outer `try`. `try?` and `try!` take no clause (`LYR-PAR0051`).
6. *(Informative.)* Each form opens a dispatch of its own, as the block does: `try?` clears the
   error and gives `null` there, `try!` panics there, the clauses are tested there. Nothing is
   unwound; the cost is the block's (§4 rule 7, §5 rule 1).

## 7. Closing: `using`

1. **`using let f = e;`** binds `f` like a `let` and **closes** it — calls `f.close()` — when its
   scope is left, on every way out but a panic, in the scope's one LIFO list with its `defer`s
   (05 E7 R2): `using let a = …; defer d; using let b = …;` closes `b`, runs `d`, closes `a`.
   `using var`, and a `using` without one name and a value, are refused (`LYR-PAR0052`). `using`
   is a word only before `let` or `var`.
2. What `using` binds is a **`Closeable`** of `std.core`,
   `interface Closeable { fn close(): void throws Error; }` (`LYR-SEM0143`, R6). The close is a
   site of the scope, `using` its mark: what `close()` throws on the bound type is covered as any
   site is ([§3](#3-the-try-mark-and-coverage)) — and a close that cannot throw needs no mark
   and draws no warning (no `LYR-SEM0139`).
3. An error from `close()` is a `defer`'s error ([§5](#5-the-error-path) rule 5, R4): on a normal
   exit it leaves, while an error is in flight it is appended to it as suppressed.
4. A `Closeable` nothing closes is warned about (`LYR-SEM0144`, R3): a call's result an expression
   statement drops, or a plain `let` used only to call its other methods — not closed, not
   `using`-bound, not stored, returned or passed on.
5. *(Informative.)* A use after the close is a run-time error once the library's types track it
   (R5); a `for` loop closes a `Closeable` iterator (R7) with the iterators.

## 8. Function values that throw

1. A **function type** may say what a call of it throws, after its return type and under the
   rules of a function's clause ([§2](#2-the-throws-set)): `fn(string) -> int throws ParseError`,
   `fn() -> void throws [IoError, ParseError]`, the bare `throws` for `Error`
   ([03 T17](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)).
   Without it the type throws nothing. The set is part of the type, as a set: `throws [A, B]` and
   `throws [B, A]` are one type, `fn() -> int` and `fn() -> int throws A` two. The **nearest**
   function type takes the `throws` after it — `fn make(): fn() -> int throws E` returns a
   throwing function and throws nothing itself — and a parenthesized return gives it to the outer
   one, `fn make(): (fn() -> int) throws E`. After one type a comma ends the function type, as in a
   parameter list; several are written in brackets.
2. A **call through a value** of such a type is a site like the call of a throwing function: it is
   marked ([§3](#3-the-try-mark-and-coverage) rule 1), and its set is covered (rule 3).
3. A function value **coerces** to a function type that throws more: the same parameters and
   return, and every type of its set covered by the target's (05 E2 K6) — `fn(int) -> int` where
   `fn(int) -> int throws E` is expected, `throws A` where `throws [A, B]` is. Never the other way:
   a value that may throw does not fit a type that throws less (`LYR-SEM0001`). The parameters and
   the return still match exactly ([03 §8.1](03-types.md#81-the-type)).
4. A throwing **function or method named as a value** has its set in its type, in the instance's
   terms ([§3](#3-the-try-mark-and-coverage) rule 5): `check`, declared
   `fn check(n: int): int throws Negative`, is a `fn(int) -> int throws Negative`, and `limit.take`
   bound to its object likewise ([03 §8.4](03-types.md#84-functions-and-methods-as-values)).
5. A **lambda** throws what its type says (05 E2 K3). The parenthesized form may write the set
   after its return type, `(s: string): int throws ParseError => try parse(s)`, and several types
   in brackets (`LYR-PAR0049`); otherwise a position that expects a function type gives the set,
   and the body is held to it (`LYR-SEM0034`); where neither fixes it, the set is what the body lets
   escape — the types its sites throw past every `try` inside it. The function around the lambda
   covers nothing of it: the lambda runs later.
6. A **type parameter** may stand as the set, `throws E` with `E :: [Error]`
   ([§1](#1-what-is-thrown) rule 2, `LYR-SEM0030`), and is **inferred** at a call from the
   argument's set (05 E2 K4): a set of none binds `never`, one type binds it, several bind `Error`
   (the K7 join) — `fn map<T, U, E :: [Error]>(xs: T[], f: fn(T) -> U throws E): U[] throws E`
   throws what `f` throws. Where several arguments could bind it, one binding stands, as for any
   type parameter ([03 §9.2](03-types.md#92-inference-at-a-call)), and an argument that throws
   beyond it is refused there. An `E` bound to `never` names nothing: a call
   whose set comes out empty throws nothing, needs no `try`, and a `try` over it is warned about
   (`LYR-SEM0139`).
7. *(Informative.)* A function value is two words, code and environment
   ([03 §8.1](03-types.md#81-the-type)); the code takes its caller's error slot whether its type
   throws or not, so the coercion of rule 3 changes nothing at run time and wraps nothing, and code
   that cannot throw never writes the slot. An instance whose `E` is `never` is compiled as a
   function that does not throw.

## 9. Panics and `never`

1. A **panic** is no error: nothing throws it and no clause takes it. It ends the program with
   its report and the exit code 101, and no `defer` and no `using` close runs past it (05 E8) —
   the report and the codes are the runtime's ([13 §1.4](13-abi.md#14-panics-and-crashes)).
   Besides the runtime's checks, a program panics through four functions of `std.core`, in scope
   without an import: `panic(message): never` (`LYR-RT0008`); `assert(condition, message =
   "assertion failed")`, which panics with `LYR-RT0011` when the condition is false — the message
   an argument like any other, evaluated before the test; `unreachable(message = "entered
   unreachable code"): never` (`LYR-RT0012`); and `todo(message = "not implemented yet"): never`
   (`LYR-RT0013`).
2. **`never`** is the type of what gives no value (05 E12): a `throw`, a call of a function that
   returns `never` — `panic`, `unreachable`, `todo` among them — a `loop` no `break` leaves
   ([07 §1](07-statements.md#1-loop-and-the-jumps)), an `if` or `match` whose every branch is
   one, and an operator over one alone. It **fits every type** where a value is wanted,
   an operand included: `let n: int = found ?? unreachable();`, and `ok || fail("why")` is a
   `bool`.
3. `never` is written **only as a return type**: the whole return type of a function, a lambda or
   a function type, `fn fail(m: string): never`. Anywhere else — a parameter, a binding, a field,
   an element, an optional, a type argument, a thrown set, an alias — it would type a value that
   cannot exist and is refused (`LYR-SEM0145`); `?never` and `never[]` are refused in a return
   position too. `try?` over an expression of type `never` would be worth `?never` and is refused
   the same way.
4. A function that returns `never` **does not return**: every path ends in a `throw`, a panic, a
   call that does not return or a `loop` no `break` leaves (`LYR-SEM0017` otherwise), and a
   `return` in it is refused unless what it returns does not return either (`LYR-SEM0146`).

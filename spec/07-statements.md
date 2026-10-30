# 7. Statements

**Base.** Lyric 5.0 [§7](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/07-statements.md) applies, with the deviations below.

**Status.** The core (S2), definite assignment (S3) and the loops and jumps (S4) written; the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

## Written (S2, the core)

1. **The script's code.** The statements of a module are its code, run in their order
   ([07 Top](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). Its outermost `let` and `var` are
   the module's bindings: every function of the module sees them. `return` outside a function is
   refused (`LYS-SEM0902`): a script ends at its end, or with `exit(n)`.
2. As in Lyric 5, an expression stands alone as a statement only where it does something — a
   call, an assignment, a loop (`LYS-SEM0022`).

## Written (S3, definite assignment)

3. **Definite assignment** is Lyric 5's (§1 rule 5): a `var x: T` without a value is read only
   where it is assigned on every way to the read (`LYS-SEM0018`). A branch that does not come
   out — it returns, breaks, continues or gives `never` — adds nothing to what follows; a `while`
   and a `for` may not run their block; a `loop` is assigned after it what each of its breaks
   has assigned; the right side of `&&`, `||` and `??`, the value of `??=` and the arguments
   after `?.` may not be evaluated, and what they assign does not count. A clause of a `try`
   may run after any part of its body: it knows assigned only what was before the `try`, and
   after the `try` a binding is assigned where the body and every clause assign it
   ([06](06-errors.md) rule 2). A `do … while` runs its block at least once: its condition knows
   what the block assigned, and after it a binding is assigned where the condition's way and every
   `break` assign it (rule 5). A `let` declared without a value is never written
   (`LYS-SEM0019`), as in Lyric 5.
4. **A global of the script takes its value where it is declared** (`LYS-SEM0903`): a function
   may run, and read it, before any statement of the script's code assigns it.

## Written (S4, loops and jumps)

5. **Loops and their labels** (Lyric 5 §1 rules 1–4). `loop { … }` is worth what its breaks give,
   `never` where nothing leaves it; a value leaves only a `loop` (`LYS-SEM0148`), all its breaks
   or none (`LYS-SEM0149`). **`do { … } while (c)`** runs its block, then the condition; a
   `continue` goes to the condition. A label names a loop — `outer: for (…)`, `outer: while`,
   `outer: do`, `outer: loop`, before a `loop` where a value stands too — and `break outer`,
   `break outer value` and `continue outer` leave or continue it from a loop nested in it. After
   `break` a name is the label where a loop around carries it, and the value's start otherwise.
   A jump to a label no loop around carries is refused (`LYS-SEM0101`) — a lambda's body is a
   function of its own —, a label repeating one around it too (`LYS-SEM0102`); a label nothing
   jumps to is warned about (`LYS-SEM0103`).

## Written (S7, the core collections)

6. **`for` over a list** visits its elements in order from the first. The binding is fresh for
   each element — a closure keeps the element it saw —, and `break` and `continue` work as in
   every loop. A change of the list's length while the loop walks it — a push, a pop, an
   insert, a removal — makes the next step panic, `LYS-RT0016` (Lyric 5's `List` iterator);
   writing an element is no change.
7. **`for` over an Iterator or an Iterable** (Lyric 5 §1; S7c4a). The prelude declares
   `interface Iterator { type Item; fn next(): ?Self.Item }` — without Lyric 5's error type
   ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md): every call may throw) — and `interface Iterable { type Iter :: [Iterator];
   fn iter(): Self.Iter }`. `for (x in e)` over an `Iterator` pulls `e.next()` until it gives
   `null`, `e` evaluated once; over an `Iterable` it pulls the iterator `e.iter()` gives. Where
   the iterator is a `Closeable` it is closed at every way out of the loop — its end, a `break`,
   a `return`, an error (05 E7). Over a value that is neither: `LYS-SEM0007`. A list, a range
   and a coroutine are walked as rules 6 and §10 say.

## Deviations (skeleton, written with later milestones)

- No `mut fn`; class methods write `var` fields without a marker ([03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).

**Conformance.** `conformance/cases/07-statements/` (`since: 1.0.0`).

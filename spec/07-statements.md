# Statements

> **Skeleton.** Written with milestone **M2/M3** of the Lyric 5 plan, spec-first: each rule lands
> here with its conformance case before or with its implementation. Source of the decisions:
> [08 Syntax](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md).

## Scope

Bindings, blocks, `if`, `while`, `loop`, `for` over `Iterable` (with `try` for throwing iterators), labels, `break`/`continue`/`return`.

## 1. `loop` and the jumps

1. **`loop { … }`** runs its block again and again; only a `break` leaves it (05 E11, 08 S3). At
   the start of a statement it is the statement, with no `;` after its block; anywhere else it is
   an expression — `let found = loop { … };`, `return loop { … };`. `loop` is a word only before
   its `{`: elsewhere it is a name like any other, and before a `{` it is always the loop.
2. A loop is worth what its **breaks** give (05 E11, 08 S4): `break value;` leaves it with the
   value, and the loop's type is the values' types unified, or the type its position expects,
   each value checked against it — `let n: ?int = loop { break null; };`. A loop whose breaks
   give no value is worth nothing (`void`); a loop no `break` leaves is worth **`never`**
   ([06 §9.2](06-errors.md#9-panics-and-never)) — a function whose body ends in one needs no
   `return`, and the loop fits where any value is wanted. The breaks of one loop give a value all
   or none (`LYR-SEM0149`). A value leaves **only a `loop`**: `while`, `do` and `for` also end
   when their condition or their elements run out, and there would be no value then
   (`LYR-SEM0148`).
3. **Labels**: `outer: loop { … }`, `outer: while (…) { … }`, `outer: do { … } while (…);` and
   `outer: for (…) { … }` name the loop, and `break outer;`, `break outer value;` and
   `continue outer;` leave or continue it from a loop nested in it. After `break`, a name is the
   label when a loop around the `break` carries it, and the beginning of the value otherwise:
   `break x;` gives `x` unless a loop around is labeled `x`, and `break (x);` gives `x` whatever
   it names. A jump to a label no loop around carries is refused (`LYR-SEM0101`), as is a label
   repeating one around it — a jump to it would be ambiguous (`LYR-SEM0102`); a label nothing
   jumps to is warned (`LYR-SEM0103`). Labels share nothing with the names of values.
4. A `break` or `continue` leaves or continues a loop **of its own function**: outside every loop
   it is refused (`LYR-SEM0147`). A lambda's body is a function of its own — the loops around the
   lambda are out of its jumps' reach, and their labels name nothing in it.
5. **Definite assignment** follows the jumps. A branch of an `if` or an arm of a `match` that does
   not complete — it returns, throws, breaks, continues or gives `never` — adds nothing to what
   follows it: the continuation follows the branches that complete. A `loop` runs its block at
   least once and is left only by its breaks: a variable is assigned after it when it is assigned
   at every `break` that leaves it. A `do … while (c)` runs its block at least once, reaches `c`
   from the end of the block and from every `continue`, and is left where `c` is false and by
   every `break`. A `while` and a `for` may not run their block at all: what is assigned after
   them is what was assigned before. A read of a variable that is not assigned on every way to it
   is refused (`LYR-SEM0018`).
6. **The end of a body** follows the jumps too. A function that returns a value ends every path
   in a `return`, a `throw` or an expression worth `never`
   ([06 §9](06-errors.md#9-panics-and-never)); a body that can run off its end is refused
   (`LYR-SEM0017`). A loop ends a path only when nothing leaves it: a `while (true)` or a
   `do … while (true)` with no `break` of it, and a `do` loop whose block ends every path so and
   holds no `break` and no `continue` of the loop — a `break` is a way past what follows it, and
   a `continue` reaches the condition, which may end the loop. A jump is its loop's **wherever
   it stands in the loop's block**: in a nested statement, in the `else` of a `let … else`, in
   an arm of a `match` expression or a clause of a `try` expression that is part of a larger
   expression — and, when it names the loop's label, in a loop nested in it, a `loop` worth
   `never` included. Only a lambda's body is out of reach (rule 4). A statement no path reaches
   is warned about (`LYR-SEM0073`); the statement behind a loop a jump leaves is reached.

## 2. `for`

1. **`for (x in e) { … }`** walks an **`Iterable`** (design 10 B6 I2): `e.iter()` gives the
   iterator, once, and the loop calls its `next()` before every pass, running the block with `x`
   bound to the value until `next()` answers `null`. Anything else is refused (`LYR-SEM0007`).
   An `Iterator` is iterable as itself ([12 §Iteration](12-stdlib.md)), its `iter()` the iterator
   as a value: a loop over a struct iterator walks a copy and leaves the variable where it was;
   over a class iterator it walks the object, and a second loop goes on where the first stopped.
2. `x` is the iterator's **`Item`**; a pattern takes it apart, `for ((k, v) in …)`, where it
   cannot fail (`LYR-SEM0098`). An `Item` may itself be optional: `next()` then answers `??T`
   ([03 §3.1](03-types.md)), and a `null` of the inner level is a value the loop runs for. Two
   loops over one `Iterable` value each take an iterator of their own — `iter()` is called per
   loop.
3. A range written in the head is the counted loop ([03 §7](03-types.md) rule 2); a range held
   in a binding is an iterator like any other.
4. A loop over a binding — a local or a parameter — that an **earlier loop walked** warns
   (`LYR-SEM0162`, design 10 B6 I2) where the binding's `iter()` gives the iterator itself, the
   iterator may be an object other bindings reach — a class, or a type parameter or associated
   type a class may answer —, and the earlier loop stands before it in the same block or an
   enclosing one with no assignment to the binding between: the second loop goes on where the
   first stopped (rule 1). A struct iterator is walked as a copy and warns not, nor does an
   `Iterable` whose `iter()` makes a new iterator, nor a loop after one in a branch that may not
   have run.
5. Over an **array, a view or an inline array** the loop is the **index loop** (design 10 B6
   I10): the sequence is evaluated once — an inline array copied, as a binding copies it — and
   the element at each index below its length is read at its pass, so a write to a later
   element of an array or a view is seen, and a new array assigned to the variable is not. No
   iterator stands between: an element that is itself optional walks. An array and a view are
   `Iterable` besides, through `SliceIter<T>` ([12 §Iteration](12-stdlib.md)), for what takes
   an `Iterable`; an inline array is not, as a view of a local one is refused
   ([03 §5.3](03-types.md) rule 4).
6. An iterator that **may throw** — its `Error` is not `never` (design 10 B6 I5) — makes the
   loop's calls throw sites at its head, `iter()` once and `next()` at every pass: the head is
   marked, **`for (line in try lines)`**, the `try` covering the source and every pull
   (`LYR-SEM0138` without it), and what they throw is covered as a call's is
   ([06 §3](06-errors.md)) — by a `try` block around the loop or by the function's set. Through
   a constraint the `Error` is open: a loop over `A :: [Iterable]` throws `A.Iter.Error`, which
   the function declares, and a call where it is `never` throws nothing. A mark over a loop that
   cannot throw is warned about (`LYR-SEM0139`). Only the plain mark stands in a head
   (`LYR-SEM0163`): `try?`, `try!` and the catching form would take the head's value and leave
   the pulls outside.
7. A loop over an iterator that is **`Closeable`** — by its type, or by its constraints —
   **closes** it on every way out but a panic (design 10 B6 I6, 05 E7 R7), as a `using` binding
   closes what it binds: at its end, at `break`, at `return`, and when something in it throws;
   `continue` stays inside. The `close()` is a call of the loop's, marked by its head's `try`
   where it may throw (rule 6). Through a constraint that does not say `Closeable` the loop does
   not close.

## 3. Value blocks

1. A **value block** is a block that is worth a value, `{ …; v }`: statements, and last a
   **tail** — written without a `;`. It stands where the grammar puts one and nowhere else
   ([08 Y4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)): as the
   body of a lambda, as a block arm of a `match`, as a clause of a `try` expression
   ([06 §6](06-errors.md#6-the-expression-forms)), as a branch of an `if` expression and as the
   right of `??` ([08 §2](08-expressions.md#2-if-and-match-as-values)). A brace anywhere else in
   an expression is an initializer's or a trailing lambda's: there is no block expression as
   such.
2. The tail is an expression — or an **`if` with its `else`, a `match` or a `loop` standing
   last**: there the three are worth what they are worth as expressions (the tail rule). Before
   the end of the block, and in every block that is no value block — a function's body, a
   loop's, the branches of an `if` statement — they are statements, and a value without `;` in a
   statement block is refused (`LYR-PAR0016`). An `if` without a final `else` is a statement
   wherever it stands, and so is one whose condition binds, `if (let …)`. The form without
   braces, `if (c) a else b`, is an expression everywhere.
3. A value block is **worth its tail's value**. Without a tail it gives no value: it is worth
   `never` where every path through it leaves — by `return`, `throw`, `break`, `continue` or an
   expression worth `never` ([06 §9](06-errors.md#9-panics-and-never)) — and **nothing** where
   it runs to its end. A block worth nothing stands where nobody takes a value; where the
   position wants one, or beside a branch or an arm that gives one, it is refused
   (`LYR-SEM0033`, or the branches do not unify, `LYR-SEM0016`).
4. A value block is a **scope**: its bindings end with it, and its `defer`s run when it ends —
   after the tail's value is taken.
5. A lambda's block is a value block in each of its forms: `(x) => { … }`, `x => { … }`, a
   trailing `{ x => … }`, and a trailing block that holds statements, `{ let d = it * 2; d + 1 }`.
   Its tail is the lambda's result, as `return tail;` at its end would be; a lambda nobody takes
   a value from may end in a tail worth nothing.

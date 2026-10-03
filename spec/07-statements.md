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

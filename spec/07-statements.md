# 7. Statements

**Base.** Lyric 5.0 [§7](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/07-statements.md) applies, with the deviations below.

**Status.** The core (S2) and definite assignment (S3) written; the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

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
   after `?.` may not be evaluated, and what they assign does not count. Script has no `do`
   loop and no `try` yet; their rules come with them. A `let` declared without a value is never
   written (`LYS-SEM0019`), as in Lyric 5.
4. **A global of the script takes its value where it is declared** (`LYS-SEM0903`): a function
   may run, and read it, before any statement of the script's code assigns it.

## Deviations (skeleton, written with later milestones)

- No `mut fn`; class methods write `var` fields without a marker ([03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).

**Conformance.** `conformance/cases/07-statements/` (`since: 1.0.0`).

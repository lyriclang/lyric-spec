# 7. Statements

**Base.** Lyric 5.0 [§7](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/07-statements.md) applies, with the deviations below.

**Status.** The core written (S2); the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

## Written (S2, the core)

1. **The script's code.** The statements of a module are its code, run in their order
   ([07 Top](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). Its outermost `let` and `var` are
   the module's bindings: every function of the module sees them. `return` outside a function is
   refused (`LYS-SEM0902`): a script ends at its end, or with `exit(n)`.
2. As in Lyric 5, an expression stands alone as a statement only where it does something — a
   call, an assignment, a loop (`LYS-SEM0022`).

## Deviations (skeleton, written with later milestones)

- No `mut fn`; class methods write `var` fields without a marker ([03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).

**Conformance.** `conformance/cases/07-statements/` (`since: 1.0.0`).

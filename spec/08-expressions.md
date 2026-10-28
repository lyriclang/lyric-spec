# 8. Expressions

**Base.** Lyric 5.0 [§8](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/08-expressions.md) applies, with the deviations below.

**Status.** The core written (S2); the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

## Written (S2, the core)

1. **Mixed arithmetic.** An arithmetic operation or a comparison with an `int` and a `float`
   operand widens the `int`; `int / int` stays the integer division
   ([03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)). `+` joins two strings; it joins nothing else to a string
   (`LYS-SEM0003`) — an f-string does.
2. **`as`** converts between `int`, `float` and `char` alone (`LYS-SEM0006`).

## Deviations (skeleton, written with later milestones)

- Mixed `int`/`float` arithmetic widens to `float`; `int / int` stays integer division; `as` only between `int`, `float` and `char`; no prefix `&`, no `comptime` ([03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [09](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).

**Conformance.** `conformance/cases/08-expressions/` (`since: 1.0.0`).

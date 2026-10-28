# 8. Expressions

**Base.** Lyric 5.0 [§8](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/08-expressions.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- Mixed `int`/`float` arithmetic widens to `float`; `int / int` stays integer division; `as` only between `int`, `float` and `char`; no prefix `&`, no `comptime` ([03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [09](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).

**Conformance.** `conformance/cases/08-expressions/` (`since: 1.0.0`).

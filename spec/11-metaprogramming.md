# 11. Metaprogramming and reflection

**Base.** Lyric 5.0 [§11](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/11-metaprogramming.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- No `comptime`, no macros, no `inline fn` ([02 W](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md)).
- Read-only reflection at run time; function values as `Any`; data attributes readable at run time; the closed compiler-attribute list without `@When`, `@Export` and the inline hints ([09 Rf, At](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).

**Conformance.** `conformance/cases/11-metaprogramming/` (`since: 1.0.0`).

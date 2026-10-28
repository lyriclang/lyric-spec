# 7. Statements

**Base.** Lyric 5.0 [§7](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/07-statements.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- No `mut fn`; class methods write `var` fields without a marker ([03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).

**Conformance.** `conformance/cases/07-statements/` (`since: 1.0.0`).

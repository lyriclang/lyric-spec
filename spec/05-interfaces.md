# 5. Interfaces

**Base.** Lyric 5.0 [§5](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/05-interfaces.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- Synthesis from the compiler's fixed list; derivable interfaces of one's own through reflection in default bodies ([05 Syn](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- A struct becomes an interface value shared, not copied; `Clone` matters for classes ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).

**Conformance.** `conformance/cases/05-interfaces/` (`since: 1.0.0`).

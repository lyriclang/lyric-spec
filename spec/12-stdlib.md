# 12. Standard library contract

**Base.** Lyric 5.0 [§12](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/12-stdlib.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- Lyric 5's API adapted to Lyric-Script's types, plus the batteries `cli`, `csv`, `log`, `fs.glob`, and `reflect`; no `sync`, `thread`, `ffi`, `meta`, `syntax`, `build` ([12](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).

**Conformance.** `conformance/cases/12-stdlib/` (`since: 1.0.0`).

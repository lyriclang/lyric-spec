# 6. Errors

**Base.** Lyric 5.0 [§6](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/06-errors.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- Thrown sets are inferred; a written `throws` is a checked contract; `try` is accepted without effect; lint `unmarked-throw` ([02 K2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [05 Th](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- Function types carry no `throws`; iterators have no error type ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- An error that escapes the top level ends the script with exit 1; embedded it is `.Error` at the host ([05 E6](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md), [01 S11](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).

**Conformance.** `conformance/cases/06-errors/` (`since: 1.0.0`).

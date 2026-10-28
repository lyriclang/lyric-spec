# 4. Modules

**Base.** Lyric 5.0 [§4](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/04-modules.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- A module's statements are its `main`; only the entry module runs them ([07 Top](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).
- Without a manifest the entry script's folder is the root, without prefix ([07 Path](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).
- Public by default, `private` per file; `pub` and `internal` accepted; the prelude adds `print`, `println`, `eprintln`, `readLine`, `args`, `exit`; global initializers may throw ([02 V](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [07](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).

**Conformance.** `conformance/cases/04-modules/` (`since: 1.0.0`).

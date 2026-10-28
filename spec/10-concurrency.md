# 10. Concurrency

**Base.** Lyric 5.0 [§10](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/10-concurrency.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- No threads, `Mutex` or `Atomic`; one scheduler per instance; `Semaphore` guards sections across waits ([02 W](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [07](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).
- The top-level code is a `TaskScope` ([07 End](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).

**Conformance.** `conformance/cases/10-concurrency/` (`since: 1.0.0`).

# Cases

One directory per chapter, one `.lyr` per rule, named after the sentence it pins. Every case
carries `//! since: 5.0.0` or later; the 4.x suite lives on the `script` branch.

| Directory | Chapter | Written with |
|---|---|---|
| `03-types/` | [03 Types and values](../../spec/03-types.md) | M3 S1–S8, and on |
| `04-modules/` | [04 Modules and packages](../../spec/04-modules.md), the module-level bindings | M3 S6 |
| `05-interfaces/` | [05 Interfaces and conformance](../../spec/05-interfaces.md) | M4 |
| `06-errors/` | [06 Errors](../../spec/06-errors.md) | M5 S1–S4 |
| `07-statements/` | [07 Statements](../../spec/07-statements.md) §1, `loop` and the jumps | M5 S4c |
| `08-expressions/` | [08 Expressions](../../spec/08-expressions.md) §1, calls | M4 S2 |
| `09-patterns/` | [09 Patterns](../../spec/09-patterns.md) | M3 S4 |
| `10-concurrency/` | [10 Concurrency](../../spec/10-concurrency.md) §1, coroutines and generators | M6 S2a |

The reference runner drives `lyric5` — `python3 tools/run_conformance.py --lyric5 <compiler>
--profile debug` (or `release`) builds every case and compares it with its header, as
[the format](../README.md) says. `lyriclang/lyric` runs the suite in its CI against every commit,
in both profiles; until a 5.0 toolchain is released, this repository's own CI reads the headers
only (`--parse-only`).

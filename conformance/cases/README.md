# Cases

One directory per chapter, one `.lyr` per rule, named after the sentence it pins. Every case
carries `//! since: 5.0.0` or later; the 4.x suite lives on the `script` branch.

| Directory | Chapter | Written with |
|---|---|---|
| `03-types/` | [03 Types and values](../../spec/03-types.md) §1, the scalars | M3 S1 |

Until the reference runner drives `lyric5` (a slice of M3), the cases are run by hand with
`lyric5 build` and the binary: a `check` case with `error:` must be refused (exit 1) naming
the code, a `check` case without one must compile in silence, a `run` case must exit and print
as its header says, and a `panic:` case must exit 101 with `panic [CODE]` on its first line.

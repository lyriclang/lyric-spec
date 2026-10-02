# The Lyric Language Specification

**Status: Lyric 5.0 — skeleton, written milestone by milestone.** The Lyric 4.x text (normative
from 2.0 to 4.6) lives on the [`script`](https://github.com/lyriclang/lyric-spec/tree/script)
branch, where it goes on as the specification of
[Lyric-Script](https://github.com/lyriclang/lyric-script).

This repository holds the specification of the Lyric programming language and its conformance
suite: a document from which a second, independent implementation can be built — and a suite
that tells it whether it succeeded. The relationship stays as it was since 2.0: the
specification defines the language, the toolchain implements it, and a divergence is a
toolchain bug. A change to observable behavior is a specification change FIRST.

The decisions this text writes down were made in the Lyric 5 design round:
[`lyric/design/v5/spec`](https://github.com/lyriclang/lyric/tree/main/design/v5/spec). The
chapters below cite the document each rule comes from; the specification carries the rule, the
design documents carry the reasoning and what was rejected.

## Layout

| Path | Content | Milestone |
|---|---|---|
| `spec/01-lexical.md` | tokens and literals | M2/M3 |
| `spec/02-grammar.md` | the canonical EBNF | M2–M9b |
| `spec/03-types.md` | types and values | M3 |
| `spec/04-modules.md` | modules and packages | M7 |
| `spec/05-interfaces.md` | interfaces and abstraction | M4 |
| `spec/06-errors.md` | errors | M5 |
| `spec/07-statements.md` | statements | M2/M3 |
| `spec/08-expressions.md` | expressions | M2/M3 |
| `spec/09-patterns.md` | patterns | M3 |
| `spec/10-concurrency.md` | concurrency | M6 |
| `spec/11-metaprogramming.md` | metaprogramming | M9a/M9b |
| `spec/12-stdlib.md` | the standard library contract | M8a–M10 |
| `spec/13-abi.md` | the C ABI and embedding | M1/M14 |
| `spec/14-cli.md` | the command line | M2–M13 |
| `spec/15-project.md` | projects | M7 |
| `spec/16-diagnostics.md` | diagnostics | M12 |
| `spec/appendix-a-diagnostics.md` | the catalogue — generated | M12 |
| `conformance/` | the suite: one `.lyr` — or one package — per case, expectations in a `//!` header | — |
| `tools/run_conformance.py` | the reference runner | — |

## Versioning

The specification describes a **language version**: this text describes Lyric 5.0 as it is
written. A case carries `//! since: X.Y.Z` and applies to that version and later.

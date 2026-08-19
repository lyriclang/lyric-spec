# The Lyric Language Specification

**Status: DRAFT — non-normative until Lyric 2.0.**

This repository holds the specification of the Lyric programming language and its conformance
suite. The goal is the same one `Bytecode.md` reached for the module format: a document from
which a second, independent implementation can be built — and a suite that tells it whether it
succeeded.

Until 2.0 the toolchain implementation is the authority and this document describes it. At 2.0
the relationship inverts: the specification becomes normative, the toolchain implements it, and
a divergence is a toolchain bug.

## Layout

| Path | Content |
|---|---|
| `spec/` | the specification, one numbered chapter per file |
| `conformance/` | the conformance suite: `.lyr` cases with expected outcomes |
| `conformance/README.md` | the manifest format and how to run the suite against a toolchain |

## Canonical sources during the draft phase

Two documents remain canonical in [`lyriclang/lyric`](https://github.com/lyriclang/lyric) until
this specification subsumes them at 2.0, because they are pinned there by tests:

- `docs/Grammar.md` — the EBNF grammar (pinned against the lexer and parser).
- `docs/Bytecode.md` — the `.lyrbc` module format (already normative on its own).

Chapters here reference them rather than duplicating them; duplication would drift.

## Versioning

The specification describes a **language version**, which is the toolchain's minor line: this
draft tracks Lyric 1.16. The semantics it describes are FROZEN — from 1.16 on, a change to
observable language behavior is a specification change first.

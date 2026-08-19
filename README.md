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
| `spec/01-lexical.md` | tokens, literals, escapes, contextual words |
| `spec/02-grammar.md` | the EBNF's home and the rules around it |
| `spec/03-types.md` | the type system; wrapping arithmetic; `as`; opaque aliases |
| `spec/04-modules.md` | modules, imports, visibility, capabilities |
| `spec/05-interfaces.md` | conformance, inheritance, interface values, extends |
| `spec/06-operators.md` | every operator as its interface method |
| `spec/07-statements.md` | bindings, loops, narrowing, lambdas, match |
| `spec/08-generics.md` | monomorphization and constraints |
| `spec/09-errors.md` | return values vs. throwables vs. panics |
| `spec/10-coroutines.md` | `Coroutine<T>`, `yield`, `resume` |
| `spec/11-stdlib-contract.md` | what of the library is LANGUAGE |
| `spec/12-diagnostics.md` | the code catalogue as contract |
| `conformance/` | the suite: one `.lyr` per case, expectations in a `//!` header |
| `tools/run_conformance.py` | the reference runner |

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

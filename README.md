# The Lyric Language Specification

**Status: NORMATIVE since Lyric 2.0.**

This repository holds the specification of the Lyric programming language and its conformance
suite: a document from which a second, independent implementation can be built — and a suite
that tells it whether it succeeded.

Since 2.0 the relationship stands inverted from the draft phase: the specification defines the
language, the toolchain implements it, and a divergence is a toolchain bug. A change to
observable language behavior is a specification change FIRST — the chapter sentence and its
conformance case land before or with the implementation, never after.

## Layout

| Path | Content |
|---|---|
| `spec/01-lexical.md` | tokens, literals, escapes, contextual words |
| `spec/02-grammar.md` | the canonical EBNF and the rules around it (mirrored in the toolchain) |
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
| `spec/13-bytecode.md` | the `.lyrbc` module format (canonical; mirrored in the toolchain) |
| `spec/appendix-a-diagnostics.md` | the catalogue itself: every code, severity, cause, and the retired numbers |
| `conformance/` | the suite: one `.lyr` per case, expectations in a `//!` header |
| `tools/run_conformance.py` | the reference runner |

## The mirror model

The grammar (chapter 02) and the bytecode format (chapter 13) are canonical **here**. The
toolchain repository carries byte-identical mirrors as `docs/Grammar.md` and
`docs/Bytecode.md` — its tests pin against them and its doc site publishes them — and its CI
diffs everything below the `<!-- sync:body -->` marker against these chapters. Duplication
would drift; a checked mirror cannot.

## Versioning

The specification describes a **language version**: this document describes Lyric 3.8. A case
in the suite may carry `//! since: X.Y.Z` and applies to that version and later, which is how
one suite serves every release since the freeze (1.16) without a manual deferral dance.

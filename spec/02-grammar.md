# 2. Grammar

The complete EBNF grammar of Lyric lives in
[`lyriclang/lyric` → `docs/Grammar.md`](https://github.com/lyriclang/lyric/blob/main/docs/Grammar.md)
and is **canonical there during the draft phase**: the toolchain's lexer and parser tests pin
it, so a drifting copy here would be the lie this repository exists to prevent. This chapter
subsumes it at 2.0; until then it states only what the EBNF alone does not.

## 2.1 Reading the grammar

- The grammar in `Grammar.md` is the contract: what it does not derive is not Lyric
  (`CONTRIBUTING.md` rule). Prose paragraphs beside the productions carry semantic rules and
  are as binding as the productions.
- Contextual words (`type`, `opaque`, `throws`) appear in productions as quoted literals but
  are not reserved (§1.1).

## 2.2 Precedence and associativity

Operator precedence is defined by §6.1 of `Grammar.md` as a numbered table; the formatter
re-derives parentheses from it, and a conforming implementation must reproduce that table
exactly. Notable: `&` binds tighter than `==` (unlike C).

## 2.3 Statement termination and blocks

Statements end with `;`. Blocks `{ … }` are statements and expressions per the productions;
`if`/`while`/`for`/`match` heads require parentheses around their condition or header.

## 2.4 Error recovery is not specified

How an implementation recovers from a parse error — what it synchronizes on, how many follow-up
diagnostics it emits — is quality of implementation, not conformance. Conformance requires only
that an ill-formed program is rejected with at least one diagnostic whose code the catalogue
(chapter 12) defines for the construct, and that a well-formed program parses to the tree the
grammar derives.

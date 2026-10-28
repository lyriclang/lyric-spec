# 2. Grammar

**Base.** Lyric 5.0 [§2](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/02-grammar.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- End of statement: the lexical rule with continuation rules ([09 NL](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).
- Accepted Lyric 5 forms with the same meaning (`;`, `throws`, `try`, `pub`, `internal`, `fn main`, `mut fn` on class methods); refused forms with a hint (`&x`, width types, `var` struct fields, `Slice`, `T[N]`, `comptime`, macros, `inline fn`, `unsafe`, `extern`, `@When`) ([09 Cmp](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).
- Top-level statements; map literal `[k: v]` and `[:]`; expression bodies `fn f(…) = e`; fields separated by line ends ([02](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [07 Top](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).

**Conformance.** `conformance/cases/02-grammar/` (`since: 1.0.0`).

# 1. Lexical structure

**Base.** Lyric 5.0 [§1](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/01-lexical.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- No statement terminator is required: line ends are tokens to the grammar (§2); `;` remains a separator ([09 NL](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).
- A file may open with a `#!` line and a frontmatter block between two `---` lines (TOML; dependencies only) ([09 Hd](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).
- `b"…"` denotes a `Bytes` value, not `uint8[]` ([02 T1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md)).
- Reserved and contextual words are Lyric 5's, including the ones Lyric-Script does not use, so names stay portable ([09 Y1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).

**Conformance.** `conformance/cases/01-lexical/` (`since: 1.0.0`).

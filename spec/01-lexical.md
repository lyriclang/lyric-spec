# 1. Lexical structure

**Base.** Lyric 5.0 [§1](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/01-lexical.md) applies, with the deviations below.

**Status.** Written (S2). Source of the decisions: [09 NL, Hd, Y1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md),
[03 K3](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md),
[02 T1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md).

## Deviations

### D1. The line end

1. A line feed is a **line end token** where it ends a statement; elsewhere it is whitespace, as in
   Lyric 5. The rules decide with the tokens around it alone, in this order:
   1. inside `( )` and `[ ]` — the innermost open bracket is one of them — a line end is
      whitespace; inside `{ }` the rules apply again;
   2. after a token that asks for more — a binary operator but `>` and `>>`, `=` and every
      compound assignment, `,`, `.`, `?.`, `=>`, `->`, `::`, `(`, `[`, `{` — it is whitespace.
      `>` and `>>` also close type arguments (`let xs: List<int>`), so a line end after them ends
      the statement; a comparison continued on the next line puts `>` there (rule 3);
   3. before a token no statement starts with — `.`, `?.`, `)`, `]`, the words `else` and
      `catch`, and the operators `*` `/` `%` `*%` `&&` `||` `??` `==` `!=` `<` `>` `<=` `>=`
      `<<` `>>` `..` `..=` `|` `&` `^` `!in` — it is whitespace;
   4. otherwise it ends the statement. When the next line starts with `+` or `-`, these start a
      new statement, as signs, and the toolchain warns (`LYS-LEX0101`).
2. Line ends after one another are one; a line end before the first token, or right after `;`,
   is none. Comments are whitespace to these rules, doc comments included.
3. `;` remains a separator wherever a line end ends a statement ([§2](02-grammar.md)).

### D2. The head of a script

1. A byte order mark is no part of the source (as in Lyric 5). A first line starting `#!` is
   skipped.
2. A line that is exactly `---` — trailing blanks aside — as the first line, or the first after
   the `#!` line, opens the **frontmatter**: the lines up to the next `---` line, both included,
   are one token whose text between the two lines is TOML (the dependencies,
   [15](15-project.md)). Without a closing line the script is refused (`LYS-LEX0100`). Elsewhere
   `---` is the operators `--` and `-`.

### D3. Literals

1. A number takes **no suffix**: letters after its digits are refused (`LYS-LEX0003`) — the
   literal is `int` or `float` by its form ([§3](03-types.md)). The suffix rules of Lyric 5 §4.1
   rule 1 and §4.2 do not apply.
2. `b"…"` denotes a `Bytes` value, not a `uint8[]` ([§3](03-types.md)); its text is Lyric 5
   §4.5's.

### D4. Words

1. The reserved words, the contextual words and the builtin type names are Lyric 5's (§3),
   including those Lyric-Script gives no meaning — a name stays portable between the two
   languages. A width type name (`int8` … `uint64`, `float32`, `float64`, `uint`) is refused where
   it is used ([§3](03-types.md)).

### D5. Diagnostics

1. The lexical codes carry the prefix `LYS-`. A code below `LYS-LEX0100` means what Lyric 5's
   `LYR-LEX` code of the same number means; from 0100 on the codes are Lyric-Script's own.

**Conformance.** `conformance/cases/01-lexical/` (`since: 1.0.0`).

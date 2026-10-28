# 2. Grammar

**Base.** Lyric 5.0 [§2](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/02-grammar.md) applies, with the deviations below; the
forms of expressions and statements are Lyric 5's
([§7](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/07-statements.md),
[§8](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/08-expressions.md)) — the precedence table, comparisons
and ranges that do not chain, a `-` that belongs to the number right after it.

**Status.** The core written (S2): D1–D6. D7 lists what later milestones write. Source of the
decisions: [09 NL, Ret, Cmp, Y2, Y7](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md),
[02 L](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md),
[07 Top](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md).

## Deviations

### D1. Statement ends

1. A statement ends at a line end token ([§1](01-lexical.md) D1), at `;`, or before the `}` or
   the end of the file that closes it. Anything else after a whole statement is refused
   (`LYS-PAR0001`).
2. Where a body follows a header — after `if (…)`, `while (…)`, `for (…)`, `else`, a function's
   signature, a type's name — line ends before its `{` are whitespace.

### D2. A module is declarations and statements

1. A module is a sequence of **items**: declarations (`fn`, `struct`, `class`, `enum`,
   `type Name = T`) and statements, in any order; its statements are the script's code
   ([07 Top](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). A visibility word stands before a declaration
   only (`LYS-PAR0053`).
2. A function's body is a block, or **`= expression`** after the signature: `fn twice(x: int) =
   x * 2` (09 Ret).

### D3. Members end at line ends

1. The fields of a struct or a class, the variants of an enum and the fields of an initializer
   end at `,` or at a line end (09 Y2). Two fields on one line without `,` are refused
   (`LYS-PAR0029`); a variant is a name, and anything after it but `,` or a line end is refused
   (`LYS-PAR0001`).
2. An enum's methods follow its variants without `;`: a method starts with its words. An enum
   holds no field (`LYS-PAR0901`).

### D4. Initializers

1. A name that begins with a capital letter, followed by `{`, opens an **initializer**:
   `Point { x = 1, y = 2 }`, `Point { x, y }`; after any other name the brace is a block's.
   Lyric 5 tells the two apart by what ends the first value, `;` or `,`; a line end ends both
   here, so the form of the name decides.

### D5. Collection literals

1. `[a, b]` is a list, `["a": 1, "b": 2]` a map, `[:]` the empty map, `[]` the empty list
   ([02 L](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md)). An entry of a map without `:` is refused (`LYS-PAR0902`).

### D6. Bounds and codes

1. The parser refuses nesting deeper than its bound (`LYS-PAR0045`), at least **64** levels of
   expressions, blocks and prefix operators — Lyric 5's floor is 128 levels on a thread; a
   script is compiled on a task's stack as well.
2. A code means what Lyric 5's `LYR-PAR` code of the same number means; Lyric-Script's own
   codes start at 0900 (§16). `LYS-PAR0900` is a digit beyond its literal's
   base (`0b12`).

### D7. Written with later milestones

- Accepted Lyric 5 forms with the same meaning (`throws`, `try`, `pub`, `internal`, `fn main`,
  `mut fn` on class methods) and refused forms with a hint (`&x`, width types, `var` struct
  fields, `Slice`, `T[N]`, `comptime`, macros, `inline fn`, `unsafe`, `extern`, `@When`)
  ([09 Cmp](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)) — with the checker.
- Patterns, lambdas and trailing blocks, generics, interfaces, `match`, labels — with the
  milestones of the plan that build them.

**Conformance.** `conformance/cases/02-grammar/` (`since: 1.0.0`).

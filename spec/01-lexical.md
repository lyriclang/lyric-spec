# Lexical structure

The tokens of a source file — what separates them, the names and the words, the literals and the
comments. Source of the decisions: [08 Syntax](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md) Y1 (the words), Y7 (the literals), Y8 (the
comments).

## Scope

Source text, tokens, the reserved and contextual words, literals (integer, float, char, string,
raw, multi-line, byte strings, f-strings), comments and doc comments.

## 1. Source text

1. A source file is UTF-8 text; a byte order mark at its start is no part of it. A line ends at a
   line feed, or at a carriage return and a line feed — a string over lines (§4.4 rule 3) has
   `\n` between its lines either way.
2. Tokens are separated by whitespace — space, tab, line feed, carriage return — and by comments
   where one would otherwise run on into the next; the longest token that fits is taken: `>>=` is
   one token, `a-b` three. A list of type arguments closes on a `>` the lexer read as part of
   `>>`, `>=` or `>>=` ([03 §9](03-types.md)): the parser takes it apart.

## 2. Comments

1. `//` begins a comment that runs to the end of its line. `/* … */` is a comment that may run
   over lines, and **nests**: `/* a /* b */ c */` is one comment.
2. `///` begins a **doc comment** of the declaration that follows — a function, a type, a field, a
   variant — in Markdown ([11](11-metaprogramming.md)); `//!` at the start of a file is the
   **module's** doc comment. Both are optional, and neither changes what the program means.

## 3. Names and words

1. A **name** begins with an ASCII letter or `_` and goes on with ASCII letters, digits and `_`. A
   character beyond ASCII stands in no name and is refused where it stands (`LYR-LEX0001`). `_`
   alone is the wildcard where a name would bind.
2. The **reserved words** are no names: `import as pub internal private static struct class enum
   interface extend fn mut let var if else while do for in is match break continue return yield
   defer try catch throw true false null this`. One where a name belongs is refused — the
   parser's error for a missing name, `LYR-PAR0020` for a binding, with a note that it is a word —
   and read as that name, so nothing further is reported about it.
3. The **contextual words** are names everywhere but at their place: `type` before a type alias,
   `opaque` before `type` (and refused there, [03 §10](03-types.md#10-aliases)), `throws` after a
   signature, `extern` before its ABI string, `sealed` before `interface`, `by` in a conformance
   list, `with` after an expression, `loop` before its `{` ([07 §1](07-statements.md#1-loop-and-the-jumps)),
   `using` before `let` or `var` ([06 §7](06-errors.md#7-closing-using)), and `comptime` before an
   expression. *(Informative.)* `inline`, `macro` and `quote` come with the compile-time forms
   (M9a).
4. `module` and `params` are names (08 Y1: they were Lyric 4's words). At their old places —
   `module a.b;` at the start of a file, `params xs: T[]` in a list of parameters — they are read
   as they were, to be refused with what replaced them: `LYR-RES0008` ([04 §2](04-modules.md)) and
   `LYR-SEM0024` ([08 §1.1](08-expressions.md#11-arguments)).
5. The builtin type names — `int`, `uint`, `float`, `int8` … `int64`, `uint8` … `uint64`,
   `float32`, `float64`, `bool`, `char`, `string`, `void`, `never`, `Self` — are names that no
   declaration takes ([03](03-types.md)).

## 4. Literals

### 4.1 Integers

1. An integer literal is decimal digits, or `0x` and hex digits, `0o` and octal digits, `0b` and
   binary digits. `_` may stand among and after the digits and means nothing: `1_000_000`, `0xFF`,
   `0o755`, `0b1010`. A suffix `i8`, `i16`, `i32`, `i64`, `u8`, `u16`, `u32` or `u64` gives the
   literal its type ([03 §1](03-types.md)); without one its position does.
2. A `-` directly before an integer literal belongs to it (08 Y7 L2): `-9223372036854775808` is
   `int`'s least value. Before parentheses the `-` is the operator, on the value inside them.
3. A literal beyond 64 bits is refused (`LYR-PAR0007`), and so is an unknown suffix
   (`LYR-PAR0006`).

### 4.2 Floats

1. A float literal is digits, a `.` and digits, or an exponent — `e` or `E`, an optional sign,
   digits —, or both: `1.0`, `2.5e3`, `1e-2`, `1_000.5`. A digit stands on both sides of the `.`:
   `1.` and `.5` are no float literals. A suffix `f32` or `f64` gives it its type.

### 4.3 Characters

1. A character literal is **one Unicode scalar value** between `'`, as written or escaped:
   `'a'`, `'😀'` (08 Y7 L3). None or two are refused (`LYR-LEX0008`).
2. The escapes are `\n`, `\r`, `\t`, `\\`, `\'`, `\"`, `\0` and `\u{…}` with one to eight hex
   digits naming a scalar value — at most `10FFFF`, no surrogate (`LYR-LEX0007` for any other
   sequence). `\xNN` is a byte's and refused here (§4.5 rule 2).

### 4.4 Strings

1. A string literal is text between `"` on one line, with the escapes of §4.3: `"tab\there"`. An
   unterminated one is refused (`LYR-LEX0009`).
2. A **raw string** takes no escape — a backslash is itself (08 Y7 L5): `r"C:\path\n"`. It ends
   at the first `"`; one opened with hashes, `r#"…"#`, ends at the first `"` followed by as many
   `#`, and holds quotes: `r#"say "hi""#`.
3. A **multi-line string** `"""…"""` (L6, Swift's rule): the text begins on the line after the
   opening `"""`, which ends its own line, and ends with the line before the closing `"""`, which
   stands on a line of its own (`LYR-LEX0014` for either). The closing line's indentation is taken
   off every line — a line indented less is refused (`LYR-LEX0015`), a blank one need not be. The
   lines are joined by `\n`; the line break before the closing `"""` is no part of the text.
   Escapes are resolved after the lines are read — an escaped `\n` is no line. `r"""…"""` is the
   raw form.

### 4.5 Byte strings

1. `b"…"` is a **`uint8[]`** of its bytes (08 Y7 L7), a new array each time it is evaluated: ASCII
   text, the escapes of §4.3 but `\u{…}`, and `\xNN`, any byte by two hex digits. A character
   beyond ASCII and `\u{…}` are refused (`LYR-LEX0012`): a byte string holds bytes, and they are
   written by their number.
2. `\xNN` is a byte's escape and stands in a byte string alone (L4): in a string, a character or an
   f-string it is refused (`LYR-LEX0013`) — a character is `\u{…}`.

### 4.6 f-strings

1. `f"…"` is text with **holes**, `{expr}` and `{expr:spec}` in the format language of
   [12 §2](12-stdlib.md#2-the-format-language); `{{` and `}}` are a brace. A hole stays on one line.
2. The prefixes combine (08 Y7 L8): `fr"…"` resolves no escape, `f"""…"""` runs over lines as
   §4.4 rule 3 says — a hole counts as text there, so a line that begins with one is indented as
   any other —, and `fr"""…"""` is both.

### 4.7 Words as literals

1. `true` and `false` are `bool`'s literals, `null` every optional's ([03 §3](03-types.md)).

## 5. Punctuation and operators

1. The punctuation: `(` `)` `[` `]` `{` `}` `,` `;` `:` `::` `.` `->` `=>` `@` `@[` `..` `..=`
   `...` `?` `?.` `??` `!`.
2. The operators: `+` `-` `*` `/` `%` `+%` `-%` `*%` `++` `--` `&` `|` `^` `~` `<<` `>>` `==` `!=`
   `!in` `<` `<=` `>` `>=` `&&` `||`, and the assignments `=` `+=` `-=` `*=` `/=` `%=` `+%=` `-%=`
   `*%=` `&=` `|=` `^=` `<<=` `>>=` `&&=` `||=` `??=`. What each means is
   [08 Expressions](08-expressions.md)'.

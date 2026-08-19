# 1. Lexical structure

A Lyric source file is UTF-8 text. The lexer turns it into a token stream; everything the parser
sees is defined here, and nothing below this chapter re-interprets characters.

Normative language: **must** binds the implementation; **is** states a fact an implementation
reproduces; a diagnostic code in parentheses names the error a conforming implementation reports
for the construct (the codes are contract; see chapter 12).

## 1.1 Identifiers and keywords

An identifier starts with a letter `a`–`z`, `A`–`Z` or `_`, and continues with letters, digits
or `_`. Identifiers are case-sensitive.

The reserved words are:

```
module import as pub
struct class enum interface extend
fn mut static let var params
if else while do for in match
break continue return yield resume defer
try catch throw
true false null
this
```

A reserved word must not be used as an identifier. Two words that LOOK reserved are not:
`type` and `opaque` are **contextual** — they introduce a type alias only in declaration
position (`[pub] [opaque] type Name = Type;`) and remain ordinary identifiers everywhere else.
`throws` and `testRoot`-style manifest keys are likewise not reserved words of the language.

## 1.2 Comments and documentation

Two comment forms exist:

- `// …` to the end of the line;
- `/* … */`, non-nesting, to the closing delimiter.

A line comment beginning `///` is a **documentation comment**. It binds to the declaration
directly below it, including a `module` header; a blank line between the last `///` line and the
declaration breaks the binding, while an ordinary `//` line between them does not. Documentation
comments have no semantic effect; tooling reads them.

Comments and whitespace are trivia: a conforming implementation must produce the same token
stream and the same program with or without them.

## 1.3 Integer literals

An integer literal is one of:

- decimal: `0`, `42`, `1_000_000`;
- hexadecimal: `0x` or `0X` followed by hex digits, e.g. `0x2545F4914F6CDD1D`;
- binary: `0b` or `0B` followed by `0`/`1` digits.

`_` may separate digits for readability. It must not directly follow the `0x`/`0b` prefix, must
not lead the literal, and carries no meaning.

An integer literal may carry a width suffix: `i8 i16 i32 i64 u8 u16 u32 u64`. Without a suffix
the literal has type `int` (64-bit signed). A literal whose value does not fit the suffixed
width is an error.

## 1.4 Floating-point literals

A floating-point literal is decimal digits, a `.`, and decimal digits: `3.5`, `0.25`. `_`
separators follow the integer rule. The suffixes `f32` and `f64` select the width; without a
suffix the type is `float` (IEEE 754 binary64). There is no exponent form in the lexical
grammar of this version.

## 1.5 Character literals

A character literal is `'…'` holding exactly one **code point** — a Lyric `char` is a Unicode
scalar value, never a UTF-16 unit. The escape sequences of §1.7 apply.

## 1.6 String literals

A string literal is `"…"`. Strings are immutable sequences of code points; the lexical form
carries no length limit and no embedded-NUL restriction beyond `\0` being an ordinary escaped
character.

An **interpolated string** is `f"…"`. Inside it, `{expr}` embeds an expression and
`{expr:spec}` formats it through the specifier `spec` (chapter 6 defines the desugaring; the
specifier language is the host's numeric format contract, applied invariantly). `{{` and `}}`
denote literal braces.

## 1.7 Escape sequences

Inside character and string literals the following escapes exist, and no others
(`LYR-LEX0007` otherwise):

| Escape | Meaning |
|---|---|
| `\n` `\t` `\r` | line feed, tab, carriage return |
| `\\` `\"` `\'` | the character itself |
| `\0` | U+0000 |
| `\xHH` | the code point of the two hex digits |
| `\uXXXX` | the code point of the four hex digits |

## 1.8 Operators and punctuation

The operator and punctuation tokens are exactly those the grammar (chapter 2) uses. Longest
match wins: `..=` lexes as one token, not `..` `=`; `::` never lexes as two `:`.

## 1.9 Line endings

`\n` and `\r\n` both end a line. The language attaches no semantics to line ends beyond
terminating `//` comments; statements end with `;`.

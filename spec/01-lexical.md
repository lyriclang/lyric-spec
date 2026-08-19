# 1. Lexical structure

A Lyric source file is UTF-8 text. The lexer turns it into a token stream; everything the parser
sees is defined here, and nothing below this chapter re-interprets characters. The productions
quoted here are §1 of the canonical grammar; this chapter adds the behavioral contract around
them.

Normative language: **must** binds the implementation; **is** states a fact an implementation
reproduces; a diagnostic code in parentheses names the error a conforming implementation reports
(chapter 12).

## 1.1 Identifiers and keywords

An identifier starts with `a`–`z`, `A`–`Z` or `_` and continues with those or digits — ASCII
only, case-sensitive. `@` followed by an identifier is one token (an attribute name); a bare `@`
is an error (`LYR-LEX0012`).

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

`type`, `opaque` and `throws` look reserved and are not: they are **contextual**, recognized
only in their declaration positions, and remain ordinary identifiers everywhere else.

## 1.2 Whitespace, comments, documentation

Whitespace is space, tab, `\r`, `\n`. Statements end with `;`; line ends carry no semantics
beyond terminating line comments.

Comment forms:

- `// …` to the end of the line;
- `/* … */`, **nesting** — `/* a /* b */ c */` is one comment; an unclosed one is an error
  (`LYR-LEX0002`);
- `/// …` is a **documentation comment** — lexically its own token, not trivia: it binds to the
  declaration directly below it (a `module` header included). A blank line between the last
  `///` and the declaration breaks the binding; an ordinary `//` between them does not.

Comments and whitespace never change the token stream around them: a conforming implementation
compiles the same program with or without them.

## 1.3 Integer literals

```
IntLit = ( DecLit | HexLit | BinLit | OctLit ) [ IntSuffix ]
```

Decimal `42`, hexadecimal `0x2A`/`0X2A`, binary `0b101010`, octal `0o52` — prefixes accept
either case. `_` may separate digits anywhere after the first: it must not directly follow a
prefix (`LYR-LEX0005`), and a prefix must be followed by at least one digit (`LYR-LEX0004`).

The width suffixes are `i8 i16 i32 i64 u8 u16 u32 u64`, legal on every integer form; a float
suffix on a prefixed literal is an error (`LYR-LEX0003`). Without a suffix the literal's
DEFAULT type is `int` — but see §3.1: an unsuffixed integer literal adapts to a checked
context type when its value fits.

## 1.4 Floating-point literals

```
FloatLit = DecLit ( '.' DecLit [ Exponent ] | Exponent ) [ FloatSuffix ]
         | DecLit FloatSuffix
Exponent = ( 'e' | 'E' ) [ '+' | '-' ] DecDigit { DecDigit | '_' }
```

`3.5`, `1e9`, `2.5E-3`, `1f32` — a float suffix alone makes an integer-shaped literal a float,
and an exponent alone does too. The suffixes are `f32` and `f64`; an integer suffix on a float
shape is an error (`LYR-LEX0003`). Without a suffix the type is `float` (IEEE 754 binary64).
`1.` is not a float literal: `.` only begins a fraction when a digit follows, which is what
keeps `0..9` a range.

## 1.5 Character literals

`'…'` holds exactly one **code point** (`LYR-LEX0008` otherwise) — a Lyric `char` is a Unicode
scalar value, never a UTF-16 unit. Unterminated is `LYR-LEX0010`.

## 1.6 String literals

`"…"` is an immutable sequence of code points; it ends at the closing quote and must not span a
line (`LYR-LEX0009`). There is no raw or multiline string form.

## 1.7 Interpolated strings

`f"…"` interleaves text chunks with interpolations:

- `{expr}` embeds an expression; `{expr:spec}` formats it — the `:` starts the specifier only
  at the TOP level of the interpolation (braces, parentheses and brackets inside the expression
  are tracked), and the specifier runs to the matching `}`;
- `{{` and `}}` produce a literal brace; a lone `}` in the text stands for itself;
- the escape sequences of §1.8 apply in the text chunks;
- an f-string must not span a line.

## 1.8 Escape sequences

In string, character and f-string text, and nowhere else (`LYR-LEX0007` for anything unlisted):

| Escape | Meaning |
|---|---|
| `\n` `\t` `\r` | line feed, tab, carriage return |
| `\\` `\"` `\'` | the character itself |
| `\0` | U+0000 |
| `\xHH` | exactly two hex digits |
| `\u{H…}` | one to eight hex digits naming a Unicode scalar value |

## 1.9 Operators and punctuation

```
(   )   {   }   [   ]
,   .   ;   :   ::  ->  =>
?   ?.  ??  !
+   -   *   /   %
&   |   ^   ~
<<  >>
==  !=  <   <=  >   >=
&&  ||
++  --
..  ..=
=   +=  -=  *=  /=  %=
&=  |=  ^=  <<= >>=
&&= ||= ??=
```

Longest match wins: `<<=` before `<<` before `<`; `..=` is one token. `::` introduces an
interface list and never appears in a module path; `!` is postfix force-unwrap and prefix
logical not. How a `<` after a name resolves between comparison and type-argument list is
§6.3 of the grammar, restated in chapter 6.

# The standard library contract

> **Partly written.** §1 was written with milestone **M3** of the Lyric 5 plan; the rest comes with
> **M8a–M10**, spec-first: each rule lands here with its conformance case before or with its
> implementation. Source of the decisions:
> [10 Standard library](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md).

## Scope

What of the standard library is language: the prelude, the core interfaces and their contracts (hash, order, clone), the answer forms and the panic rule, the naming law.

## 1. The converters the compiler binds

The functions of `std.string` an f-string hole and `+` on strings compile to, by name
([10 S-series](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)): a
program need not import them for an f-string to work, and a program that imports them gets
the same functions.

| Function | Text |
|---|---|
| `concat(a: string, b: string): string` | the two joined; what `+` on strings is |
| `fromInt(value: int): string` | the decimal digits, `-` when negative ([03 §1.7](03-types.md)) |
| `fromUint(value: uint): string` | the decimal digits |
| `fromFloat(value: float): string` | the shortest text that reads back as the value; `inf`, `-inf`, `NaN` ([03 §1.7](03-types.md)) |
| `fromBool(value: bool): string` | `true` or `false` |
| `fromChar(value: char): string` | the character, UTF-8 |

A narrower integer or a `float32` in a hole widens to the converter's parameter type first
([03 §1.3](03-types.md)): `f"{x}"` with `x: int8` is `fromInt(x)`, with `x: float32` it is
`fromFloat(x)`.

## Numbers

The ten number types conform, in `std.core`, to a tower of interfaces (design 10 B5 Z1), whose
parent lists fix the operators' `Out` to `Self` ([05 §8](05-interfaces.md) rule 7), so
arithmetic stays in the type:

| Interface | Parents | Members | Conformers |
|---|---|---|---|
| `Num` | `Equatable`, `Ordered`, `Add`, `Sub`, `Mul`, `Div`, `Rem` (each `<Out = Self>`), `Display`, `Debug`, `Parse`, `Default` | `static let zero, one: Self`; `isZero(): bool` | all ten |
| `Signed` | `Num`, `Neg<Out = Self>` | `abs(): Self`, `signum(): Self` | `int8`…`int`, `float32`, `float` |
| `Integer` | `Num`, `TotalOrder`, `Hashable`, the bit operators (each `<Out = Self>`) | `static let min, max: Self`; `static let bitWidth: int`, `isSigned: bool` | `int8`…`int`, `uint8`…`uint` |
| `Float` | `Signed` | `static let epsilon, infinity, nan, min, max, leastPositive: Self`; `static fn fromBits(b: uint64): Self`; the methods below | `float32`, `float` |

The prelude passes `Num`, `Integer` and `Float` on (design 10 B2); `Signed` is `std.core`'s.

`isZero`, `abs` and `signum` are defaults, each type's own ([05 §1](05-interfaces.md) rule 4):
`signum` gives `-1`, `0` or `1` in the type, and a float's NaN stays NaN; `abs` gives `0.0` for
`-0.0`. `uint` has no `abs`.

`Integer` says where its arithmetic would leave the type, each a default:

- `checkedAdd`, `checkedSub`, `checkedMul`, `checkedDiv`, `checkedRem` (`o: Self`) give `?Self`:
  `null` where the result does not fit, or the divisor is zero; `min / -1` does not fit, and a
  remainder by `-1` is `0`.
- `saturatingAdd`, `saturatingSub`, `saturatingMul` hold at `min` or `max`, by the sign the
  result would have.
- `wrappingAdd`, `wrappingSub`, `wrappingMul` reduce modulo 2^`bitWidth`, as `+%`, `-%`, `*%` do a
  builtin's ([08](08-expressions.md)); `wrappingDiv` gives `min` for `min / -1` and
  `wrappingRem` `0` for a remainder by `-1` — a zero divisor panics as `/` does.
- `pow(n: uint): Self` multiplies by squaring; an overflow is one of `*`
  ([03](03-types.md)).
- `leadingZeros`, `trailingZeros` and `popCount` count bits at the type's width (`bitWidth` for
  zero); `rotateLeft(n)` and `rotateRight(n)` rotate modulo the width, a negative `n` the other
  way.

`Float` describes the type in its statics (design 10 B5 Z2): `epsilon` the distance from `1.0`
to the next value above it, `min` the most negative finite value, `max` the greatest,
`leastPositive` the least positive one — a subnormal —, `nan` the quiet NaN with its sign clear.
`fromBits(b)` is the value a bit pattern names, a `float32` the low 32 bits. Its methods are
defaults over `Self`, computed in `float` and rounded once to a `float32`:

- `isNan`, `isInfinite`, `isFinite`;
- `floor`, `ceil`, `round` — a half away from zero —, `trunc`;
- `sqrt`, `cbrt`, `exp`, `ln`, `log2`, `log10`; `sin`, `cos`, `tan`, `asin`, `acos`, `atan`,
  `sinh`, `cosh`, `tanh`, in radians; `x.atan2(y)`, the angle of the point (x, y), -π to π;
  `hypot(o)`, `pow(e)`;
- `totalCompare(o): Ordering`, IEEE 754's total order: -NaN, -infinity, the negatives, `-0.0`,
  `0.0`, the positives, infinity, NaN, every value in its one place — the order `sortBy` takes,
  where `float` has no `TotalOrder` of its own;
- `toBits(): uint64`, a `float32`'s 32 bits in the low ones.

### Parsing

A type read from a text conforms to **`Parse`**, `static fn parse(s: string): Self throws
ParseError` (design 10 B4, B5 Z6): every number type through `Num`, and `bool`. The text is
taken whole — no whitespace, nothing after the value — and what is wrong with it is thrown,
never panicked (10 B3): a **`ParseError`**, whose `kind` is a **`ParseErrorKind`** — `Empty` for
no text, `Invalid` for a text not of the type's form, `Overflow` for a number beyond the type's
range. All three are `std.core`'s.

- An **integer** is an optional `+` or `-` and ASCII digits, `_` only between two digits.
  `parse(s, radix)` stands beside `parse(s)` ([08 §1.2](08-expressions.md)) and reads digits in
  `radix`, 2 to 36 — `a`…`z` or `A`…`Z` for 10 to 35; a radix outside is the program's error
  and panics. An unsigned type takes no `-`, not even before `0`. A byte outside the form makes
  the text `Invalid` however many digits run before it; only a well-formed number is an
  `Overflow`.
- A **float** is an optional sign, then digits with an optional `.` and fraction — one digit at
  least — and an optional exponent, `e` or `E` with its own sign and digits, `_` only between
  two digits; or the sign and `inf` or `nan`. The value is the float nearest the text: beyond
  the range an infinity, below it a zero, as IEEE 754 rounds — a float has no `Overflow`.
- A **bool** is `true` or `false`.

# The standard library contract

> **Partly written.** §1 was written with milestone **M3** of the Lyric 5 plan; the rest comes with
> **M8a–M10**, spec-first: each rule lands here with its conformance case before or with its
> implementation. Source of the decisions:
> [10 Standard library](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md).

## Scope

What of the standard library is language: the prelude, the core interfaces and their contracts (hash, order, clone), the answer forms and the panic rule, the naming law, the syntax tree as values (`std.syntax`), serialization as a pair (`std.codec`), JSON (`std.json`), TOML (`std.toml`).

## 1. The converters

The functions of `std.string` that give a scalar's text — the text an f-string hole writes
([§2](#2-the-format-language) rule 4) — and the one `+` on strings compiles to, by name
([10 S-series](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)): a
program need not import `concat` for `+` to work, and a program that imports them gets the
same functions.

| Function | Text |
|---|---|
| `concat(a: string, b: string): string` | the two joined; what `+` on strings is |
| `fromInt(value: int): string` | the decimal digits, `-` when negative ([03 §1.7](03-types.md)) |
| `fromUint(value: uint): string` | the decimal digits |
| `fromFloat(value: float): string` | the shortest text that reads back as the value, `1.0` for an integral one; `inf`, `-inf`, `nan` ([03 §1.7](03-types.md)) |
| `fromFloat32(value: float32): string` | the shortest text that reads back as the same `float32` — `0.1`, not the `float`'s `0.10000000149011612` (the review's M8a-9) |
| `fromBool(value: bool): string` | `true` or `false` |
| `fromChar(value: char): string` | the character, UTF-8 |

A narrower integer in a hole writes its value's text, widened ([03 §1.3](03-types.md)):
`f"{x}"` with `x: int8` writes what `fromInt(x)` gives. A `float32` has a converter of its own:
with `x: float32` the hole writes what `fromFloat32(x)` gives.

## 2. The format language

A hole may name a format after a colon — `{x:>8}`, `{n:#x}`, `{f:.2f}`, `{v:?}` — in one
language, without locale, checked where it is written
([08 Y7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md),
[10 S7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)).

1. **Form**: `[[fill]align][sign][#][0][width][grouping][.precision][type]`. `align` is `<`
   (left), `>` (right) or `^` (centred, the odd fill after), the fill any character before it, a
   space without; `sign` is `+` (a sign on every number) or `-` (on a negative one only, as
   without); `#` writes a radix's prefix, `0b`, `0o`, `0x`, `0X`; `0` pads with zeros between the
   sign and prefix and the digits — with a grouping, the zeros are grouped with the digits and
   the width counts the separators, a minimum that no separator leads (the review's A4):
   `{1234:010,}` is `00,001,234`, `{1234:08_}` is `0_001_234`; `width` is the least number of
   **characters**, not bytes;
   `grouping` is `,` or `_` between each three decimal digits, `_` between each four of another
   radix; `precision` is the digits after a float's point or the most characters of a string;
   `type` is `b`, `o`, `x`, `X` (an integer's radix), `e`, `E`, `f`, `%` (a float's form) or `?`
   (`Debug`).
2. **What applies**: an integer takes all but a precision and a float's type; a float all but `#`
   and an integer's type; a `string` fill, alignment, width and precision; a `char`, a `bool`
   and a `Display` type fill, alignment and width, on its text — for a `Display` type, what
   `showTo` writes; `?` takes fill, alignment and width, on what `debugTo` writes, for every
   type. A spec that is no format,
   or a part that does not apply to the hole's type, is refused (`LYR-SEM0164`). A type with
   formats of its own conforms to `Format { fn format(spec: StringView, out: StringBuilder): void; }`
   and reads the spec as written, unchecked — `?` stays `Debug`.
3. **Defaults**: a number right-aligned, the rest left-aligned. A float without a type or a
   precision is its shortest text ([03 §1.7](03-types.md)); with a precision and no type it is
   fixed, `{2.5:.3}` is `2.500`; `e`, `E`, `f` and `%` take six digits without a precision; `%`
   writes the value a hundredfold, fixed, with `%` after; an exponent carries its sign and two
   digits at least, `{1234.5:e}` is `1.234500e+03`. The fixed, the exponent and the percent
   forms round **half away from zero** on the value's exact binary digits — the language's one
   rounding rule, `round()`'s (the review's M8a-8), the same on every host: `{0.125:.2f}` is
   `0.13`, `{2.5:.0f}` is `3`, and `{2.675:.2f}` is `2.67`, the double nearest 2.675 lying below
   the half. `nan`, `inf` and `-inf` keep their words, `NAN` and `INF` under `E`.
4. **Binding**: an f-string writes its text into one `StringBuilder`, piece by
   piece in order (design 10 S6) — no string per hole and no chain of joins: a scalar's hole
   its text (§1), another `Display` type's through `showTo`; `{x:spec}` through
   `format(spec, out)` for a `Format` type — the scalars conform —, through the padding of what
   `showTo` writes for another `Display` type, and through `debugTo` under `?`. The calls are
   `std.core`'s, bound by the compiler: a program need not import anything for an f-string.
5. **At run time**: `std.fmt.format(template: string, args: Display...): string` reads its
   template when it runs, in this language (design 08 Y7, 10 S7): `{}` takes the next value and
   `{i}` the i-th from 0 — the two mix, `{}` counting only itself —, either with `:spec` as rules
   1–3 say, `?` for the value's `Debug` text; `{{` and `}}` write a brace, and a value no hole
   names is left out. A value is passed as a `Display` ([05 §2](05-interfaces.md)), a scalar's
   too. What the compiler refuses in an f-string **panics** here (`LYR-RT0008`, design 10 B3): a
   brace left open or closed without being opened, a value named that is not given, a spec that
   is no format or holds a part the value's type does not take, `?` on a value without `Debug`.

## Numbers

The ten number types conform, in `std.core`, to a tower of interfaces (design 10 B5 Z1), whose
parent lists fix the operators' `Out` to `Self` ([05 §8](05-interfaces.md) rule 7), so
arithmetic stays in the type:

| Interface | Parents | Members | Conformers |
|---|---|---|---|
| `Num` | `Equatable`, `Ordered`, `Add`, `Sub`, `Mul`, `Div`, `Rem` (each `<Out = Self>`), `Display`, `Debug`, `Parse`, `Default` | `static let zero, one: Self`; `isZero(): bool` | all ten |
| `Signed` | `Num`, `Neg<Out = Self>` | none of its own: what `std.math`'s `abs` and `signum` take | `int8`…`int`, `float32`, `float` |
| `Integer` | `Num`, `TotalOrder`, `Hashable`, the bit operators (each `<Out = Self>`) | `static let min, max: Self`; `static let bitWidth: int`, `isSigned: bool` | `int8`…`int`, `uint8`…`uint` |
| `Float` | `Signed` | `static let epsilon, infinity, nan, min, max, leastPositive: Self`; `static fn fromBits(b: uint64): Self`; the members below | `float32`, `float` |

The prelude passes `Num`, `Integer` and `Float` on (design 10 B2); `Signed` is `std.core`'s.

`isZero` is a default, each type's own ([05 §1](05-interfaces.md) rule 4). What one computes
with a number — its absolute value, its sign, a root, an angle — is no member of the type but
`std.math`'s (design 10 B5 Z2, "Review 2026-10-12"; below): what a number *is* stands at its
type, what one *does* with numbers in `std.math`.

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
`fromBits(b)` is the value a bit pattern names, a `float32` the low 32 bits. Its members are
defaults over `Self`, what describes the value:

- `isNan`, `isInfinite`, `isFinite`;
- `totalCompare(o): Ordering`, IEEE 754's total order: -NaN, -infinity, the negatives, `-0.0`,
  `0.0`, the positives, infinity, NaN, every value in its one place — the order `sortBy` takes,
  where `float` has no `TotalOrder` of its own;
- `toBits(): uint64`, a `float32`'s 32 bits in the low ones.

### `std.math`, `clamp`, a `char`'s code point

What one computes with numbers is `std.math`'s (design 10 B5 Z2, "Review 2026-10-12"): free
functions, generic over the tower, so that a reader finds `sqrt(x)` where every language puts
it and the type keeps what describes it. The elementary functions over `Float` are computed in
`float` and rounded once to a `float32`. `sqrt`, `floor`, `ceil`, `round` and `trunc` are exact;
the rest — `cbrt`, `exp`, the logarithms, `pow`, the trigonometric and hyperbolic functions,
`hypot` — are one implementation's (musl's), which the runtime carries on every platform: a
program computes the same bits wherever it runs, and a `comptime` site computes the bits the
program would ([11 §2](11-metaprogramming.md)):

- `floor(x)`, `ceil(x)`, `round(x)` — a half away from zero —, `trunc(x)`;
- `sqrt(x)`, `cbrt(x)`, `exp(x)`, `ln(x)`, `log2(x)`, `log10(x)`; `sin`, `cos`, `tan`, `asin`,
  `acos`, `atan`, `sinh`, `cosh`, `tanh`, in radians; `atan2(y, x)`, the angle of the point
  (x, y), -π to π; `hypot(x, y)`; `pow(x, e)` — an integer's power by squaring is its own
  `x.pow(n)`, arithmetic in the type.

Over `Signed`: `abs(x)`, `0.0` for `-0.0`, which `<` does not tell from `0.0`; `signum(x)`,
`-1`, `0` or `1` in the type, a float's NaN staying NaN. `uint` is no `Signed`, and has neither.

What describes the world rather than a type: `pi`, `e` and `tau`, typed `float` —
`math.pi as float32` for the narrow width. Beside them stand the functions of two numbers:

- `min(a, b)` and `max(a, b)` over `Ordered`, `a` where the two are equal or unordered (a NaN);
- `gcd(a, b)` and `lcm(a, b)` over `Integer`, never negative, `gcd(0, 0)` is `0`; a result beyond
  the type overflows and panics — `gcd(int.min, 0)`;
- `lerp(a, b, t)` over `Float`, `a` at `t = 0` and `b` at `t = 1` exactly.

A narrowing that answers is a static of the target (Z4): `int8.exact(v)` is the `int8` an
integer `v` of any type names, or `null` where it does not fit; `int8.clamping(v)` holds at
`min` or `max` instead. They are members of `Integer` (the review's M8a-7): each integer type
answers them, and a type parameter bounded by `Integer` reaches them — `U.exact(v)`,
`U.clamping(v)`.

`x.clamp(lo, hi)` is a default of `Ordered`: `lo` below it, `hi` above it, the value itself
between; `lo` above `hi` is the program's error and panics, and a value unordered with the bounds
comes back as it is. A `char`'s code point is `c as uint32` (the review's A9e: the method that
said the same is gone), and `char.fromUint32(n): ?char` is
`null` for a surrogate or beyond `0x10FFFF` (Z8), where `n as char` panics
([03 §1.4](03-types.md)).

## Iteration

The protocol `for` walks (design 10 B6) is `std.core`'s; the prelude passes `Iterator`,
`Iterable` and `FromIterator` on.

- **`Iterator { type Item; type Error :: [Error] = never; mut fn next(): ?Self.Item throws
  Self.Error; fn sizeHint(): (int, ?int) }`**: `next()` gives the next value, and `null` at the
  end. A walk that can fail answers its `Error`, which `next()` throws; by default it throws
  nothing ([07 §2](07-statements.md) rule 6). `sizeHint()` says how many values are left, at
  least and at most where that is known; the default says `(0, null)`. A type that is an
  `Iterator` **and** `Closeable` throws in `close()` only what its `Error` allows
  (`LYR-SEM0174`; the review's M8a-4): a loop that closes the iterator is covered by the
  clause that covers its pulls ([07 §2](07-statements.md) rule 7).
- **`Iterable { type Iter :: [Iterator]; fn iter(): Self.Iter; }`**: what `for` walks. Every
  iterator is iterable as itself, `extend<I :: [Iterator]> I :: [Iterable<Iter = I>]`.
- **`DoubleEnded :: [Iterator] { mut fn nextBack(): ?Self.Item; }`**: the last value not yet
  given.
- A **`Range<T>`** of an integer type or of `char` is an `Iterator` of `T` and `DoubleEnded`:
  `next()` gives `start` and moves it on, `nextBack()` moves `end` back and gives it. A
  **`RangeInclusive<T>`** is both too and gives `end` as well; its last value leaves `start` past
  `end`, or `end` before `start` where that value is the type's last (its first, from the back) —
  no bound leaves the type. A range of characters has its values the scalar values in between,
  the surrogates passed over, its first `'\0'` and its last `'\u{10FFFF}'`. A range walked
  changes: `start` and `end` are `var`.
- A **`Coroutine<T>`** is an `Iterator` of `T` and `Closeable`, built in (design 10 B6 I7): its
  `Error` is what it throws, `never` where nothing, and it conforms to nothing else. A loop over
  one pulls it and closes it on its way out ([07 §2](07-statements.md) rule 7): left early, its
  stack unwinds and its defers run.
- The **adapters** are members of every iterator (design 10 B6 I3, I4), each giving a struct of
  its own — monomorphized, nothing allocated. They are `std.iter`'s (M9a S11c): the prelude
  names that module, so its blocks reach every iterator in every module without an import
  ([04](04-modules.md) rule 5), and a program imports a struct where it writes the type,
  `import std.iter { MapIter }`. The protocol, the ranges and the iterators of `std.core`'s own
  types stay `std.core`'s. Each: `it.map(f)` gives a `MapIter<I, U, E>` (`Map` is
  the collection's), `it.filter(p)` a `FilterIter<I, E>`; `E` defaults to `never`, so
  `MapIter<I, U>` names the one whose function throws nothing. Every iterator type's name ends in `Iter`
  (the review's A9g): the adapters (`TakeIter`, `ZipIter`, …), the string's (`CharsIter`,
  `SplitIter<P>`, `MatchesIter<P>`, `LinesIter`), the map's (`MapEntriesIter`, `MapKeysIter`,
  `MapValuesIter`), the
  slice's and the list's (`SliceIter`, `ListIter`). They pull lazily, one value at a time, and their
  `Error` is the inner iterator's, joined with what a function they take throws (below). Of one
  source besides: `take(n)` and `skip(n)`;
  `takeWhile(p)`, which stays ended once `p` failed, and `skipWhile(p)`; `stepBy(n)`, the first
  value and then every `n`th, `n` below 1 a panic; `enumerate()`, each value with its position
  from 0, `(int, Item)`; `inspect(f)`, each value shown to `f` on its way through;
  `mapNotNull(f)`, the values through `f`, the `null`s left out; `flatMap(f)`, the values of the
  `Iterable`s `f` gives, one after the other, and `flatten()` of an iterator of `Iterable`s;
  `dedup()` of an `Equatable` item and `dedupBy(same)`, a run of values `same` holds for given
  once; `scan(init, f)`, `init` and then each running value `f` makes of the one before and a
  value; `peekable()`, a `PeekableIter` whose `peek()` gives the next value without taking it;
  `rev()` of a `DoubleEnded` iterator, its values from the back — no `DoubleEnded` itself, and
  throwing nothing, as a pull from the back throws nothing; `cycle()` of an iterator that is
  `Clone`, its values over and over from a clone each time, none where it has none — an array's
  walk, a range and a string's characters are `Clone`. Of two
  sources: `zip(other)`, each value beside the other's as long as both have one, the other an
  `Iterable`; `chain(other)`, the values and then the other's, an iterator of the same items.
  An adapter over a `Closeable` iterator — `rev()` and `cycle()` excepted — is `Closeable`
  itself and passes `close()` on (the
  review's M8a-4), so a loop that leaves `gen().map(f)` early closes the generator; `zip` and
  `chain` close both of theirs, the first error winning.
  Their `Error` is the **join** of their sources' (design 05 E2 K7), `Join<A, B>` of `std.core`:
  one type where both are one, the other where one is `never`, the root `Error` where they
  differ — reduced once both are known; open, it covers each of its parts.
- A **function an adapter or a terminator takes may throw** (design 05 K4; 13 M8c P2): `map`,
  `filter`, `takeWhile`, `skipWhile` and `inspect` take a `fn(…) -> … throws E` and give an
  iterator whose `Error` is `Join<I.Error, E>`; `fold`, `reduce`, `any`, `all`, `none`, `find`,
  `position` and `forEach` throw `Join<I.Error, E>`. `E` is what the function throws, bound at the
  call, and `never` where it throws nothing — then nothing is joined and no `try` stands:
  `words.iter().map((s) => try int.parse(s))` is walked with `try`, `xs.iter().map((x) => x * 2)`
  without.
- The **terminators** walk an iterator — a copy of a struct one, a class one where it stands — and
  throw what it throws: `count()`; `fold(init, f)` and `reduce(f)`, the latter `null` without a
  value; `first()`, `last()` and `nth(n)`, `null` where there is no such value, a negative `n`
  included; `any(p)`, `all(p)` (`true` for none) and `none(p)`, stopping at the value that
  decides; `find(p)` and `position(p)`; `forEach(f)`, inline
  ([03 §8.5](03-types.md#85-inline-functions)): a lambda written at the call is set in place, its
  `return` the caller's; `toArray()`, in one pass; `minBy(key)`
  and `maxBy(key)`, the value whose `TotalOrder` key is least or greatest, the first of equal
  ones, `null` without a value. Of `std.collections`: `chunks(n)`, the values in `List`s of `n`,
  the last shorter where they do not divide, and `windows(n)`, every run of `n` values in turn,
  each a `List` of its own, none where there are fewer — `n` below 1 panics (`LYR-RT0008`);
  `sorted()` of a `TotalOrder` item and `sortedBy(cmp)`, the values in a `List`, stably sorted;
  `partition(p)`, the values `p` holds for and the others, two `List`s in order; `groupBy(key)`,
  a `Map` of the values in `List`s under their key, each list in order; `toMap()` of pairs, a
  `Map`, a later value of a key replacing the earlier one. `collect()` into an array or a list
  starts with the room the iterator's `sizeHint()` gives; where that is exact, an array is made
  without a copy.
- **`FromIterator<T> { static fn fromIter<I :: [Iterator<Item = T>]>(it: I): Self throws
  I.Error; }`** is what **`collect<C :: [FromIterator<Item>]>()`** builds (design 10 B6, I4;
  M8a S15): the values in a `C`, the type the call's position expects —
  `let names: Set<string> = words.iter().collect();` —, throwing what the iterator throws. `T[]`
  is a `FromIterator<T>`, and so are `List<T>`, `Deque<T>`, `Set<T>`, `Heap<T>` and
  `Map<K, V>` of `(K, V)` (§Collections) — a set's and a map's keys once, a later value of a key
  replacing the earlier one. `toSet()`, of a `Hashable` element, is `collect()` into a `Set`, as
  `toList()` is into a `List` and `toArray()` into an array.
- The terminators **of an element kind** stand on the iterators whose `Item` admits them
  ([05 §13](05-interfaces.md) rule 2): `sum()` and `product()` of a `Num`, zero and one where there
  is no value; `min()` and `max()` of an `Ordered`, `null` without a value, the first of equal
  ones; `join(sep)` of a `Display`, the texts with `sep` between each two; `average()` of `int`
  or of `float` values, a `float`, `null` without a value.
- **`SliceIter<T>`** is the iterator of an array or a view, from both ends, through a view of its
  elements — nothing is copied, and a write to a later element is seen; its `sizeHint()` is
  exact. `T[]` and `Slice<T>` are `Iterable` through it: `xs.iter()`.

### Parsing

A type read from a text conforms to **`Parse`**, `static fn parse(s: StringView): Self throws
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

## Results and conversions

A failure kept as a value, and a value made from another (design 05 E1, 10 B3, B4) — both
`std.core`'s, and named in the prelude ([04](04-modules.md)).

- **`Result<T, E :: [Error]>`** is an enum, `Ok(T)` or `Err(E)`, matched as every enum is
  ([09](09-patterns.md)). `throws` stays the mechanism: two bridges lead to it and back, and no
  operator is a result's own (05 E1). **`Result.of(f)`** calls `f`, a `fn() -> T throws E`, and
  is `Ok` with what it returns or `Err` with what it throws — `Result.of { try half(n) }`, `E`
  inferred from what the lambda throws (05 K4), the root `Error` where that is two types.
  **`r.get()`** is an `Ok`'s value and throws an `Err`'s error: `try r.get()`. `E` is an `Error`,
  since `get()` throws it. The library returns no `Result` (10 B3); the caller makes one. It is
  `@MustUse` ([11 §1](11-metaprogramming.md) rule 11): a statement that drops one warns.
- **`From<T> { static fn from(v: T): Self; }`** is a conversion into a type, which the type
  writes: `Centimeters.from(m)`. **`Into<T> { fn into(): T; }`** follows from it through
  std.core's blanket `extend<T, U :: [From<T>]> T :: [Into<U>]` ([05 §13](05-interfaces.md)
  rule 9): `let c: Centimeters = m.into();` — the type the position expects chooses the target;
  where none is expected the call is refused (`LYR-SEM0060`), and a target that is no `From` of
  the value's type too (`LYR-SEM0028`). A constraint `T :: [Into<X>]` holds for every type `X`
  is a `From` of. `as` converts numbers only ([03 §1.4](03-types.md)).

## Arrays and views

The members of an array and of a view are `std.core`'s (design 10 C2), written once on
`Slice<T>` and reached on an array through a view of all of it ([03 §5.2](03-types.md) rule 4)
— and so on an inline array that lies in the heap ([03 §5.3](03-types.md) rule 6): a write
through one reaches the array. `length()` and the index are the primitives
([03 §5.1](03-types.md)).

- `isEmpty()`; `get(i)`, `null` outside `0 ≤ i < length()`; `first()` and `last()`, `null`
  where there is no element.
- `swap(i, j)`, an index outside panicking as `[i]` does; `reverse()` in place; `reversed()`, a
  new array.
- `copyInto(into)`: the elements into the view `into`, which is at least as long — a shorter
  one panics as an index outside does (`LYR-RT0003`), a longer one keeps its rest; the two may
  overlap either way (the review's B16). One copy, not an element at a time: what the
  collections grow and shift with.
- Of an `Equatable` element: `contains(x)`, through which `T[]` and `Slice<T>` are
  `Contains<T>` (10 C12) — what `x in xs` asks ([05 §12](05-interfaces.md) rule 10) — and
  `indexOf(x)`, the first index or `null`.
- Of a `Clone` element: `fill(v)`, every element a clone of `v` — no object shared into several
  slots, as `[x] * n` shares none ([03 §5.1](03-types.md)).
- `partitionPoint(p)`: the first index whose element fails `p`, for elements `p` partitions —
  every one it holds for before every one it does not; a binary search. Of a `TotalOrder`
  element, `binarySearch(x)`: the index of an element equal to `x` in sorted elements, any of
  several equal ones, or `null`.
- Of a `Display` element: `join(sep)`, the elements' texts with `sep` between each two.
- **Clone** (10 K5; N2a): of a `Clone` element, `T[]` is `Clone` — `clone()` is a new array of the
  elements' clones, and `[xs] * n` repeats such an array by `clone` ([03 §5.1](03-types.md)).
- **Equality and display** (10 C9; M8a S14): of an `Equatable` element, `T[]` and `Slice<T>` are
  `Equatable`, element by element in order — `[1, 2] == [1, 2]`, `xs[1..] == ys[1..]`. Of a
  `Debug` element they are `Debug` and `Display` alike: `[1, 2, 3]`, each element in its debug
  text — a string quoted, `["a", "b"]`, where unquoted its bounds would be lost — so `{xs}` and
  `{xs:?}` print the same, and a width pads it as a `Display` value's text. An array literal
  beside `==` or `!=` takes the other side's type, `xs == []`; `[] == []` fixes none
  (`LYR-SEM0060`).
- The **sorts** (10 C10): `sortBy(cmp)` puts the elements in the order `cmp` gives, and
  `sortByKey(key)` in the order of a `TotalOrder` key; of a `TotalOrder` element, `sort()` in
  ascending order. All three are **stable** — equal elements keep their order — and take a buffer
  of the length. `sortUnstable()`, of a `TotalOrder` element, sorts in place without one; equal
  elements end in any order. Each is `O(n log n)` in comparisons. A `float` has no total order
  of its own: its elements sort through `sortBy`. The comparison of `sortBy`, the key of
  `sortByKey` and the test of `partitionPoint(p)` may throw, and the call throws it: a sort that
  one ends leaves every element in the slice, in some order.
- `arrayOf(n, f)` ([03 §8](03-types.md)) calls `f` once per index, in order; a negative `n`
  panics; what `f` throws, the call throws, and no array is made.

## Hashing

A hash is computed with a **`Hasher`** of `std.core` (design 10 Q3, K2): `writeByte(b)` writes a
byte; `write(bytes)` the bytes of a `Slice<uint8>`, `writeUint(v)` and `writeInt(v)` the eight
bytes of a word, the lowest first — defaults over `writeByte` a hasher may replace; `finish()`
answers the hash of what was written, a `uint64`, and leaves the hasher writable. `std.hash`
holds three:

- **`DefaultHasher`**, SipHash-1-3 under a key the system draws once per process, at the first
  use — the same in every thread, another in the next run. What it hashes cannot be aimed at
  collisions from outside, and an order that follows its hashes differs from run to run.
- **`FixedHasher`**, SipHash-1-3 under a zero key: the same hash in every run.
- **`Fnv1a64`**, FNV-1a in 64 bits: keyless, for input no adversary chooses.

Where the system gives no random bytes, the program panics with `LYR-RT0015`
([13](13-abi.md)).

`std.hash` also holds three **checksums** of a `Slice<uint8>`, each a `uint32` (design 10 Q3; M8c
S11). Each continues from a running value, as zlib's do: the checksum of the whole is that of its
pieces, one after the other — `crc32(rest, crc32(first))`.

- **`crc32(bytes, running = 0)`**, CRC-32 of ISO-HDLC (zip, gzip, PNG):
  `crc32("123456789".toBytes())` is `0xCBF43926`.
- **`crc32c(bytes, running = 0)`**, the Castagnoli polynomial (iSCSI, RFC 3720): `0xE3069283` over
  the same nine bytes.
- **`adler32(bytes, running = 1)`**, RFC 1950's (zlib): `adler32("Wikipedia".toBytes())` is
  `0x11E60398`.

## Input and output

The core of `std.io`, its buffers and its text ([design 10 O1–O3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md);
M8b S2, S3 and S10a). The files, the console's streams and the network follow with M8b's later
slices.

1. **`IoError`** is the one error that input and output throw (O3), a struct: `kind:
   IoErrorKind`, `path: ?string`, `detail: string` and `inner: ?Error` — the field O3 calls
   `cause`, named so because `Error` asks for a method `cause()` and a type's members do not share
   a name (as `Exception`'s `inner`). Its `message()` is the kind in words, then the path and the
   detail where there are any: `not found: data.txt (opened to read)`. `IoErrorKind` names O3's
   kinds, and `Other { code }` a system's code no kind names. It is `@NonExhaustive`
   ([11 §1](11-metaprogramming.md) rule 12): a later release may name another kind, so a `match`
   over it outside `std` writes a `_`.
2. **`Reader`** has `read(into: Slice<uint8>): int`: it fills the slice from the front and answers
   how many bytes it put there — **0 only at the end**, and at once for an empty slice; fewer than
   the slice holds is no end. **`Writer`** has `write(from: Slice<uint8>): int`: it takes from the
   front and may take **fewer** bytes than it is handed. **`Seek`** has `seek(to: SeekFrom): int`,
   `SeekFrom.Start(n)`, `.End(n)` or `.Current(n)`, and answers the position counted from the
   start. All three are `mut fn`s. `read`, `write` and a writer's **`flush()`** — which hands on
   what it holds back; the default does nothing (design 10 B8) — throw **`[IoError, Cancelled]`**,
   `seek` throws `IoError`. **Why `Cancelled`** (design 10 Review 2026-10-08): a read from a socket
   or a pipe, or a write into one, waits for as long as the other side does nothing, and a cancel
   ([10 §1](10-concurrency.md) rule 7) must be able to end that wait with the error every wait
   ends with — not with an `IoError`, which a handler would take for the stream's failure. A
   reader or writer that never waits without bound declares `IoError` alone, as an implementation
   may throw less than its member ([06 §2](06-errors.md) rule 4); code over any reader or writer
   is told both.
3. **The defaults** (O1), on every reader: `readExact(into)` fills the slice whole or throws
   `UnexpectedEof`; `readToEnd()` is everything to the end in a new array; `readToString()` the
   same as UTF-8 — bytes that are no UTF-8 throw `InvalidData`, the decoder's `Utf8Error` as the
   cause. On every writer: `writeAll(from)` writes until all of it is taken — a writer that takes
   no byte of a slice that has some throws `Other { code: 0 }` rather than being asked forever —
   and `writeString(s)` writes the text's UTF-8. They throw what any reader's or writer's call
   may, `[IoError, Cancelled]` — over one that declares `IoError` alone too.
4. **`copy(r, w): int`** copies everything `r` holds into `w` and answers how many bytes, and
   throws `[IoError, Cancelled]`. The two
   are used as the values handed in: a class is itself, and a reader that is a struct is read
   through a copy, its position unmoved for the caller.
5. **The streams over memory** (O2): `ByteReader.new(bytes)` reads a `Slice<uint8>` from the
   front and seeks — a position past the end reads nothing, one before the start panics;
   `ByteBuffer.new()` appends what is written and reads from the front what was written and not
   yet read, with `length()` and `toArray()` of what it holds. Both are classes, say
   `throws IoError` and throw nothing; never waiting, they leave `Cancelled` out.
6. **The buffers** (O2), with 8 KiB of their own. `BufReader.new(r)` is a reader that reads `r` a
   buffer at a time; a read at least as large as the buffer, while it is empty, goes to `r`
   directly. `BufWriter.new(w)` is a writer that holds back what it is handed until the buffer is
   full, a `flush()` or a `close()`; a write at least as large goes to `w` directly, after what is
   held. A flush that throws keeps what `w` did not take, for the next. Both throw what any
   reader's or writer's call may (rule 2). A `BufWriter` is
   `Closeable`: `close()` flushes and leaves `w` open, and one that nothing closes is warned
   about (06 §7.4, `LYR-SEM0144`). *(Informative.)* O2 has both as structs with the bytes inline;
   every read hands the inner reader a view of the buffer, and an inline array in a frame has no
   view (03 §5.3), so they are classes over a buffer on the heap.
7. **`TextReader.new(r, skipBom: false)`** reads UTF-8 text through a buffer of its own.
   `readLine(): ?string` is the next line without its end — a `\n` or a `\r\n`; a `\r` alone is
   text — or `null` at the end. A last line without an end is a line; the end of the last line
   starts none. `lines()` iterates the same; `chars()` iterates the codepoints; `readToEnd():
   string` is the rest. All throw `[IoError, Cancelled]`, and the two iterators' `Error` is
   `Join<IoError, Cancelled>`, the root `Error` once reduced (§Iteration): a loop over them is
   told `Error`. A codepoint split between two reads of `r`
   waits for its rest. Bytes that are no UTF-8 throw `InvalidData`, a `Utf8Error` as the cause
   whose offset counts from the reader's start; a line that throws is consumed. A byte order mark
   is text, `U+FEFF`, unless `skipBom: true` drops it from the front.
8. **`TextWriter.new(w)`**: `write(s)` writes the text's UTF-8, `writeLine(s)` that and a `\n`, on
   every system. It holds nothing back, and throws what `w` may.

## Encodings

`std.encoding` ([design 10 Q5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S4a): bytes as text and
back, and the integers of a byte slice. Each encoding is a struct of static members, a name
space: `Base64.encode(bytes)`.

1. **`EncodingError`** is what a decoder throws: `offset`, where the text first is not the
   encoding — a byte of it, a unit of UTF-16 —, and `detail`, what is wrong there. Its
   `message()` is `no Base64 digit at offset 1`.
2. **`Base64`** and **`Base64Url`** encode a `Slice<uint8>` with RFC 4648's alphabets (§4 with
   `+` and `/`, §5 with `-` and `_`), padded with `=` to a multiple of four characters. `decode`
   is strict: a text whose length is no multiple of four fails at its end; a character outside the
   alphabet — whitespace and the other alphabet's two among them — or a `=` before the end fails
   where it stands; bits past the last byte that are not zero fail at their character (RFC 4648
   §3.5). **`Base64Url.encodeUnpadded`** and **`decodeUnpadded`** (M10 S5; design 10 S4a) are the
   same alphabet without the `=` padding, as JOSE writes it (RFC 7515 §2): the text's length is
   4k, 4k + 2 or 4k + 3 — a length of 4k + 1 fails at its end —, a `=` is no digit here, and the
   bits past the last byte are checked as above.
3. **`Hex`** encodes two digits a byte, in small letters, and decodes either case; an odd count
   of digits fails at the end.
4. **`Utf16`** encodes a text as code units, `uint16[]`, a codepoint past `U+FFFF` as a surrogate
   pair; `decode` takes units, and half of a pair without its other half fails at its unit.
5. **The integers of bytes**: `T.fromBytesLE(s)` and `T.fromBytesBE(s)` for every integer type
   `T` read exactly its width — another length panics (`LYR-RT0008`) —, the first byte the lowest
   or the highest. `Slice<uint8>` has `getUint16LE(at)`, `getUint16BE`, the same for `Uint32`,
   `Uint64`, `Int16`, `Int32` and `Int64`: the width at the byte offset `at`. The way back:
   `v.toBytesLE()` and `v.toBytesBE()` of every integer type give its width as an inline array,
   `uint8[N]` — `(258 as uint16).toBytesBE()` is `[1, 2]` (M8c S11). An inline array in a frame
   gives no view ([03 §5.3](03-types.md)): `T.fromBytesLE(v.toBytesLE().toArray())` is `v`. They
   are members of the module's blocks, there where `std.encoding` is imported. *(Informative.)* A string's bytes
   are `toBytes()` (§Strings).

## Cryptography

`std.crypto` ([design 10 Q4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S4b): the hashes for security, HMAC,
the system's random bytes, and a comparison of secrets. The doors are Ed25519, X25519,
ChaCha20-Poly1305 and Argon2.

1. **`Digest`** is a hash fed in pieces: `static let size` and `static let blockSize` in bytes,
   `static fn new()`, `update(bytes)` as often as there are pieces, and `finish(): uint8[]`, the
   hash of all of them. `finish` leaves the digest as it was: fed further, it hashes the longer
   input. *(Informative.)* Q4 writes `finish(): uint8[N]`; an interface names no length that is
   each implementer's own, as 5.0 has no generic constant ([03 §5](03-types.md)).
2. **`Sha256`** and **`Sha512`** are FIPS 180-4's SHA-256 and SHA-512, **`Sha1`** its SHA-1 and
   **`Md5`** RFC 1321's MD5. SHA-1 and MD5 are broken for collisions and are there for what an old
   format asks. `sha256(bytes): uint8[32]` is the hash at once.
3. **`Hmac<D>.new(key)`** is RFC 2104's HMAC over any `Digest`, with `update` and `finish` as a
   digest's: a key longer than `D.blockSize` is hashed first, a shorter one padded with zeros.
4. **`randomBytes(n): uint8[]`** and **`randomUint64(): uint64`** come from the system; a system
   that gives none panics (`LYR-RT0015`).
5. **`constantTimeEq(a, b): bool`** compares two byte slices in a time that depends on their
   lengths alone — not on where they first differ. Slices of different lengths are unequal.

## Random numbers

`std.random` ([design 10 Q2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S4c): a generator, its draws, and the free
forms over the running thread's own. Not for secrets — `randomBytes` of §Cryptography is.

1. **`Random`** is ChaCha8 (RFC 8439's block function, eight rounds), 64 bits a draw.
   `Random.seeded(seed: uint64)` gives the stream the seed names, **the same in every 5.x**:
   the key is four outputs of SplitMix64 from the seed — eight words, the low half of each output
   first —, the nonce is zero, the block counter counts from zero in words 12 and 13, and each
   block's sixteen words are taken in order, two of them a draw, the first the low half.
   `Random.fresh()` keys a generator from the system's random bytes.
2. **The draws.** `nextUint64()`; `nextInt()`, the draw as an `int`; `nextInRange(r)`, an integer
   of the `Range<int>` `r`, each alike — a draw below 2⁶⁴ modulo the range's length is drawn
   again —, an empty range panics (`LYR-RT0008`); `nextFloat()`, the high 53 bits of a draw over
   2⁵³, in [0, 1); `nextBool()`, the high bit of a draw; `nextBytes(into)`, eight bytes a draw, the
   low byte first, a shorter tail from one draw's low bytes; `nextNormal(mean = 0.0, stdDev =
   1.0)`, Marsaglia's polar method, two floats a try and one of the pair kept. Each takes its
   draws from the stream as said, so a seeded generator gives the same values in every 5.x —
   `nextNormal` up to the last bits of the platform's `ln` and `sqrt`.
3. **`shuffle(s)`** puts a `Slice<T>` in an order each of its orders alike (Fisher–Yates, from
   the back, the place `i` swapped with one of `0..i + 1`). **`choice(s): ?T`** is an element,
   each alike, or `null` for an empty slice, which draws nothing. **`sample(s, k): T[]`** is `k`
   elements from `k` different places, in a random order; `k` outside `0..=s.length()` panics.
4. **The free forms** `random.nextInRange(r)`, `random.nextFloat()` and `random.shuffle(s)` draw
   from the running thread's generator — its own, keyed from the system at its first use there.
   *(Informative.)* Q2 names them `random.int` and `random.float`; no declaration takes a builtin
   type's name ([07](07-statements.md) K5), so they carry `Random`'s names.

## Time

`std.time` ([design 10 Q1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S5a, S5b): spans, the system's two clocks,
the calendar and RFC 3339. The time zones' database and the format patterns follow with M10.

1. **`Duration`** is a span in whole nanoseconds, negative or not: `ofNanos`, `ofMicros`,
   `ofMillis`, `ofSecs`, `ofMinutes`, `ofHours`; `nanos()`, `millis()` and `secs()` rounded toward
   zero, `asSecsFloat()`. `+` and `-` with a `Duration`, `*` and `/` with an `int`; arithmetic that
   leaves the range of `int` panics (`LYR-RT0002`), a division by zero too (`LYR-RT0001`). It is
   `Equatable`, `Ordered`, `TotalOrder`, `Hashable`, its default is zero.
2. **A duration's text** is Go's: `0s`; under a second one unit — `ns`, `µs`, `ms` — with its
   fraction, the fraction's trailing zeros dropped (`1.5µs`, `500ms`); from a second on hours,
   minutes and seconds, from the first that is not zero, the seconds with their fraction
   (`1.5s`, `1m30s`, `1h0m0s`); a minus in front of a negative span.
3. **`Duration.parse(s)`** reads Go's form: an optional sign, then one or more numbers each with a
   unit — `ns`, `us` (or `µs`, `μs`), `ms`, `s`, `m`, `h` —, a number with a fraction allowed
   (`1.5h`, `.5s`), `0` alone for zero. An empty text throws `ParseError` with `Empty`, a number
   without a unit or a unit unknown, `Invalid`, a span beyond the range, `Overflow`. A fraction is
   taken as Go takes it, `fraction × (unit ÷ 10^digits)` in floating point, so what Go reads this
   reads. A duration's text parses back to it.
4. **`Instant`** is a moment on the wall clock, nanoseconds since `1970-01-01T00:00:00Z`, POSIX
   time without leap seconds: `Instant.now()`, `epochSecs()` and `epochMillis()` rounded down,
   `instant + duration`, `later.since(earlier): Duration`. Instants compare and order as the
   moments they are. The system may set its wall clock back. **`Monotonic`** is a moment on the
   clock that only moves forward, from an unspecified start: `Monotonic.now()`,
   `elapsed(): Duration`.
5. **The calendar** is the proleptic Gregorian one, every year an `int` holds. `Date.of(year,
   month, day)` and `Time.of(hour, minute, second, nano = 0)` throw `TimeError` for what is no
   date — a month outside 1–12, a day beyond the month's — and no time of day — 24:00, a second
   60, which POSIX time does not count. A year is a leap year divisible by 4, and by 400 where by
   100 (`isLeapYear()`). `plusDays(n)` moves a date, `dayOfWeek()` is a `Weekday`, `Monday` first.
   Dates and times compare and order; a date's text is ISO 8601's `YYYY-MM-DD` — a year outside
   0000–9999 with its sign and at least four digits —, a time's `HH:MM:SS` and the fraction
   without trailing zeros.
6. **A zone** is a fixed offset from UTC: `Zone.utc`, `Zone.fixed(offset)` — whole minutes under
   a day, else `TimeError`. *(Informative.)* The zones of a database come with M10.
7. **`DateTime`** is a date and a time of day at an offset: `DateTime.of(date, time, zone)`,
   `instant.toDateTime(zone)`, `toInstant()`, `date()`, `time()`, `offset()`. Two compare field by
   field — one moment at two offsets is two date-times, one instant.
8. **RFC 3339** (§5.6) is the text of an `Instant` — in UTC, `Z` — and of a `DateTime` — its offset,
   `Z` for none —, the fraction without trailing zeros, none where it is zero. Parsing is strict: a
   `T` or `t` between date and time, `Z`, `z` or `±hh:mm`, a fraction of any length, cut to
   nanoseconds; a space for the `T`, a missing offset, a date or a time that does not exist is
   `Invalid`, an empty text `Empty`. `Date.parse` reads the full-date alone.

**The zones** (design 10 Q1; M10 S11). `Zone` is UTC, a fixed offset, or a zone of the database:

1. **Where a zone comes from.** `Zone.utc`; `Zone.fixed(offset)` (whole minutes under a day);
   `Zone.load(name)` reads the IANA name's TZif file (RFC 8536, versions 1 to 4: the 64-bit block
   of a version 2+ file, the footer's rule for the years beyond the last transition, leap seconds
   read over) from the system's database — `TZDIR` or `/usr/share/zoneinfo` —, `TimeError {
   kind = .NoZoneData }` where the system has none (Windows), `.NoSuchZone` where it has no such
   zone or the name is none (empty, absolute, with `..`); `Zone.fromTzif(name, bytes)` and
   `Zone.fromPosix(name, tz)` (a POSIX TZ string, `CET-1CEST,M3.5.0,M10.5.0/3`, `EST5EDT`,
   `<+0330>-3:30`; the offsets west-positive as POSIX writes them; daylight time without an
   offset one hour ahead, without a rule the US rule) take data of one's own; `Zone.local()` is
   `TZ` where set (a name of the database, else a POSIX string), else `/etc/localtime`, else UTC.
   `name()`, `isFixed()`, `offsetAt(instant)`, `infoAt(instant)` — `ZoneInfo { offset, isDst,
   abbreviation }` —; `offset()` of a zone of the database is its offset now. Two zones are
   equal by name and kind.
2. **A moment in a zone.** `instant.toDateTime(zone)` takes the offset in force at the moment.
   `DateTime.of(date, time, zone)` resolves a local time: once, it is that moment; in the hour
   the clocks fall back, it is the earlier of the two moments; in the hour they spring forward,
   it moves forward by the gap (`02:30` on the morning of the change is `03:30` at the new
   offset). A `DateTime` keeps its zone: `zone()`, `zoneInfo()`, `withZone(zone)` the same moment
   there, `plusDays(n)` the same local time `n` days on at the offset then in force (a day
   across the change is 23 or 25 hours). Two date-times are equal by date, time and offset; their
   zones' names are not compared.
3. **Patterns** (UTS #35, English). `dateTime.format(pattern)`: `y` the year (`yy` its last two
   digits, more `y` padded to the count), `M` the month (`MM` padded, `MMM` `Jan`, `MMMM`
   `January`, `MMMMM` `J`), `d` the day, `H` the hour of 24, `h` of 12, `m`, `s`, `S…` the
   fraction to as many digits, `a` `AM`/`PM`, `E` to `EEE` `Tue`, `EEEE` `Tuesday`, `EEEEE` `T`,
   `Z` to `ZZZ` `+0100`, `ZZZZ` `GMT+01:00` (`GMT` for none), `ZZZZZ` `+01:00` (`Z` for none),
   `X`/`XX`/`XXX` `+01`/`+0100`/`+01:00` with `Z` for none, `x`/`xx`/`xxx` the same without;
   text in `'…'` as it is, `''` a quote, what is no letter as it is; a letter the pattern does
   not know or a quote not closed is `TimeError`. `DateTime.parseWith(pattern, text, zone =
   Zone.utc)` reads the same fields back: a number takes the digits it finds (a padded field at
   least its width), a name is matched without case, a fraction as many digits as there are,
   `yy` as 1970–2069; what the pattern does not name is 1970-01-01 00:00:00 UTC; an offset field
   makes a fixed zone, without one the zone given resolves the local time; what does not fit is
   `ParseError { kind = .Invalid }`.

## Paths

`std.path` ([design 10 O6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S6a): a path is a string, and there is no
`Path` type. These functions take a path apart and put one together lexically, as Go's
`path/filepath` does; none of them asks the file system.

1. **The system's forms.** `path.separator` is `\` on Windows and `/` elsewhere. On Windows both
   `\` and `/` separate; a path may start with a volume — a drive, `C:`, or a UNC share,
   `\\server\share` —; two names compare without regard to the case of ASCII letters; and what
   these functions build, they build with `\`.
2. **`normalize(p)`** is Go's `Clean`: separators run together, `.` elements dropped, a `..`
   taking the element before it away — above the root it is dropped, in a relative path kept —,
   no separator at the end but the root's, and `.` for nothing. **`join(parts...)`** joins the
   parts that are not empty by the separator and normalizes; it is empty for no such part.
3. **`fileName(p)`** is the last element (Go's `Base`), **`parent(p)`** the rest, normalized
   (Go's `Dir`), **`extension(p)`** the last element's extension with its dot, from its last dot
   (Go's `Ext`; of `.bashrc` that is all of it), **`stem(p)`** the last element without it, and
   **`withExtension(p, ext)`** the path with another extension — a dot added to `ext` where it
   has none, the extension dropped for an empty one.
4. **`isAbsolute(p)`** is Go's `IsAbs` — on Windows a drive with the root, or a UNC share.
   **`relative(base, target): ?string`** is Go's `Rel`: the path that names `target` from `base`,
   `.` for the same place, `null` where none exists — one absolute and the other not, two volumes,
   a base that climbs above where the target is.
5. **`components(p)`** lists the root — with its volume — and then the elements, without the
   empty ones and `.`, keeping `..`; nothing is normalized.

## Files

`std.fs` ([design 10 O4, O5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S6b, S6c): `File`, a handle on a file, and the
conveniences that read or write a file whole or its lines one by one. The directories follow
with S7.

1. **`File.open(path)`** opens to read, **`File.create(path)`** to write — made where it is not
   there, cut to nothing where it is —, **`File.openWith(path, options)`** as an `OpenOptions`
   says: `read`, `write`, `append` (writes at the end), `create`, `truncate`. Options that read and
   write nothing, cut without writing from the start, or create without writing are refused
   (`InvalidInput`).
2. **A file is a `Reader`, a `Writer` and a `Seek`** at its position, and `Closeable`. It reads
   and writes through the caller's slice. A read or a write may take part of it, as rule 2 of
   §Input and output allows.
3. **What a file cannot do is an `IoError`** with its path and what was done — `opened to read`,
   `opened to write`, `read`, `written`, `sought`, `closed` —: `not found: data.txt (opened to
   read)`. The system's errors map to `NotFound`, `PermissionDenied`, `AlreadyExists`,
   `IsDirectory`, `NotDirectory` and `InvalidInput`, and any other to `Other { code }`, the
   system's number. Whether a directory opens as a file and fails at the read, or fails to open,
   is the system's (POSIX opens it; the read says `IsDirectory`).
4. **A file is closed once**: after `close()` every call throws `Closed`, and a second `close()`
   does nothing. A `File` that nothing closes is warned about (06 §7.4).
5. **The I/O pool.** A file's calls run on a few threads of the program's own, started at the
   first call: the running task is parked meanwhile and its thread runs the other tasks. A call
   on a file ends in a bounded time and is no wait in the sense of [10 §1](10-concurrency.md)
   rule 7: in a cancelled task it runs to its end, and the cancellation is thrown at the task's
   next wait. *(Informative.)* Ending early would hand the caller back a buffer the pool still
   writes into. So a `File` declares `IoError` alone (§Input and output rule 2), and so do the
   conveniences below and `FileLinesIter`, though the defaults they use declare `Cancelled` for
   any reader: from a file it cannot come.
6. **The conveniences** read or write a file whole: **`fs.readText(path)`**, its UTF-8 — bytes
   that are no UTF-8 throw `InvalidData` with the path, and a byte order mark is text, as rule 7
   of §Input and output keeps it —, **`fs.readBytes(path)`**, **`fs.writeText(path, text)`** and
   **`fs.writeBytes(path, bytes)`**, which make or cut the file as `File.create` does, and
   **`fs.appendText(path, text)`**, which writes at its end and makes it where it is not there.
   Each closes its file on every way out; what the close throws counts where nothing went
   wrong before ([06 §7](06-errors.md)).
7. **`fs.lines(path)`** gives the file's lines as `TextReader`'s `readLine` gives them, through a
   `FileLinesIter` with `Error = IoError` that is `Closeable`: it closes the file at its end and
   at its first error, a loop that leaves it early closes it ([07 §2](07-statements.md) rule 7),
   and so does `close()`. After its end or an error it gives no more; after `close()` a call
   throws `Closed`, and what it had read ahead is not given.

## Directories

`std.fs` ([design 10 O5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S7a, S7b): what a path names, the directories and
their entries, and what is put together from them. Each call of the system's runs on the I/O pool
(§Files rule 5).

1. **`fs.metadata(path)`** says what a path names, through links: `size` in bytes, `modified`,
   an `Instant`, `isFile` and `isDir` — neither for what is neither —, `readonly`, and
   `isSymlink`, whether the path itself is a link. A link that leads nowhere is not found.
   **`fs.exists(path)`** is whether `metadata` answers: false where it would throw.
2. **`fs.createDir(path)`** makes a directory in one that is there, **`fs.removeDir(path)`**
   removes an empty one, **`fs.remove(path)`** a file, and **`fs.rename(from, to)`** renames on
   one file system, a file that `to` names replaced. What they cannot do is an `IoError` with the
   path and what was done — `made`, `removed`, `renamed to <to>`, `looked at` —, as §Files rule 3
   says. A directory that is not empty is `Other` with the system's code: no kind names it. What
   a directory removed as a file, or a file read as a directory, gives is the system's.
3. **`fs.readDir(path)`** gives the directory's entries in the system's order, without `.` and
   `..`, as `DirEntry`s: `name`, `path` — the directory's joined with the name (§Paths) —, and
   `isFile`, `isDir` and `isSymlink` of the entry itself, a link not followed; its `metadata()`
   follows it. Its `ReadDirIter`, with `Error = IoError`, is `Closeable` and lets the directory
   go as a file's lines let their file go (§Files rule 7). A name that is no UTF-8 is
   `InvalidData` with the directory's path.
4. **`fs.canonicalize(path)`** is the path absolute, its links resolved and its `.` and `..`
   taken out, as the system names it; it must be there. **`fs.absolute(path)`** makes it absolute
   by the working directory and normalizes it (§Paths), and asks nothing more of the file system.
5. **`fs.createDirAll(path)`** makes the directory and every one above it that is not there; a
   directory there already is nothing to do, and something else there is `NotDirectory`.
   **`fs.removeAll(path)`** removes the path and all that is in it: a link is removed, never
   followed into, and nothing there is nothing to do. It removes what it can and throws the first
   error it met.
6. **`fs.copy(from, to)`** copies a file's bytes — `to` made or cut as `File.create` makes it —
   and answers how many. Onto itself, the same file by `canonicalize`, it is `InvalidInput`, and
   from a directory `IsDirectory`, before anything is written.
7. **`fs.walk(path)`** gives the entries under the path, not the path itself: depth first, a
   directory before what is in it, each directory's entries in the byte order of their names,
   and links not followed. It reads each directory whole and lets it go, so it holds nothing
   open; its `Error` is `IoError`, and an error ends it.
8. **`fs.tempDir()`** makes a new directory under the system's directory for temporary files
   and answers its path; **`fs.tempFile()`** makes a new empty file there and answers its path.
   Each name is made where nothing was, so it is the program's alone. Neither is removed by
   itself.

## The console

`std.io` ([design 10 O9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S8a–S8c): the program's standard input, output and
error.

1. **`print(v)`** writes `v`'s text — what its `Display` shows — on the standard output, and
   **`println(v)`** the same followed by a newline; **`eprint(v)`** and **`eprintln(v)`** write
   on the standard error. Each takes one argument of any type that is `Display`; an f-string
   formats more.
2. **Each stream is buffered**: the output a line at a time where it is a terminal, a block at a
   time otherwise; the error always a line at a time. **`flush()`** writes what both hold, the
   output's first. What they hold is written at every end of the program: when `main` returns,
   before a panic's report, and before an error that leaves `main` is reported. These functions
   drop a failed write, but for the one rule 6 names.
3. *(Informative.)* Through one pipe the two streams show the modes: the error's lines come as
   they are written, the output's block at the end. A program another reads while it runs — a
   line someone waits for — flushes, as a C program does.
4. **`stdin()`** is the program's standard input, one for the program: a `Reader` whose reads go
   through a buffer of its own, with **`readLine()`** — the next line without its end, `\n` or
   `\r\n`, and `null` at the end of the input — and **`lines()`**, an iterator of them with
   `Error = IoError`. A `read` takes what a line's read left in the buffer first. The console's
   read runs on the I/O pool as a file's call does (§Files rule 5), so `readLine`, `read` and
   `lines()` — a `StdinLinesIter` of its own — throw `IoError` alone.
5. **`stdout()`** and **`stderr()`** are `Writer`s over the buffers `print` and `eprint` write into,
   so what the two write keeps its order. Their `flush()` throws what the system says — a pipe
   nobody reads is `BrokenPipe`; the console is not `Closeable`.
6. **A standard output nobody reads ends a printing program**: where the flush of `print`,
   `println` or `flush()`, or the one when `main` returns, finds the standard output a pipe nobody
   reads, the program ends as SIGPIPE would have ended it — on POSIX killed by that signal, which
   a shell shows as 141 —, what the error holds written first. A `Writer` of `stdout()` throws
   `BrokenPipe` instead (rule 5), and a failed write to the error is dropped. Where there is no
   such signal (Windows), the write is dropped and the program goes on; where a host embeds the
   program ([13](13-abi.md)), the host's signals decide.

## The terminal

**`std.term`** (design 10 Q7; M10 S10) is the terminal as ECMA-48 writes it: questions about the
standard streams, styles as SGR sequences, the cursor and the screen as sequences to print. No
raw mode (a door).

1. **The questions.** `isTerminal(stream)` for `StdStream.Stdin`, `Stdout` or `Stderr`: whether
   the stream is a terminal (a pipe, a file or nothing is none). `size()`: the columns and rows
   of the terminal on the standard output, `null` where it is none. Under Windows the runtime
   switches a console to virtual-terminal processing when it first writes to it, so the same
   bytes mean the same there.
2. **Styles.** `Style { fg: ?Color, bg: ?Color, bold, dim, italic, underline, inverse, strike }`
   with `Color` the 16 (`Black` … `White`, `BrightBlack` … `BrightWhite`), `Index(n)` of the 256
   and `Rgb(r, g, b)` (each clamped to 0..255). `style.sgr()` is the sequence that turns it on —
   `ESC [` the parameters in the order bold 1, dim 2, italic 3, underline 4, inverse 7, strike 9,
   the foreground (30–37, 90–97, `38;5;n`, `38;2;r;g;b`), the background (40–47, 100–107,
   `48;5;n`, `48;2;r;g;b`), `m` — empty for a plain style; `reset()` is `ESC [0m`. `style.apply
   (text)` is the text between the sequence and the reset where styles are on, the text itself
   else; `style.force(text)` wraps whatever the terminal is; a plain style changes nothing.
3. **When styles are on.** `colorsEnabled()`: `NO_COLOR` set and not empty says no; else
   `FORCE_COLOR` set and not empty says yes; else `TERM=dumb` says no; else the standard output
   being a terminal decides. An empty value counts as not set (`std.os` sets, it does not unset).
4. **The cursor and the screen**, each the sequence to print: `cursorUp(n = 1)` `ESC [nA`,
   `cursorDown` `B`, `cursorForward` `C`, `cursorBack` `D`, `cursorNextLine(n)` `E`,
   `cursorTo(row, column)` `ESC [row;columnH` (both from 1), `cursorHide()` `ESC [?25l`,
   `cursorShow()` `ESC [?25h`, `cursorSave()` `ESC [s`, `cursorRestore()` `ESC [u`,
   `clearScreen()` `ESC [2J ESC [H`, `clearToEnd()` `ESC [0J`, `eraseLine()` `ESC [2K` and a
   carriage return, `eraseToEndOfLine()` `ESC [0K`.

## The system

`std.os` ([design 10 Q9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S9): the program's arguments, its environment, its
working directory, its end, and the facts of the system it runs on. A text the system holds
that is no UTF-8 is taken with U+FFFD for its bad bytes, as `string.fromUtf8Lossy` takes it.

1. **`os.args()`** gives the program's arguments, its own name first, as a new `string[]`.
2. **`os.env(name)`** is the variable's value, or `null` where it is not set; **`os.envs()`** the
   whole environment as a `Map<string, string>`, a snapshot; **`os.setEnv(name, value)`** sets a
   variable for the process and those it starts. A name that is empty or holds `=` or a NUL, or a
   value that holds a NUL, is the program's mistake: `setEnv` panics.
3. **`os.cwd()`** is the working directory, absolute; **`os.setCwd(path)`** moves it. What they
   cannot do is an `IoError` with the path.
4. **`os.exit(code)`** ends the program with `code`: what the console holds is written, and no
   `defer`, no `using` and no other task runs ([06 §7](06-errors.md)).
5. **The facts**: `os.platform()` (`Platform`: `Linux`, `MacOS`, `Windows`, `Other`) and
   `os.arch()` (`Arch`: `X86_64`, `Aarch64`, `Other`), whose texts are the target triples' words
   (`linux`, `macos`, `windows`, `x86_64`, `aarch64`) — the two kinds are `std.core`'s, whose
   `target` holds the build's ([11 §3](11-metaprogramming.md)); `os.homeDir()`, the user's home or `null`;
   `os.tempDir()`, the system's directory for temporary files, absolute (`fs.tempDir()` makes a new
   one in it); `os.hostname()`; `os.cpuCount()`, one at least; `os.pid()`.

## The network

`std.net` ([design 10 O7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S10b, S10c): IP addresses, socket addresses,
TCP, UDP and the resolver. A call that would block parks the task until the thread's poller says the socket is ready,
and is a wait in the sense of [10 §1](10-concurrency.md) rule 7: a cancel ends it with
`Cancelled` (§Input and output rule 2). There are no socket timeouts: `withTimeout` is the one
way. *(Informative.)* POSIX waits for its sockets through epoll or kqueue; Windows waits for its sockets through AFD
poll requests on the thread's completion port (M8b S11).

1. **`IpAddr`** is `V4(a, b, c, d)`, four `uint8`, or `V6(…)`, eight `uint16` groups; it is
   `Equatable`. **`IpAddr.parse(s)`** takes version 4 as four decimal bytes, none with a leading
   zero, and version 6 as RFC 4291 §2.2 writes it — groups of one to four hex digits, `::` once
   for one or more zero groups, an IPv4 tail in the last 32 bits, no zone; anything else is a
   `ParseError`. Its text is version 4 dotted, and version 6 as RFC 5952 §4 has it: lower case,
   no leading zero, the longest run of two or more zero groups — the first of equals — as `::`,
   and an IPv4-mapped address (`::ffff:0:0/96`) with its dotted tail.
2. **`SocketAddr { ip, port: uint16 }`** is `Equatable`; its text, and what `SocketAddr.parse`
   takes, is `192.0.2.1:8080` or `[2001:db8::1]:8080` — a version 6 address in brackets, and only
   it —, the port decimal from 0 to 65535 with no leading zero.
3. **`TcpListener.bind(addr)`** makes a listener; port 0 asks the system for a free one, which
   `localAddr()` says. **`accept()`** waits until a connection comes and gives it as a
   `TcpStream`.
4. **`TcpStream.connect(addr)`** waits until the connection is made; one that nobody listens for
   is `ConnectionRefused`. A stream is a `Reader` and a `Writer`: `read` waits until bytes come
   and answers 0 once the peer has shut its writing; `write` waits until the system takes some.
   A peer that is gone is `BrokenPipe` or `ConnectionReset`. **`shutdown(how)`**, `Shutdown.Read`,
   `.Write` or `.Both`, ends a way of the stream; `setNoDelay(on)` turns Nagle's waiting off;
   `peerAddr()` and `localAddr()` are its two ends.
5. **A socket is closed once** (`Closeable`): after `close()` every call throws `Closed` — a task
   that waits in a call of it, on any thread, runs again and throws it —, and a second `close()`
   does nothing.
6. *(Informative.)* Every wait is the task's own: its thread runs its other tasks meanwhile, so
   one thread serves many connections.
7. **`UdpSocket.bind(addr)`** makes a UDP socket, port 0 as for a listener. **`sendTo(from,
   addr)`** sends `from` as one datagram — whole or not at all — and waits until the system takes
   it; **`recvFrom(into)`** waits for the next datagram and answers how many of its bytes went into
   `into` — the rest of a longer one is lost — and who sent it, a `SocketAddr`.
8. **`resolve(host)`** gives the addresses a name stands for — `localhost`, a name the system's
   resolver knows, or an address's own text — each once, in the resolver's order, as a
   `List<IpAddr>`; a name nobody knows is `NotFound`. It runs on the I/O pool as a file's call does
   (§Files rule 5): no wait in the sense of 10 §1 rule 7.

## URIs

**`std.uri`** (design 10 O11; M10 S5) is RFC 3986, strictly: `Uri` is a reference in its five
parts, `Uri.parse` reads one as the grammar allows, `show` writes it back, `resolve` and
`normalize` are the RFC's algorithms, `percentEncode`/`percentDecode` the encoding per
component, `Query` the pairs of a query. WHATWG's URL is a browser's leniency and not this.

1. **The parts.** `Uri { scheme: ?string, userinfo: ?string, host: ?string, port: ?int, path:
   string, query: ?string, fragment: ?string }`, each `null` where it was not written; the host
   stands without its brackets, `""` for an empty authority (`file:///etc`), `null` for none; a
   port written empty is `null`. `authority()` is the text between `//` and the path,
   `isAbsolute()` whether there is a scheme. `show()` is §5.3: the parts recomposed, an address
   with a `:` in brackets — `parse` and `show` round-trip every text the grammar takes. A `Uri` is
   `Equatable`, `Hashable`, `Debug`, `Display`, `Parse` and `Codable` (its text, as an `Instant`
   is).
2. **`Uri.parse(text)`** is §3 and appendix B: the scheme up to the first `:` where its characters
   are a scheme's and no `/`, `?` or `#` comes first; after `//` the authority up to the next
   `/`, `?`, `#`, split at the last `@` and the port's `:`, a host in brackets an IPv6 address
   (an IPvFuture is refused); the path up to `?` or `#`; the query up to `#`; the fragment. Each
   part is checked against its grammar: `ParseError { kind = .Invalid }` for a character a part
   does not take — a space, a control character, one beyond ASCII, `<`, `>`, `"`, `{`, `}`, `\`,
   a `%` without two hex digits, a port beyond 65535 or with a letter, a second `@` or `#`, a
   first segment holding `:` where there is no scheme and no authority (path-noscheme, §4.2). The
   empty text is the empty reference, `Uri {}`.
3. **`base.resolve(ref)`** is §5.2.2, strict (a reference with the base's scheme is absolute, no
   backward compatibility): the reference's scheme or authority takes over, an empty path keeps
   the base's path and, where the reference has no query, its query, a relative path merges after
   the base's last `/` (at the root where the base has an authority and no path), dot segments go
   (§5.2.4; `removeDotSegments(path)` alone), the fragment is the reference's. The examples of
   §5.4.1 and §5.4.2 hold, each. A relative base gives a relative result (§5.2.1 asks for an
   absolute one; the algorithm does not need it). `normalize()` is §6.2.2 and §6.2.3: the scheme
   and the host in small letters, a percent-encoding of an unreserved character decoded, the
   others' digits in capitals, the dot segments of a path removed where there is a scheme or an
   authority, an empty path with an authority `/`, the scheme's default port dropped — 80 for
   `http` and `ws`, 443 for `https` and `wss`, 21 for `ftp`.
4. **The encoding.** `percentEncode(text, component)` keeps what the component takes as it is and
   writes every other byte as `%` and two capital hex digits, a character beyond ASCII as the
   bytes of its UTF-8: `Component.Userinfo` keeps unreserved, sub-delims and `:`; `Host`
   unreserved and sub-delims; `Path` pchar and `/`; `Segment` pchar (a `/` is encoded); `Query`
   and `Fragment` pchar, `/` and `?`; `Pair` unreserved alone, for a key or a value of a query.
   `percentDecode(text)` reads `%XX` back and is `ParseError { kind = .Invalid }` for a `%`
   without two hex digits or bytes that are no UTF-8; a `+` stays. **`Query`** is the pairs of a
   query in the order written, a key more than once allowed: `Query.parse(text)` splits at `&`
   and the first `=` (a part without `=` is a key with an empty value, an empty part is skipped),
   reads a `+` as a space and the percent-encodings; `get(key)` is the first value, `all(key)`
   every one, `has`, `length`, `isEmpty`, `pairs()`; `add` appends, `set` replaces the key's first
   pair and drops its others (appends where the key is new), `remove` drops the key; `show()`
   writes `key=value` joined by `&`, each encoded for `Pair` (a space is `%20`). `uri.queryPairs()`
   is the query parsed, empty where there is none.

## HTTP

**`std.http`** (design 10 Q6; M10 S7 the client, S8 the server) is HTTP/1.1 over `Reader` and
`Writer`: the message types, a client that keeps its connections, a server with a task per connection. No TLS of its own (a
package's transport brings it), no HTTP/2, no cookies.

1. **The message types.** `Method` (`Get`, `Head`, `Post`, `Put`, `Delete`, `Patch`, `Options`,
   `Other(token)`; `Method.of("GET")`, its `show()` the token); `Status { code, reason }` with
   `Status.of(code)` giving RFC 9110's phrase, `isSuccess`, `isRedirect`, `isClientError`,
   `isServerError`, `isInformational`, its `show()` `404 Not Found`; **`Headers`**, the fields in
   the order written, names compared without case: `get` (the first value), `all`, `has`, `set`
   (this value alone), `add`, `remove`, `length`, `pairs`. **`Request { method, uri, headers,
   body: ?Reader, contentLength: ?int }`**, `Request.get(uri)`, `Request.post(uri, bytes,
   contentType)`, `setBody(bytes)`, `setText(text)`. **`Response { status, headers, body }`** with
   `bytes()`, `text()` (UTF-8, a wrong byte U+FFFD) and `json<T>()` (`std.json` into a `Decode`
   type); `body` is a `Reader` that ends where the message does.
2. **The client.** `Client.new(options)` with `ClientOptions { followRedirects = false,
   maxRedirects = 10, timeout = null, keepAlive = true, userAgent = "lyric5", transport = null
   }`; `client.get(uri)` and `client.send(request)` give the response once its head is read.
   The request goes out as RFC 9112 writes it: the request target is the path (`/` for none) and
   the query, `Host` the authority (the port where it is not the scheme's), `User-Agent` where
   none is set, a body with `Content-Length` where its length is known and in chunks
   (`Transfer-Encoding: chunked`) else, `Content-Length: 0` for a POST, PUT or PATCH without one.
   The response's body is framed by the head: none for HEAD, 204 and 304; `Transfer-Encoding:
   chunked` (extensions ignored, trailers read away); `Content-Length`; up to the connection's
   close else (HTTP/1.0 among them). An interim response (100, 103) is read away. A connection is
   kept for the next request to the same scheme, host and port once the body has been read to its
   end, unless a side said `Connection: close`, the body ran to the close, or `keepAlive` is off —
   a body left unread gives the connection up; an idle connection the peer closed meanwhile is
   tried again on a new one (a request without a body). `client.close()` drops the idle ones.
3. **Redirects, time, transport.** With `followRedirects`, a 301, 302, 303, 307 or 308 with a
   `Location` is followed, the target resolved against the request's URI (§URIs), up to
   `maxRedirects` — more is `HttpError { kind = .Redirects }`; a 303, and a 301 or 302 after a
   POST, go on as a GET without the body; a 307 or 308 keep the method, and with a body are
   refused (it cannot be sent again). `timeout` spans the whole exchange — the connection, the
   request, the head — and ends it with `TimedOut`, the connection closed. `transport` is a
   `fn(host, port) -> Stream` (`Stream :: [Reader, Writer, Closeable]`; a `TcpStream` is one)
   that makes the connection; `http` connects over TCP where it is `null`, `https` needs one.
   What is refused: a scheme that is neither (`HttpError { kind = .Unsupported }`), a URI
   without a host, a status line or header line that is not HTTP/1.1's (`.Protocol`: a version
   that is none, a `Content-Length` that is no number, a folded line, more than 256 lines or a
   line beyond 64 KiB), a body that ends early or a chunk that is none (`IoError`,
   `UnexpectedEof` or `InvalidData`). The errors of the connection are `IoError`, a cancel
   `Cancelled`. `http.get(text)` is a GET with the defaults and redirects followed.

4. **The server** (M10 S8). `Server.bind(addr, options)` with `ServerOptions { keepAlive = true,
   serverName = "lyric5" }`, `localAddr()`, `serve(handler)` — `handler: fn(Request) -> Response
   throws Error` — and `shutdown()`. `serve` accepts until the listener is closed and takes a task
   per connection; on it each request is read as the client writes one: the request line
   (origin-form, absolute-form or `*`; HTTP/1.1 or 1.0), the headers (§3's limits), the body
   framed by `Content-Length` or `Transfer-Encoding: chunked` and given to the handler as the
   request's `body` (a `Reader`; `request.bytes()`, `text()`, `json<T>()` read it whole; a body
   the handler leaves is read away before the next request). `Expect: 100-continue` is answered
   with `100 Continue` before the handler runs. The handler's response goes out as `HTTP/1.1`
   with `Server`, `Content-Length` where the body's length is known and in chunks else, nothing
   for a HEAD, a 204, a 304 or a 1xx; `Response.of(status, bytes, contentType)`,
   `Response.withText(text, status)`, `Response.withJson(value, status)`, `Response.stream(status,
   reader, length)` and `Response.empty(status)` make one, its `headers` are the handler's to
   set. A handler that throws answers `500` with the error's message as text. The connection
   stays for the next request unless the request was HTTP/1.0 without `keep-alive`, a side said
   `Connection: close`, `keepAlive` is off, or the server is shutting down; it is closed after
   the peer's remaining bytes are read away (a close with bytes unread would reset it and lose the
   answer). A request that is none — a request line or version that is none, no `Host` under
   HTTP/1.1, a target that is no URI, a `Content-Length` that is no number, a transfer encoding
   that is not chunked, a folded line — is answered `400 Bad Request` with the reason as text and
   the connection closed. `shutdown()` closes the listener (`serve` returns), closes the
   connections waiting for a request, and lets a request under way be answered first.

4. **The server** (M10 S8). `Server.bind(addr, options)` with `ServerOptions { keepAlive = true,
   serverName = "lyric5" }`, `localAddr()`, `serve(handler)` — `handler: fn(Request) -> Response
   throws Error` — and `shutdown()`. `serve` accepts until the listener is closed and takes a task
   per connection; on it each request is read as the client writes one: the request line
   (origin-form, absolute-form or `*`; HTTP/1.1 or 1.0), the headers (§3's limits), the body
   framed by `Content-Length` or `Transfer-Encoding: chunked` and given to the handler as the
   request's `body` (a `Reader`; `request.bytes()`, `text()`, `json<T>()` read it whole; a body
   the handler leaves is read away before the next request). `Expect: 100-continue` is answered
   with `100 Continue` before the handler runs. The handler's response goes out as `HTTP/1.1`
   with `Server`, `Content-Length` where the body's length is known and in chunks else, nothing
   for a HEAD, a 204, a 304 or a 1xx; `Response.of(status, bytes, contentType)`,
   `Response.withText(text, status)`, `Response.withJson(value, status)`, `Response.stream(status,
   reader, length)` and `Response.empty(status)` make one, its `headers` are the handler's to
   set. A handler that throws answers `500` with the error's message as text. The connection
   stays for the next request unless the request was HTTP/1.0 without `keep-alive`, a side said
   `Connection: close`, `keepAlive` is off, or the server is shutting down; it is closed after
   the peer's remaining bytes are read away (a close with bytes unread would reset it and lose the
   answer). A request that is none — a request line or version that is none, no `Host` under
   HTTP/1.1, a target that is no URI, a `Content-Length` that is no number, a transfer encoding
   that is not chunked, a folded line — is answered `400 Bad Request` with the reason as text and
   the connection closed. `shutdown()` closes the listener (`serve` returns), closes the
   connections waiting for a request, and lets a request under way be answered first.

## Processes

`std.process` ([design 10 O8, Q9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S12a): a child started, its
streams, its end.

1. **`Command { program, args, cwd, env, stdin, stdout, stderr }`** is an options struct: the
   program a path or a name looked up on `PATH`; `args` after its name; `cwd` the parent's where
   `null`; `env` pairs set over the parent's environment; each stream `Stdio.Inherit` — the
   default —, `Stdio.Piped` or `Stdio.Null`. A NUL in an argument or a variable, or a variable's
   name that is empty or holds `=`, is `InvalidInput`.
2. **`spawn()`** starts the child. A program that is not there is `NotFound`, one that may not run
   `PermissionDenied`, the program as the path. Its piped streams are `stdin: ?PipeWriter` and
   `stdout`, `stderr: ?PipeReader` — a `Writer` and `Reader`s whose calls wait as a socket's do
   (§The network), and that are `Closeable`; closing `stdin` is the end of the child's input.
3. **`wait()`** closes the child's `stdin`, then waits for its end — a wait a cancel ends — and
   answers an **`ExitStatus`**: `success()`, `code(): ?int` — 0 to 255 on POSIX, any 32 bits on
   Windows —, and `signal(): ?Signal`, the signal that ended it; its text is `exit code 3` or
   `signal 9`. Every task that waits for one child, on
   any thread, sees its end.
4. **`kill()`** ends the child — SIGKILL on POSIX; on Windows its code is then 1 —, **`signal(s)`**
   sends it `s` (10 Q9), `Unsupported` on Windows, which has no signals; neither touches a child
   that has ended.
5. **`output()`** starts the child with no input and both other streams piped, takes the two to
   their ends at once and waits: an **`Output { status, stdout, stderr }`**. **`status()`** starts it
   with the parent's streams and waits.
6. *(Informative.)* On POSIX a child's end comes as SIGCHLD, which the runtime keeps for itself
   (10 Q9). A child starts with SIGPIPE at its default although the program ignores it: an ignored
   signal would outlive the exec. On Windows (M8b S12b) a child gets its arguments on one command
   line, quoted as the C runtime reads them back, and inherits its three handles alone; its pipes'
   calls block, and run on the I/O pool as a file's do (§Files rule 5).

## Characters

A `char` is a Unicode scalar value ([design 10 S4, S5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8c S1). What it is,
`std.core` answers from the Unicode Character Database, its version pinned:
`std.string.unicodeVersion` is `"18.0.0"` for Lyric 5.0.

1. **`category(): UnicodeCategory`** is the character's general category (UAX #44). The enum's
   thirty variants are the standard's, in its order: `UppercaseLetter`, `LowercaseLetter`,
   `TitlecaseLetter`, `ModifierLetter`, `OtherLetter`, `NonspacingMark`, `SpacingMark`,
   `EnclosingMark`, `DecimalNumber`, `LetterNumber`, `OtherNumber`, `ConnectorPunctuation`,
   `DashPunctuation`, `OpenPunctuation`, `ClosePunctuation`, `InitialPunctuation`,
   `FinalPunctuation`, `OtherPunctuation`, `MathSymbol`, `CurrencySymbol`, `ModifierSymbol`,
   `OtherSymbol`, `SpaceSeparator`, `LineSeparator`, `ParagraphSeparator`, `Control`, `Format`,
   `Surrogate`, `PrivateUse`, `Unassigned`. No `char` is a `Surrogate`; a code point the database
   does not list is `Unassigned`.
2. **`isX` asks Unicode, `isAsciiX` ASCII.** `isAlpha` is a letter, the categories Lu, Ll, Lt,
   Lm and Lo; `isDigit` a decimal digit of any script, Nd; `isAlphanumeric` either; `isUpper` Lu;
   `isLower` Ll; `isControl` Cc; `isWhitespace` the property White_Space. `isAsciiDigit` is
   `0`–`9`; `isAsciiAlpha` `a`–`z` and `A`–`Z`; `isAsciiHexDigit` the digits and `a`–`f`, `A`–`F`;
   `isAsciiWhitespace` the space, tab, line feed, form feed and carriage return.
3. **Case maps one character to one.** `toUpper()` and `toLower()` are the database's simple
   case mappings; a character without one maps to itself — `'ß'.toUpper()` is `'ß'`. No locale
   takes part.
4. **Digits are ASCII**, as `parse` reads them: `toDigit(radix): ?int` reads `0`–`9`, then `a`–`z`
   or `A`–`Z` as 10 to 35, and is `null` for a character that is no digit of the base;
   `char.fromDigit(n, radix): ?char` writes the digit `n`, its letters lowercase, and is `null`
   where `n` is no digit of the base. A radix outside 2–36 panics (`LYR-RT0008`).

## Strings

A `string` is immutable UTF-8 (design 10 S1). Its members are `std.core`'s and stand **once on
`StringView`** (below), which a string reaches through a view of all of itself (rule 4); `length()`
and `isEmpty()` it has itself. What cuts gives a **view** of the text, no copy; what builds gives a
new string. A pattern `p` is a **`Pattern`** (design 10 S2) — a view or a string, a `char`, a test
of characters `fn(char) -> bool` (through the block on its function type, [05 §13](05-interfaces.md)
rule 6), or a type of the program that conforms:
`Pattern { fn matchAt(text: StringView, at: int): ?int; fn matchBefore(text: StringView, end: int): ?int; }`,
the end of a match that begins at byte `at`, and the start of one that ends at byte `end` —
`at` and `end` a character's first byte or the text's length. A third member,
`fn nextIn(text: StringView, from: int): ?int`, the first such byte at or after `from` where a
match begins, has a default that tries `matchAt` at each; a pattern may give a faster one. One
signature per operation takes any of them:

- `length()`, the bytes, `O(1)`; `isEmpty()`; `charCount()`, the characters, `O(n)`; `chars()`,
  the characters decoded, an `Iterator` of `char` that is `DoubleEnded` — `nextBack()` takes them
  from the end, and the two ends meet; `charIndices()`, each character with the byte index it
  begins at, an `Iterator` of `(int, char)`.
- `string` is `Ordered` and `TotalOrder` byte by byte, which is the order of the code points.
- The search: `contains(p)`, `startsWith(p)`, `endsWith(p)`; `find(p)` and `rfind(p)`, the byte
  index of the first and the last `p` or `null` — an empty `p` stands at 0 and at the length;
  `count(p)`, the occurrences none overlapping another, an empty `p` between every two characters
  and at both ends.
- `split(sep)`, the parts between the separators in order, views, empty ones kept — a separator
  that matches the empty text panics; `splitN(sep, n)`, at most `n` parts, the last one the rest,
  none for `n` of 0; `splitOnce(sep)`, the views before and after the first, or `null`;
  `matches(p)`, the matches in order, views, none overlapping another; `lines()`, views split at
  `\n` with a `\r` before it taken off and no empty line after a last `\n`.
- `trim()`, `trimStart()`, `trimEnd()`, the view without the white space — the characters with
  the property White_Space (§Characters); `trimMatches(p)`, `trimStartMatches(p)`,
  `trimEndMatches(p)`, the view without the matches of `p` at the ends, again and again — a match
  of the empty text takes nothing; `isBlank()`, whether it holds nothing but white space, the
  empty text too; `stripPrefix(p)` and `stripSuffix(p)`, the view of the rest, or `null` where
  `p` is not there.
- `toUpper()`, `toLower()`, a new string, each character by its simple case mapping
  (§Characters rule 3): `"straße".toUpper()` is `"STRAßE"`, and a final sigma is no context.
- `toBytes()`, the bytes, a new `uint8[]` — a copy, since a string does not change (design 10
  S12d); `string.fromChars(chars)`, the text of an iterator's characters in order, throwing what
  the iterator throws; `parse<T :: [Parse]>()`, `T.parse(s)` with `T` from where the result goes
  — `let n: int = try s.parse();`.
- `replace(p, with)`, a new string with every `p` replaced, none overlapping — a `p` that matches
  the empty text panics; `replaceN(p, with, n)`, the first `n` replaced, all of them where `n` is
  negative; `padStart(width, fill = ' ')` and `padEnd(width, fill = ' ')`, a new string, the width
  in characters.
- **Bytes to text** (design 10 S3): `string.fromUtf8(bytes)`, the text the bytes of a
  `Slice<uint8>` are, copied — bytes that are no well-formed UTF-8 (an overlong form, a surrogate,
  beyond U+10FFFF, a byte that begins nothing, a sequence cut short) throw a **`Utf8Error`**
  (`std.core`) whose `offset` is the first byte that is not, as the data's fault (10 B3);
  `string.fromUtf8Lossy(bytes)`, the text with each maximal part of a sequence that is not
  well-formed replaced by U+FFFD — the Unicode Standard's recommended practice (3.9).
- **`StringBuilder`** (`std.string`, a class): `appendStr(s)` of a string or a view,
  `appendChar(c)`, `append(v)` of a `Display`, `length()` in bytes, `clear()`, `toString()` — in a
  buffer that doubles, no chain of concatenations.

**`StringView`** is the view of a string's bytes (design 10 S1, 03 A2), a primitive of `std.core`
visible without an import, as `Slice<T>` is ([03 §5.2](03-types.md) rule 6):

1. A view is a pointer into a string's bytes and a length, two words, copied by a binding; it
   reads the bytes and never writes them. There is no lifetime: the string lives as long as any
   view of it does ([03 §5.2](03-types.md) rule 5).
2. `s[a..b]` on a string or a view is the view of the bytes from `a` up to but not including `b`,
   in the forms of [03 §5.2](03-types.md) rule 2 — `s[a..=b]`, an open end, `^n` as a bound. The
   bounds satisfy `0 ≤ a ≤ b ≤ length()`, and neither falls inside a character — on a byte that
   continues one —, or the expression **panics** with `LYR-RT0003`, in every profile. A view of a
   view is a view of the same string.
3. `s[i]` on a string or a view is the **character** that begins at byte `i`, `i` an `int` as an
   array's index is ([03 §5.1](03-types.md)): outside `0 ≤ i < length()`, or at a byte that
   continues a character, a panic (`LYR-RT0003`). Counted from the end a byte is rarely where a
   character begins: `^n` stands as a bound of a range only (`LYR-SEM0114`). The characters are
   read and never written through the index (`LYR-SEM0019`). A string and a view conform to
   `Index<int>` with `Output = char` ([05 §12](05-interfaces.md) rule 9), so a type parameter
   that asks for it takes them.
4. At a coercion site a string stands where a view is expected and gives a view of all of
   itself; a view never stands where a string is expected (`LYR-SEM0001`) — `toString()` copies
   its bytes into a string of their own. A **receiver** is such a site, as an array's is for the
   members written on `Slice<T>` ([03 §5.2](03-types.md) rule 4): where the string's own blocks
   give no member of the name, `s.m()` is the view's member, called on a view of all of `s`. A
   view matched against a string literal compares its bytes ([09 §2](09-patterns.md) rule 3).
5. A view has `length()`, its bytes, built in as a slice's is, `isEmpty()` and `toString()`. It
   is `Equatable`, `Hashable`, `Ordered` and `TotalOrder` by its bytes, as a string is — it
   hashes as the string of its bytes —, `Display`, its text, and `Debug`, quoted. `==`, `!=` and
   the orderings between a string and a view compare the two as views: `"abc"[1..] == "bc"`.

**Debug of text** (design 10 S14) writes a string, a view or a `char` as it would be written: between
`"` — a `char` between `'` —, with `\\`, the quote, `\n`, `\r`, `\t` and `\0` escaped, and a character of
the categories Cc, Cf, Cs, Co, Cn, Zl, Zp, or a space separator other than the space, as `\u{…}`,
its scalar value in lowercase hex. A container's `Debug` and `Display` take it (§Collections),
so `["a\"b", "c"]` shows as it is written.

**Repetition** (design 10 C7): `s * n` is the text `s` `n` times over — `""` for `n` of 0 — and a
negative `n` panics with `LYR-RT0007`, as `[x] * n` does; `n * s` is refused, the one order of
[03 §5.1](03-types.md).

## Compression

**`std.compress`** (design 10 Q8; M10 S9) is DEFLATE (RFC 1951), zlib (RFC 1950) and gzip (RFC
1952), whole in Lyric: an inflater, a deflater at the levels 0 to 9, the two wrappings, each as a
stream adapter and whole in memory.

1. **The formats.** `Gzip.compress(bytes, level = 6)` and `Gzip.decompress(bytes)`, `Zlib.*` and
   `Deflate.*` (raw) over bytes in memory; **`GzipWriter<W :: [Writer]>`**, `ZlibWriter`,
   `DeflateWriter` (`new(inner, level = 6)`; `Writer` and `Closeable` — `close` writes the final
   block and the trailer and flushes `inner`, a second `close` does nothing, a `write` after it is
   `IoError { kind = .Closed }`; `flush` ends the block under way and writes an empty stored block
   so the bytes so far are whole) and **`GzipReader<R :: [Reader]>`**, `ZlibReader`,
   `DeflateReader` (`new(inner)`; `Reader`, 0 at the stream's end; `DeflateReader.bytesOut()`,
   `GzipWriter.bytesIn()`). gzip's header is the ten bytes with no name, no time, `OS` 255 and
   `XFL` 2 at level 9 and 4 at level 1; its trailer CRC-32 and the size, both checked; a header
   with an extra field, a name, a comment or a header CRC is read over; members in a row read as
   one. zlib's header is `78` with the level's `FLEVEL` (0 below 2, 1 below 6, 2 at 6, 3 above)
   and the check; its trailer the Adler-32, checked; a preset dictionary is refused.
2. **The deflater.** Level 0 stores (blocks of at most 65535 bytes, a final empty one); 1 the
   fixed tables over a greedy LZ77; 2 and above dynamic tables (the code lengths from the block's
   frequencies, at most 15 bits, 7 for the code length code; the lengths run-length coded) — a
   block is written with the fixed tables or stored where that is smaller; 4 and above lazy
   matching, the chains longer and the nice length higher with the level (zlib's table). The
   window is 32 KiB, a block at most 16384 symbols. A level outside 0..9 is `CompressError`; -1
   is 6. What the deflater writes, zlib and the platform's `gzip` read; what they write, the
   inflater reads (the artifact: `programs/gzipfile.lyr` against .NET's `GZipStream` and `gzip
   -d`).
3. **The inflater** reads stored, fixed and dynamic blocks (an over-subscribed code, a block of
   type 3, a stored length that does not match its complement, a distance before the start, a
   length or distance code beyond the tables, a stream that ends inside a block are each
   `IoError { kind = .InvalidData }` with a `CompressError` inside, its `detail` the reason). It
   takes from `inner` what it needs and, once a block could be the last, one byte at a time, so
   a wrapper reads its trailer where the stream ended.
4. **In the client.** With `ClientOptions.decompress` (the default), `std.http`'s client says
   `Accept-Encoding: gzip, deflate` and decodes a response's `Content-Encoding: gzip` (or
   `x-gzip`, or `deflate` as zlib) as the body is read; the response's headers then lose
   `Content-Encoding` and `Content-Length`; the connection returns as the raw body ends.

## Regular expressions

**`std.regex`** (design 10 S8, B1; M10 S6) is RE2's syntax matched in linear time: a pattern
is a tree, the tree a Thompson NFA, the NFA run by a Pike VM that carries the captures with
each thread — every character of the text meets each instruction at most once, so the time is
the text's length times the pattern's, whatever the pattern. What makes a backtracker's time
exponential is not here: no backreferences, no lookaround.

1. **The syntax** (`Regex.new(pattern)`): literals; `.` (no newline unless `s`); classes
   `[a-z]`, `[^…]` (a `]` first and a `-` last are themselves), `\d \w \s` and their capitals
   (ASCII, as RE2: `0-9`, `0-9A-Za-z_`, `\t \n \v \f \r` and the space), `[:alpha:]` and the
   other POSIX names inside a class (`[:^alpha:]` negated), `\pL`, `\p{Lu}`, `\PL` over the
   Unicode categories by their one- or two-letter names (no scripts); groups `(…)`, `(?:…)`,
   `(?P<name>…)` and `(?<name>…)`; alternation `|`; the repetitions `* + ? {n} {n,} {n,m}`, each
   lazy with a `?` after it, a count at most 1000, a `{` that is no count a literal; the anchors
   `^` and `$` (the text's ends; the lines' under `m`), `\A`, `\z`, `\b`, `\B` (ASCII word
   characters); the escapes `\n \t \r \f \v \a \0`, `\xHH`, `\x{H…}`, and `\` before a
   punctuation mark; the flags `i`, `m`, `s` as `(?i)` for the rest of the group, `(?i:…)` for
   a group, `(?-i)` off. A pattern outside this is `RegexError { offset, detail }`: a group or
   class not closed, an unmatched `)`, a repetition of a repetition or of nothing, a range
   reversed, an escape that is none (a backreference `\1` among them), a flag that is none (a
   lookaround `(?=` among them), a name twice, a category or POSIX class that is none, a code
   point beyond U+10FFFF, a repetition beyond 1000.
2. **The match.** Alternation is leftmost-first as in Perl and RE2: of the matches starting at
   the leftmost position the first alternative's wins, a greedy repetition takes the most and a
   lazy one the least, so `a|ab` finds `a` in `ab` and `ab|a` finds `ab`. A `Match` is `start`
   and `end` (byte offsets, as a string's indices are; a character beyond ASCII is one character
   to `.` and to a class), `value` (its text, also its `show()`), `group(i)` and `span(i)` for
   the groups (0 the whole; `null` for one that took no part or does not exist — the last
   iteration's capture stands), `named(name)`, `groups()`. The empty pattern matches the empty
   text at every position.
3. **The verbs.** `isMatch(text)`; `find(text)` the leftmost match with its groups, `findFrom(text,
   at)` from a byte offset; `findAll(text)` the matches in turn, left to right, none overlapping,
   an empty match right after a match skipped (as Go does); `replace(text, template)` the first
   and `replaceAll` every match replaced by the template — `$1`, `${1}`, `${name}` the groups, `$0`
   the whole, `$$` a `$`, an unmatched group empty, a `$` before anything else itself;
   `split(text)` the pieces between the matches (Go's `Split` with no limit: an empty text is
   one empty piece, a match at the start adds no empty piece before it). `pattern()`,
   `groupCount()`, `groupNames()`.
4. **The time is linear.** `(a*)*b` over a hundred thousand `a`, `(x+x+)+y` over twenty
   thousand `x`, `(a?){30}a{30}` over thirty `a`: each ends in the time of one pass. *(A lazy
   DFA for `isMatch` and `find` without captures is a door the plan opens at Messpunkt 4; a
   `comptime Regex.new` is one of the macro line.)*

## Collections

`std.collections` holds the containers (design 10 B7); none is safe across threads (C11). An
element is whatever a container's bounds admit, an object included, and every slot holds its own
(M8a S16).

An array literal stands for a container where one is expected ([03 §5.1](03-types.md) rule 2;
design 10 K4): `List<T>`, `Deque<T>`, `Heap<T>` and `Set<T>` are each a **`FromArrayLiteral<T>`**
of `std.core` — `static fn fromLiteral(items: T[]): Self`, the container of the elements, in
order — and `Map<K, V>` is one of `(K, V)`, a later value of a key replacing the earlier one;
`Set` and `Map` with the default hasher. `let s: Set<int> = [1, 2, 3];`,
`let m: Map<string, int> = [("a", 1)];`.

- **`List<T>`** (C3), a class: its elements in order, at the front of a buffer that doubles when
  full. `new()`, `of(xs)` (a copy of the array), `from(it)` (the values of an iterator, in order),
  `withCapacity(n)` — room for `n` elements before
  it grows, taken at the first push, since a list holds no value it was not given (10 N3; M8a S14);
  every container's `withCapacity(n)` panics on a negative `n`. `xs[i]` and `xs[i] = v` through `IndexSet<int>`
  ([05 §12](05-interfaces.md) rule 9), outside `0 ≤ i < length()` a panic (`LYR-RT0003`); `get(i)`,
  `null` there. `push(v)`, `pushAll(xs)`, `pop()` (`null` for none), `insert(i, v)`, `removeAt(i)`,
  `removeWhere(p)` (how many went; a `p` that throws ends it there — what it decided is done,
  the rest kept), `clear()` (the room stays), `truncate(n)`, `swap(i, j)`,
  `toArray()` (a copy), `shrinkToFit()` (the room cut down to the elements — a view taken before
  keeps the buffer it was taken of); of an `Equatable` element `contains(x)`, `remove(x)` (whether there was one)
  and `dedup()` (runs of equal ones kept once). `asSlice()` is a view of the buffer, so the members
  of arrays and views reach the list — a sort writes it; a push past the room moves the list to a
  new buffer, and an older view keeps the older one. A list is `Iterable` front to back
  ([10 I9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)): a change of
  its length while it is walked panics at the next pull (`LYR-RT0016`, as for a map, a set and a
  deque).
- **`Map<K :: [Hashable], V, H :: [Hasher] = DefaultHasher>`** (C4), a class: what it holds, in
  no order of its own, each key once. `Map<K, V>.new()` hashes with the process's key, so its
  order differs from run to run, and `withCapacity(n)` is the same with room for `n` keys before
  it grows; `withHasher(seed)` takes a hasher, which is a value the map
  copies fresh for every key — `FixedHasher.new()` hashes alike in every run; `from(pairs)`, the
  pairs of a view in a map, a later value of a key replacing the earlier one. `m[k]` through
  `IndexSet<K>` with `Output = ?V`: the value under `k` or `null`; `m[k] = v` puts `v` there, and
  `m[k] = null` takes `k` out. `insert(k, v)`
  answers the value it replaces or `null`; `get(k)` the value or `null`; `containsKey(k)`;
  `remove(k)` the value taken out or `null`; `length()`, `isEmpty()`, `clear()`; `getOr(k, d)`;
  `getOrInsert(k, make)`, `make()`'s value inserted where `k` has none; `update(k, f)`, whether
  there was one to replace; `retain(p)`, how many went. Their functions may throw, and the call
  throws it with the map still a map: `make()` inserts nothing, `f` replaces nothing, `retain`
  keeps what it has not judged. A map is `Iterable` over its entries,
  `(K, V)`, `entries()` too, and `keys()` and `values()` walk the same order — none the map's own (I8); a change of
  the map while it is walked panics at the next pull (I9). *(Informative.)*
  A Swiss table: groups of eight slots under a control word, the hash's seven low bits compared
  a group at a time, at most seven of eight slots filled.
- **`Set<T :: [Hashable], H :: [Hasher] = DefaultHasher>`** (C5), a class over a map's keys:
  `new()`, `of(xs)` (the array's values, each once), `withCapacity(n)`, `withHasher(seed)`, `insert(v)` (whether it was not there), `contains(v)`, `remove(v)`
  (whether it was there), `length()`, `isEmpty()`, `clear()`; `Iterable` over its values, in no
  order of its own. Its operations are methods, no operators: `union(o)`, `intersect(o)`,
  `difference(o)` and `symmetricDifference(o)`, each a new set hashing as this one does;
  `isSubset(o)`, `isSuperset(o)` and `isDisjoint(o)` — the empty set a subset of every set.
- Every iterator's **`toList()`** collects what it gives into a `List` (I4).
- **`Deque<T>`** (C6), a class over a ring buffer: `new()`, `withCapacity(n)`, `pushFront(v)`, `pushBack(v)`,
  `popFront()` and `popBack()` (the value or `null`), `peekFront()`, `peekBack()`, `length()`,
  `isEmpty()`; `[i]` from the front, panicking outside `0 ≤ i < length()` (`LYR-RT0003`);
  `Iterable` front to back, a change while it is walked panicking at the next pull (I9).
- **`Heap<T :: [TotalOrder]>`** (C1), a binary heap over a list, **the least value first** (the
  review's A1; the greatest first is a heap of a type whose order is reversed):
  `new()`, `withCapacity(n)`, `of(xs)` — the array's values, copied, in linear time —, `push(v)`,
  `pop()` and `peek()` (the value or `null`), `length()`, `isEmpty()`.
  *(Informative.)*

**Membership** (10 C12; M8a S15): a `List` of an `Equatable` element is a `Contains<T>` through
`contains(x)`, a `Set` through its own, a `Map` of its keys, `contains(k)` being `containsKey(k)` —
what `x in xs` asks ([05 §12](05-interfaces.md) rule 10). A **`Range<T>`** and a
**`RangeInclusive<T>`** of an `Ordered` `T` are `Contains<T>` too: `start <= x && x < end`, the
inclusive one with `x <= end`. A `string` and a `StringView` are `Contains<char>`: `'b' in "abc"`,
through the view's `contains<P :: [Pattern]>` at `P = char` ([05 §1](05-interfaces.md) rule 2) —
the same member that finds a text in a text.

**Clone** (10 K5; N2a). A `List`, a `Deque`, a `Set`, a `Map` and a `Heap` are `Clone` where their
elements — a map's keys and values — are: `clone()` is a new container of the elements' clones, as
deep as the element type owns; a map keeps its hasher, a heap and a deque their order.

**Equality and display** (10 C9; M8a S14). A `List` and a `Deque` are `Equatable` where their
elements are, element by element in order; a `Set` by its values and a `Map` by its entries —
the same keys, equal values, where `V` is `Equatable` — in any order. Each is `Debug` and
`Display` alike where its elements, a map's keys and values, are `Debug`: `[1, 2]` for a list
and a deque, `{1, 2}` for a set, `{"a": 1}` for a map, `{}` for an empty set or map, a set's and
a map's in the order they are walked. A `Heap` is `Debug`, its values in brackets in an order of
its own that no program may rely on. None is `Hashable` (10 C8).

A value that hashes is **`Hashable`**, `fn hash<H :: [Hasher]>(&h: H): void`, a child of
`Equatable`: it writes its parts into the hasher, and equal values write the same — nothing checks
it. An integer writes its word (`writeInt`, `writeUint` for the unsigned), a `bool` a byte, a
`char` its code point as a word, a `string` its bytes and then 255, which no UTF-8 text holds. A
`float` is none (10 SL-26); an array, a view, a `List`, a `Map` and a `Set` are none either (10
C8): their slots can be written. A type's own hash is synthesized ([05 §14](05-interfaces.md)).
An object hashes by its address where its class is `Identity` ([05 §14](05-interfaces.md) rule
8): `hashIdentityInto(o, &h)` writes it as `writeInt` does.

## Benchmarks

A function marked **`@Bench`** is a benchmark (design 10 X4; M8c S12b): `fn name(&b: Bench)`, in
a module under `src/` or `tests/`, which `lyric bench` runs ([14 §4](14-cli.md)). `Bench` is
`std.core`'s, and in the prelude as `Test` is; the bench a benchmark is handed is its measure.

- **`b.iter { … }`** runs the block until its time a run is known: once to warm up, then rounds
  of more runs until one takes a tenth of a second, then five rounds of that many. The bench keeps
  the round of the median time — its `runs`, its `nanos`, the `allocations` this thread made in
  it and their `allocatedBytes`. The loop's call of the block is in the time.
- **`b.bytes(n)`** says that a run handles `n` bytes; the report gives the megabytes a second.
- **`blackBox(x)`** of `std.core` hands `x` back through a point the compiler cannot see
  through: what computed it is not dropped as unused, and the value that comes out is not known
  in advance.

## Codecs

**`std.codec`** (design 10 B10 E1–E2, E5–E6; M10 S1) is serialization as a pair: `Encode`
writes a value into an encoder, `Decode` reads one out of a decoder, `Codable` is both. A
format — `std.json`, `std.toml` — is an encoder and a decoder of its own; `std.codec` holds the
pair, the model a format implements, the layer a conformance writes with, the errors, the
conformances of the core types, and `Value`, the tree of the forms that any format could write.

1. **The pair.** `Encode { fn encode<E :: [Encoder]>(&e: E): void throws EncodeError; }`,
   `Decode { static fn decode<D :: [Decoder]>(&d: D): Self throws DecodeError; }`, `Codable ::
   [Encode, Decode]`. A conformance is generic over the format's type, and the format is passed by
   reference, as a hasher is ([§Hashing](#hashing)): the format keeps its state, and a `mut`
   method of the layer hands `&this` on.
2. **The model has ten forms**, and a format implements them as primitives: `encodeNull`,
   `encodeBool`, `encodeInt`, `encodeUint`, `encodeFloat`, `encodeString`, `encodeBytes`, and
   `beginSeq(n)`/`endSeq()`, `beginMap(n)`/`beginKey()`/`endMap()`, `beginStruct(name, n)`/
   `beginField(name)`/`endStruct()`, `beginVariant(enum, name, index, hasPayload)`/`endVariant()`;
   the decoder mirrors them, pull-based: `isNull()` peeks, `decodeInt()` and the others take,
   `beginSeq(): ?int` answers the count where the format knows it and `seqHasNext()` whether an
   element follows, `beginMap()`/`mapHasNext()` the same with a key and a value read in turn,
   `beginStruct(name, fields)` positions on a struct and `structField(name)` on a field — `false`
   where the data has none —, `endStruct(denyUnknown)` leaves it, `beginVariant(enum, variants)`
   answers the index of the variant the data holds and `variantHasPayload()` whether one follows.
   `path()` says where the format stands, for an error. The sequence of calls is the contract: a
   format that cannot hold a form throws.
3. **The layer** is what a conformance writes with, on the format itself: `e.field(name, v)`,
   `e.element(v)`, `e.entry(k, v)`, `e.encodeUnitVariant(…)`, `e.encodeVariant(…, payload)`;
   `d.field<T>(name)` reads a field the data must have — a missing one is `Missing` —,
   `d.optional<T>(name)` one it may lack (`null` then, as for a `null` in the data), `d.next<T>()`
   the next element or `null` at the end, `d.nextKey<K>()` and `d.value<V>()` a map's entry,
   `d.decodeNullable<T>()` a value that may be null.
4. **The core types conform.** The integers (a narrower one through `int`, refused as `Invalid`
   where it does not fit; a `uint` the same), `float` and `float32`, `bool`, `string`, `char` (a
   string of one character), `Instant` (its RFC 3339 text), `?T` (`null` or the value), `T[]`,
   `Slice<T>` (writes alone), `List<T>`, `Deque<T>`, `Set<T>` (a sequence, in the set's order),
   `Map<K, V>` (a map; the keys go to the format as values, which holds them or not), the tuples
   of two and three (a sequence of that length, `Missing` where shorter). A `uint8[]` is a
   sequence of numbers; **`Bytes { value }`** is the byte form the format holds its own way
   (design 10 E6: Base64 in JSON). A format reads a number as the form asked for: an `int`
   where a `uint` fits, a `float` from an integer.
5. **The errors.** `DecodeError { kind, path, detail }` with the kinds `Missing`,
   `TypeMismatch`, `Invalid`, `UnknownField`, `UnknownVariant`; its message is the kind, the
   detail and the path — `missing: field 'name' (at User)`, `type mismatch: expected an int, got a
   string (at Team.[].User)`. `EncodeError { path, detail, inner }`. A format never panics on
   its input ([design 10 B3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)).
   An unknown field passes unless the conformance ends its struct with `endStruct(true)`.
6. **`Value`** is the tree: `Null`, `Bool`, `Int`, `Uint`, `Float`, `String`, `Bytes`, `Seq`, `Map`
   (entries in the order written), `Struct(name, fields)`, `Variant(enum, name, index,
   payload)`; `Equatable` and `Debug`. `Value.of(v)` is the tree a value writes, `tree.read<T>()`
   the value a tree reads as, `Value.encoder()` and `tree.decoder()` the two formats to pass on.
   A `Value` is itself `Codable`: it writes its forms into any format, and reads the scalars and
   the two anonymous containers from one — a struct or a variant it cannot read without its name.
7. **`Codable` writes itself** (design 10 E3; [11 §4](11-metaprogramming.md) rule 10): a struct
   or a class conforming without the members gets `encode` and `decode` over its fields in
   declaration order — every field, whatever its word —, each under its wire name; a field the
   data lacks reads as `decodeAbsent` gives it (`null` for an optional, `Missing` else); an
   unknown field passes. An enum gets its variant: a unit one as the name, one payload field as
   the value, several as a sequence in their order; reading, an unknown name is
   `UnknownVariant`. The struct's name on the wire is `typeName`'s. An own `encode` or `decode`
   replaces the synthesized one ([05 §14](05-interfaces.md)).
8. **`@Codec` steers it** (E4): on a field, `name` writes it under that name and `skip` leaves it
   out — it reads as absent, so it is an optional or it is `Missing` —; on a struct or a class,
   `rename = .SnakeCase` or `.CamelCase` rewrites every field's name and `denyUnknown` refuses a
   field the data has and the type has not (`UnknownField`); on an enum, `tag = "kind"` writes a
   variant as a struct of the tag and the payload's fields, named by position (`"0"`, `"1"`),
   and reads it by the tag. `default` is not read in 5.0: a field marked so reads as absent.


## JSON

**`std.json`** (design 10 B10 E7; M10 S3) is RFC 8259, strictly: an encoder and a decoder of
[§Codecs](#codecs)' model, and `JsonValue`, the tree.

1. **The text of a value.** `json.encode<T :: [Encode]>(v, opts = JsonOptions { })` writes any
   `Encode` value as text; `json.encodeTo(v, &w, opts)` writes it into a `Writer`. A struct is an
   object of its wire names, a sequence an array, a map an object whose keys are strings — a
   number's digits where the key is a number; another key is an `EncodeError` —, bytes a Base64
   string, a unit variant its name, a variant with a payload `{"Name": payload}`; `null`,
   `true`/`false`, numbers as `int` or the shortest float text. `NaN` and the infinities have no
   JSON text (RFC 8259 §6): writing one is an `EncodeError`. The quote, the backslash and the
   control characters are escaped (`\n`, `\t`, `\r`, `\u00XX`), everything else stands as it is.
   `JsonOptions`: `pretty` writes newlines and `indent` spaces per level (default 2), `sortKeys`
   an object's keys in order.
2. **The value of a text.** `json.decode<T :: [Decode]>(text)` reads any `Decode` value; a text
   that is no JSON is `JsonError { line, column, detail }`, a value the type cannot read a
   `DecodeError` of [§Codecs](#codecs) rule 5 whose path names the structs, the members and the
   indices — `Team.members[0].User.id`. `json.decodeFrom<T>(&r)` reads a `Reader` to its end first. A struct
   reads from an object by its members' names (the rest ignored unless the type denies them), a
   sequence from an array, a map from an object (a key as the number it spells where the key
   type is one), a variant from its name or from an object of one member, bytes from Base64. A
   number with a fraction or an exponent read as an `int` is `Invalid`; one beyond `int` is a
   float in the tree and `Invalid` as an `int`; a number read as a `float` may be an integer.
3. **Strict.** One value, whitespace (space, tab, CR, LF) around it, nothing else: a trailing
   comma, a leading zero, `+`, `.5`, `1.`, an unknown escape, a lone surrogate, a control
   character unescaped, a text after the value are refused with the line and column. A member
   repeated keeps the last value. The document may nest 512 levels.
4. **`JsonValue`** is the tree: `Null`, `Bool`, `Int`, `Float`, `String`, `Array(List)`,
   `Object(Map)`; `Equatable` by content (an object's order aside), `Display` and `Debug` the
   compact text. `json.parse(text)` reads a text into it; `v["key"]` is a member or `null`,
   `v.at(i)` an element or `null`, `v.path("a.b[0]")` walks both, `asInt`/`asFloat` (an `Int`
   widened)/`asString`/`asBool`/`asArray`/`asObject`/`isNull` ask. A `JsonValue` is `Codable`
   itself: it writes its forms into any format and reads any value's forms from one; `v.read<T>()`
   reads a value out of the tree, `v.reader()` is the decoder to pass on.

## TOML

**`std.toml`** (design 10 B10 E8; M10 S4) is TOML 1.0: an encoder and a decoder of
[§Codecs](#codecs)' model, and `TomlValue`, the tree. The toolchain's manifest reader is not
it (15 §1): `std.toml` is for programs.

1. **The document of a value.** `toml.encode(v)` writes any `Encode` value whose form is a table
   — a struct, a map — as a document; another form is an `EncodeError`. A table's plain pairs
   come first, then its sub-tables under `[a.b]` headers (a table that holds sub-tables alone
   gets no header of its own), then its arrays of tables under `[[a.b]]`; a sequence is an
   array, a map a table whose keys are strings — a number's digits for a number; another key an
   `EncodeError` —, bytes an array of integers, a unit variant its name, a variant with a
   payload a table of one key (inline inside an array), a float `inf`, `-inf` or `nan` where it
   is no number. A key is bare where it is `[A-Za-z0-9_-]+`, quoted else; a string is a basic
   string with the quote, the backslash, the control characters escaped. A `null` field is left
   out of its table (TOML has no null); a `null` elsewhere is an `EncodeError`. `toml.encodeTo(v,
   &w)` writes into a `Writer`.
2. **The value of a document.** `toml.decode<T>(text)` reads any `Decode` value out of a document;
   a text that is no TOML is `TomlError { line, column, detail }`, a value the type cannot read a
   `DecodeError` of [§Codecs](#codecs) rule 5 whose path names the structs, the keys and the
   indices — `Config.servers[0].Server.port`. A struct reads from a table by its keys, a map from
   a table (a key as the number it spells where the key type is one), a sequence from an array,
   a variant from a string or a table of one key, bytes from an array of integers 0..255; a
   string reads from a string or from a date-time's text, so an `Instant` reads from an offset
   date-time; an absent key is absent (an optional reads `null`). A float read as an integer is
   `Invalid`. `toml.decodeFrom<T>(&r)` reads a `Reader` to its end first.
3. **TOML 1.0** (toml.io/en/v1.0.0): comments; bare, quoted and dotted keys; basic strings with
   their escapes (`\b \t \n \f \r \" \\ \uXXXX \UXXXXXXXX`), literal strings, both
   multi-line (the first newline dropped, a line-ending backslash dropping the whitespace up to
   the next character); integers decimal, `0x`, `0o`, `0b` with underscores and without a leading
   zero; floats with fraction, exponent, `inf`, `nan`; booleans; the four date-times (offset,
   local, date, time, with a fraction and `T` or a space); arrays over lines with a trailing
   comma; inline tables on one line; `[table]` and `[[array]]` headers. Refused with line and
   column: a key defined twice, a table defined twice, a header for a table a dotted key made, a
   dotted key into a table a header or an inline table made, a header where a value stands, a
   header for an array of tables and the reverse, a trailing comma in an inline table, a leading
   zero, a bare underscore, a signed prefixed integer, a date that is none.
4. **`TomlValue`** is the tree: `String`, `Int`, `Float`, `Bool`, `Datetime(TomlDatetime)`,
   `Array(List)`, `Table(TomlTable)`; **`TomlTable`** keeps its keys in the order written
   (`get`, `set`, `keys`, `pairs`, `length`); **`TomlDatetime`** is `Offset(DateTime)`,
   `Local(Date, Time)`, `LocalDate(Date)` or `LocalTime(Time)`, its text TOML's. `Equatable` by
   content, `Display` and `Debug` a table's document or a value's text. `toml.parse(text)` reads a
   document into a table; `v["key"]`, `v.at(i)`, `v.path("a.b[0]")`, `asString`/`asInt`/`asFloat`
   (an `Int` widened)/`asBool`/`asDatetime`/`asArray`/`asTable` ask. A `TomlValue` is `Codable`
   itself; `v.read<T>()` reads a value out of the tree, `v.reader()` is the decoder to pass on.

## Syntax

**`std.syntax`** (design 10 B13 M2; M9b S1) is the syntax tree as values: what a program can
write, as enums and structs a `comptime` function reads, builds and writes back. The macros of
[11 §5](11-metaprogramming.md) take and give these values (M9b S2–S5).

1. **The tree is enums and structs, `Box` where a node holds its own kind.** `Expr`, `Stmt`,
   `Decl`, `Type` and `Pattern` are enums, each form a variant, each node's last payload its
   `Span`; `Ident { name, span }` is a name, `Literal` a literal with its suffix (`Int(uint64,
   ?string)`, `Float`, `Str`, `Bytes`, `Char`, `Bool`, `Null`), `Block { stmts, span }` a block;
   a declaration's body is a struct — `FnDecl`, `StructDecl`, `ClassDecl`, `EnumDecl`, `InterfaceDecl`, `ExtendDecl`, `LetDecl`,
   `FieldDecl`, `AssocType`, `AliasDecl`, `ImportDecl` — as are `Param`, `GenericParam`,
   `Attribute`, `Arg`, `FieldInit`, `WithField`, `Arm`, `Catch`, `LambdaParam` and `Variant`;
   `Body` is an expression or a block, `Node` any of the five kinds, for a walk. A `Span` is a
   file as the diagnostics name it, a line and a column from 1 — `""` and `0` for a node that was
   built, not read (`Span.none()`). The enums are `@NonExhaustive` (10 B13 M3): a `match` over
   them outside the standard library writes a `_`, and a form the compiler has that the module
   has not — the rounds of a `comptime for` over fields ([§4](#4-type-information)), a local
   function, a node the parser could not read — is refused where it is read (`LYR-CT0005`). Every
   node is `Debug`; `Box<T>` is `Debug` where `T` is, and writes its value alone.
2. **`parseExpr(s)`, `parseStmts(s)` and `parseDecls(s)` read a text as the compiler reads it**:
   an expression; statements as a block body holds them, a last expression without its `;` the
   tail; declarations as a module holds them. A text that is no syntax is a panic of the
   evaluation (`LYR-CT0001`), with the parser's message and the place in the text.
3. **`toSource()` writes a node as the formatter writes it** — on an `Expr`, a `Stmt`, a `Block`
   (its statements, without the braces), a `Decl`, a `Type` and a `Pattern`. A tree read from a
   text comes back as the formatter would write that text, a built tree the same way: a literal
   from its value, so `1.5e3` is `1500.0` and `0x10u8` is `16u8`; no comments, since a tree holds
   none. The compiler's own pin: every program of its emitter tests goes tree, values, tree and
   gives the same text.
4. **`children()` gives the nodes directly inside one, in source order; `walk(f)` visits a node
   and every node below it, parents before children** — on a `Node`, and on each of the five
   kinds.
5. **`Ident.fresh(hint)` is a name no written name is**: `hint` and a number of its own, new at
   every call of an evaluation; `Ident.of(name)` is a name that stands nowhere. What a `quote`
   binds is fresh ([11 §5](11-metaprogramming.md); M9b S3).
6. **The tree lives at compile time.** The functions of `std.syntax` that read and write source
   run inside `comptime` only; a call the program would make at run time is refused
   (`LYR-CG0002`), as the world is refused at compile time ([11 §2](11-metaprogramming.md) rule 3).

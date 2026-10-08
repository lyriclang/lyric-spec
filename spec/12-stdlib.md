# The standard library contract

> **Partly written.** §1 was written with milestone **M3** of the Lyric 5 plan; the rest comes with
> **M8a–M10**, spec-first: each rule lands here with its conformance case before or with its
> implementation. Source of the decisions:
> [10 Standard library](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md).

## Scope

What of the standard library is language: the prelude, the core interfaces and their contracts (hash, order, clone), the answer forms and the panic rule, the naming law.

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
   formats of its own conforms to `Format { fn format(spec: StringView, &out: StringBuilder): void; }`
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
   `format(spec, &out)` for a `Format` type — the scalars conform —, through the padding of what
   `showTo` writes for another `Display` type, and through `debugTo` under `?`. The calls are
   `std.core`'s, bound by the compiler: a program need not import anything for an f-string.

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

### `std.math`, `clamp`, a `char`'s code point

What describes the world rather than a type is `std.math`'s (design 10 B5 Z2): `pi`, `e` and
`tau`, typed `float` — `math.pi as float32` for the narrow width. Beside them stand the functions
of two numbers:

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
- A **`Range<T>`** of an integer type is an `Iterator` of `T` and `DoubleEnded`: `next()` gives
  `start` and moves it on, `nextBack()` moves `end` back and gives it. A **`RangeInclusive<T>`**
  is both too and gives `end` as well; its last value leaves `start` past `end`, or `end` before
  `start` where that value is the type's `max` (its `min`, from the back) — no bound leaves the
  type. A range walked changes: `start` and `end` are `var`.
- A **`Coroutine<T>`** is an `Iterator` of `T` and `Closeable`, built in (design 10 B6 I7): its
  `Error` is what it throws, `never` where nothing, and it conforms to nothing else. A loop over
  one pulls it and closes it on its way out ([07 §2](07-statements.md) rule 7): left early, its
  stack unwinds and its defers run.
- The **adapters** are members of every iterator (design 10 B6 I3, I4), each giving a struct of
  its own — monomorphized, nothing allocated: `it.map(f)` gives a `MapIter<I, U>` (`Map` is the
  collection's), `it.filter(p)` a `FilterIter<I>`. Every iterator type's name ends in `Iter`
  (the review's A9g): the adapters (`TakeIter`, `ZipIter`, …), the string's (`CharsIter`,
  `SplitIter<P>`, `MatchesIter<P>`, `LinesIter`), the map's (`MapEntriesIter`, `MapKeysIter`,
  `MapValuesIter`), the
  slice's and the list's (`SliceIter`, `ListIter`). They pull lazily, one value at a time, and their
  `Error` is the inner iterator's. Of one source besides: `take(n)` and `skip(n)`;
  `takeWhile(p)`, which stays ended once `p` failed, and `skipWhile(p)`; `stepBy(n)`, the first
  value and then every `n`th, `n` below 1 a panic; `enumerate()`, each value with its position
  from 0, `(int, Item)`; `inspect(f)`, each value shown to `f` on its way through. Of two
  sources: `zip(other)`, each value beside the other's as long as both have one, the other an
  `Iterable`; `chain(other)`, the values and then the other's, an iterator of the same items.
  An adapter over a `Closeable` iterator is `Closeable` itself and passes `close()` on (the
  review's M8a-4), so a loop that leaves `gen().map(f)` early closes the generator; `zip` and
  `chain` close both of theirs, the first error winning.
  Their `Error` is the **join** of their sources' (design 05 E2 K7), `Join<A, B>` of `std.core`:
  one type where both are one, the other where one is `never`, the root `Error` where they
  differ — reduced once both are known; open, it covers each of its parts.
- The **terminators** walk an iterator — a copy of a struct one, a class one where it stands — and
  throw what it throws: `count()`; `fold(init, f)` and `reduce(f)`, the latter `null` without a
  value; `first()`, `last()` and `nth(n)`, `null` where there is no such value, a negative `n`
  included; `any(p)`, `all(p)` (`true` for none) and `none(p)`, stopping at the value that
  decides; `find(p)` and `position(p)`; `forEach(f)`; `toArray()`, in one pass.
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
  ones; `join(sep)` of a `Display`, the texts with `sep` between each two.
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
  of its own: its elements sort through `sortBy`.
- `arrayOf(n, f)` ([03 §8](03-types.md)) calls `f` once per index, in order; a negative `n`
  panics.

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

## Input and output

The core of `std.io` ([design 10 O1–O3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md); M8b S2). The
buffers and the text, the files, the console's streams and the network follow with M8b's later
slices.

1. **`IoError`** is the one error that input and output throw (O3), a struct: `kind:
   IoErrorKind`, `path: ?string`, `detail: string` and `inner: ?Error` — the field O3 calls
   `cause`, named so because `Error` asks for a method `cause()` and a type's members do not share
   a name (as `Exception`'s `inner`). Its `message()` is the kind in words, then the path and the
   detail where there are any: `not found: data.txt (opened to read)`. `IoErrorKind` names O3's
   kinds, and `Other { code }` a system's code no kind names. *(Informative.)* O3 marks the kinds
   `@NonExhaustive`, which comes with the compiler's attributes (M9a).
2. **`Reader`** has `read(into: Slice<uint8>): int`: it fills the slice from the front and answers
   how many bytes it put there — **0 only at the end**, and at once for an empty slice; fewer than
   the slice holds is no end. **`Writer`** has `write(from: Slice<uint8>): int`: it takes from the
   front and may take **fewer** bytes than it is handed. **`Seek`** has `seek(to: SeekFrom): int`,
   `SeekFrom.Start(n)`, `.End(n)` or `.Current(n)`, and answers the position counted from the
   start. All three throw `IoError`, and all three are `mut fn`s.
3. **The defaults** (O1), on every reader: `readExact(into)` fills the slice whole or throws
   `UnexpectedEof`; `readToEnd()` is everything to the end in a new array; `readToString()` the
   same as UTF-8 — bytes that are no UTF-8 throw `InvalidData`, the decoder's `Utf8Error` as the
   cause. On every writer: `writeAll(from)` writes until all of it is taken — a writer that takes
   no byte of a slice that has some throws `Other { code: 0 }` rather than being asked forever —
   and `writeString(s)` writes the text's UTF-8.
4. **`copy(r, w): int`** copies everything `r` holds into `w` and answers how many bytes. The two
   are used as the values handed in: a class is itself, and a reader that is a struct is read
   through a copy, its position unmoved for the caller.
5. **The streams over memory** (O2): `ByteReader.new(bytes)` reads a `Slice<uint8>` from the
   front and seeks — a position past the end reads nothing, one before the start panics;
   `ByteBuffer.new()` appends what is written and reads from the front what was written and not
   yet read, with `length()` and `toArray()` of what it holds. Both are classes, say
   `throws IoError` and throw nothing.

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
  the characters decoded, an `Iterator` of `char`.
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
- `trim()`, `trimStart()`, `trimEnd()`, the view without the white space (ASCII's: space, tab,
  the line breaks, vertical tab, form feed); `stripPrefix(p)` and `stripSuffix(p)`, the view of
  the rest, or `null` where `p` is not there.
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

**Repetition** (design 10 C7): `s * n` is the text `s` `n` times over — `""` for `n` of 0 — and a
negative `n` panics with `LYR-RT0007`, as `[x] * n` does; `n * s` is refused, the one order of
[03 §5.1](03-types.md).

## Collections

`std.collections` holds the containers (design 10 B7); none is safe across threads (C11). An
element is whatever a container's bounds admit, an object included, and every slot holds its own
(M8a S16).

- **`List<T>`** (C3), a class: its elements in order, at the front of a buffer that doubles when
  full. `new()`, `of(xs)` (a copy of the array), `withCapacity(n)` — room for `n` elements before
  it grows, taken at the first push, since a list holds no value it was not given (10 N3; M8a S14);
  every container's `withCapacity(n)` panics on a negative `n`. `xs[i]` and `xs[i] = v` through `IndexSet<int>`
  ([05 §12](05-interfaces.md) rule 9), outside `0 ≤ i < length()` a panic (`LYR-RT0003`); `get(i)`,
  `null` there. `push(v)`, `pushAll(xs)`, `pop()` (`null` for none), `insert(i, v)`, `removeAt(i)`,
  `removeWhere(p)` (how many went), `clear()` (the room stays), `truncate(n)`, `swap(i, j)`,
  `toArray()` (a copy); of an `Equatable` element `contains(x)`, `remove(x)` (whether there was one)
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
  copies fresh for every key — `FixedHasher.new()` hashes alike in every run. `insert(k, v)`
  answers the value it replaces or `null`; `get(k)` the value or `null`; `containsKey(k)`;
  `remove(k)` the value taken out or `null`; `length()`, `isEmpty()`, `clear()`; `getOr(k, d)`;
  `getOrInsert(k, make)`, `make()`'s value inserted where `k` has none; `update(k, f)`, whether
  there was one to replace; `retain(p)`, how many went. A map is `Iterable` over its entries,
  `(K, V)`, and `keys()` and `values()` walk the same order — none the map's own (I8); a change of
  the map while it is walked panics at the next pull (I9). *(Informative.)*
  A Swiss table: groups of eight slots under a control word, the hash's seven low bits compared
  a group at a time, at most seven of eight slots filled.
- **`Set<T :: [Hashable], H :: [Hasher] = DefaultHasher>`** (C5), a class over a map's keys:
  `new()`, `withCapacity(n)`, `withHasher(seed)`, `insert(v)` (whether it was not there), `contains(v)`, `remove(v)`
  (whether it was there), `length()`, `isEmpty()`, `clear()`; `Iterable` over its values, in no
  order of its own.
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
inclusive one with `x <= end`.

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

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

The core of `std.io`, its buffers and its text ([design 10 O1–O3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md);
M8b S2, S3 and S10a). The files, the console's streams and the network follow with M8b's later
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
   §3.5).
3. **`Hex`** encodes two digits a byte, in small letters, and decodes either case; an odd count
   of digits fails at the end.
4. **`Utf16`** encodes a text as code units, `uint16[]`, a codepoint past `U+FFFF` as a surrogate
   pair; `decode` takes units, and half of a pair without its other half fails at its unit.
5. **The integers of bytes**: `T.fromBytesLE(s)` and `T.fromBytesBE(s)` for every integer type
   `T` read exactly its width — another length panics (`LYR-RT0008`) —, the first byte the lowest
   or the highest. `Slice<uint8>` has `getUint16LE(at)`, `getUint16BE`, the same for `Uint32`,
   `Uint64`, `Int16`, `Int32` and `Int64`: the width at the byte offset `at`. They are members of
   the module's blocks, there where `std.encoding` is imported. *(Informative.)* A string's bytes
   are reached through `std.io`'s `ByteBuffer` until `toBytes` (M8c).

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
   (`linux`, `macos`, `windows`, `x86_64`, `aarch64`); `os.homeDir()`, the user's home or `null`;
   `os.tempDir()`, the system's directory for temporary files, absolute (`fs.tempDir()` makes a new
   one in it); `os.hostname()`; `os.cpuCount()`, one at least; `os.pid()`.

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

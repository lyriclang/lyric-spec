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
| `fromFloat(value: float): string` | the shortest text that reads back as the value, `1.0` for an integral one; `inf`, `-inf`, `nan` ([03 §1.7](03-types.md)) |
| `fromBool(value: bool): string` | `true` or `false` |
| `fromChar(value: char): string` | the character, UTF-8 |

A narrower integer or a `float32` in a hole widens to the converter's parameter type first
([03 §1.3](03-types.md)): `f"{x}"` with `x: int8` is `fromInt(x)`, with `x: float32` it is
`fromFloat(x)`.

## 2. The format language

A hole may name a format after a colon — `{x:>8}`, `{n:#x}`, `{f:.2f}`, `{v:?}` — in one
language, without locale, checked where it is written
([08 Y7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md),
[10 S7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)).

1. **Form**: `[[fill]align][sign][#][0][width][grouping][.precision][type]`. `align` is `<`
   (left), `>` (right) or `^` (centred, the odd fill after), the fill any character before it, a
   space without; `sign` is `+` (a sign on every number) or `-` (on a negative one only, as
   without); `#` writes a radix's prefix, `0b`, `0o`, `0x`, `0X`; `0` pads with zeros between the
   sign and prefix and the digits; `width` is the least number of **characters**, not bytes;
   `grouping` is `,` or `_` between each three decimal digits, `_` between each four of another
   radix; `precision` is the digits after a float's point or the most characters of a string;
   `type` is `b`, `o`, `x`, `X` (an integer's radix), `e`, `E`, `f`, `%` (a float's form) or `?`
   (`Debug`).
2. **What applies**: an integer takes all but a precision and a float's type; a float all but `#`
   and an integer's type; a `string` fill, alignment, width and precision; a `char`, a `bool`
   and a `Display` type fill, alignment and width, on the text `show()` gives; `?` takes fill,
   alignment and width, on the text `debug()` gives, for every type. A spec that is no format,
   or a part that does not apply to the hole's type, is refused (`LYR-SEM0164`). A type with
   formats of its own conforms to `Format { fn format(spec: string, &out: StringBuilder): void; }`
   and reads the spec as written, unchecked — `?` stays `Debug`.
3. **Defaults**: a number right-aligned, the rest left-aligned. A float without a type or a
   precision is its shortest text ([03 §1.7](03-types.md)); with a precision and no type it is
   fixed, `{2.5:.3}` is `2.500`; `e`, `E`, `f` and `%` take six digits without a precision; `%`
   writes the value a hundredfold, fixed, with `%` after; an exponent carries its sign and two
   digits at least, `{1234.5:e}` is `1.234500e+03`. The fixed and the exponent forms round to
   nearest on the value's exact binary digits: `{2.675:.2f}` is `2.67`. `nan`, `inf` and `-inf`
   keep their words, `NAN` and `INF` under `E`.
4. **Binding**: `{x:spec}` compiles to `std.core`'s `formatted(x, "spec")` for a `Format` type —
   the scalars conform —, to `padded(x, "spec")` for another `Display` type, and to
   `debugged(x, "spec")` under `?`; a program need not import them, as with the converters
   (§1).

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
`min` or `max` instead. Each integer type has them as its own statics; through a type
parameter they are not reached.

`x.clamp(lo, hi)` is a default of `Ordered`: `lo` below it, `hi` above it, the value itself
between; `lo` above `hi` is the program's error and panics, and a value unordered with the bounds
comes back as it is. A `char`'s code point is `c.toUint32()`, and `char.fromUint32(n): ?char` is
`null` for a surrogate or beyond `0x10FFFF` (Z8), where `n as char` panics
([03 §1.4](03-types.md)).

## Iteration

The protocol `for` walks (design 10 B6) is `std.core`'s; the prelude passes `Iterator` and
`Iterable` on.

- **`Iterator { type Item; type Error :: [Error] = never; mut fn next(): ?Self.Item throws
  Self.Error; fn sizeHint(): (int, ?int) }`**: `next()` gives the next value, and `null` at the
  end. A walk that can fail answers its `Error`, which `next()` throws; by default it throws
  nothing ([07 §2](07-statements.md) rule 6). `sizeHint()` says how many values are left, at
  least and at most where that is known; the default says `(0, null)`.
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
  its own — monomorphized, nothing allocated: `it.map(f)` gives a `Mapped<I, U>` (`Map` is the
  collection's), `it.filter(p)` a `Filter<I>`. They pull lazily, one value at a time, and their
  `Error` is the inner iterator's. Of one source besides: `take(n)` and `skip(n)`;
  `takeWhile(p)`, which stays ended once `p` failed, and `skipWhile(p)`; `stepBy(n)`, the first
  value and then every `n`th, `n` below 1 a panic; `enumerate()`, each value with its position
  from 0, `(int, Item)`; `inspect(f)`, each value shown to `f` on its way through. Of two
  sources: `zip(other)`, each value beside the other's as long as both have one, the other an
  `Iterable`; `chain(other)`, the values and then the other's, an iterator of the same items.
  Their `Error` is the **join** of their sources' (design 05 E2 K7), `Join<A, B>` of `std.core`:
  one type where both are one, the other where one is `never`, the root `Error` where they
  differ — reduced once both are known; open, it covers each of its parts.
- The **terminators** walk an iterator — a copy of a struct one, a class one where it stands — and
  throw what it throws: `count()`; `fold(init, f)` and `reduce(f)`, the latter `null` without a
  value; `first()`, `last()` and `nth(n)`, `null` where there is no such value, a negative `n`
  included; `any(p)`, `all(p)` (`true` for none) and `none(p)`, stopping at the value that
  decides; `find(p)` and `position(p)`; `forEach(f)`; `toArray()`.
- The terminators **of an element kind** stand on the iterators whose `Item` admits them
  ([05 §13](05-interfaces.md) rule 2): `sum()` and `product()` of a `Num`, zero and one where there
  is no value; `min()` and `max()` of an `Ordered`, `null` without a value, the first of equal
  ones; `join(sep)` of a `Display`, the texts with `sep` between each two.
- **`SliceIter<T>`** is the iterator of an array or a view, from both ends, through a view of its
  elements — nothing is copied, and a write to a later element is seen; its `sizeHint()` is
  exact. `T[]` and `Slice<T>` are `Iterable` through it: `xs.iter()`.

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

## Arrays and views

The members of an array and of a view are `std.core`'s (design 10 C2), written once on
`Slice<T>` and reached on an array through a view of all of it ([03 §5.2](03-types.md) rule 4):
a write through one reaches the array. `length()` and the index are the primitives
([03 §5.1](03-types.md)).

- `isEmpty()`; `get(i)`, `null` outside `0 ≤ i < length()`; `first()` and `last()`, `null`
  where there is no element.
- `swap(i, j)`, an index outside panicking as `[i]` does; `reverse()` in place; `reversed()`, a
  new array.
- Of an `Equatable` element: `contains(x)`, through which `T[]` and `Slice<T>` are
  `Contains<T>` (10 C12), and `indexOf(x)`, the first index or `null`.
- Of a `Clone` element: `fill(v)`, every element a clone of `v` — no object shared into several
  slots, as `[x] * n` shares none ([03 §5.1](03-types.md)).
- `partitionPoint(p)`: the first index whose element fails `p`, for elements `p` partitions —
  every one it holds for before every one it does not; a binary search. Of a `TotalOrder`
  element, `binarySearch(x)`: the index of an element equal to `x` in sorted elements, any of
  several equal ones, or `null`.
- Of a `Display` element: `join(sep)`, the elements' texts with `sep` between each two.
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

## Strings

A `string` is immutable UTF-8 (design 10 S1). Its members are `std.core`'s:

- `length()`, the bytes, `O(1)`; `isEmpty()`; `charCount()`, the characters, `O(n)`; `chars()`,
  the characters decoded, an `Iterator` of `char`.
- `string` is `Ordered` and `TotalOrder` byte by byte, which is the order of the code points.
- The search over a string pattern: `contains(p)`, `startsWith(p)`, `endsWith(p)`; `find(p)` and
  `rfind(p)`, the byte index of the first and the last `p` or `null` — an empty `p` stands at 0
  and at the length; `count(p)`, the occurrences none overlapping another, an empty `p` between
  every two characters and at both ends.
- `split(sep)`, the parts between the separators in order, empty ones kept — an empty separator
  panics; `splitOnce(sep)`, the parts before and after the first, or `null`; `lines()`, split at
  `\n` with a `\r` before it taken off and no empty line after a last `\n`.
- `trim()`, `trimStart()`, `trimEnd()`, without the white space (ASCII's: space, tab, the line
  breaks, vertical tab, form feed); `stripPrefix(p)` and `stripSuffix(p)`, the rest, or `null`
  where `p` is not there.
- `replace(p, with)`, every `p` replaced, none overlapping — an empty `p` panics;
  `padStart(width, fill = ' ')` and `padEnd(width, fill = ' ')`, the width in characters.
- **`StringBuilder`** (`std.string`, a class): `appendStr(s)`, `appendChar(c)`, `append(v)` of a
  `Display`, `length()` in bytes, `clear()`, `toString()` — in a buffer that doubles, no chain of
  concatenations.

## Collections

`std.collections` holds the containers (design 10 B7); none is safe across threads (C11).

- **`List<T>`** (C3), a class: its elements in order, at the front of a buffer that doubles when
  full. `new()`, `of(xs)` (a copy of the array). `xs[i]` and `xs[i] = v` through `IndexSet<int>`
  ([05 §12](05-interfaces.md) rule 9), outside `0 ≤ i < length()` a panic (`LYR-RT0003`); `get(i)`,
  `null` there. `push(v)`, `pushAll(xs)`, `pop()` (`null` for none), `insert(i, v)`, `removeAt(i)`,
  `removeWhere(p)` (how many went), `clear()` (the room stays), `truncate(n)`, `swap(i, j)`,
  `toArray()` (a copy); of an `Equatable` element `contains(x)`, `remove(x)` (whether there was one)
  and `dedup()` (runs of equal ones kept once). `asSlice()` is a view of the buffer, so the members
  of arrays and views reach the list — a sort writes it; a push past the room moves the list to a
  new buffer, and an older view keeps the older one. A list is `Iterable` front to back
  ([10 I9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)): a change of
  its length while it is walked panics at the next pull.
- **`Map<K :: [Hashable], V, H :: [Hasher] = DefaultHasher>`** (C4), a class: what it holds, in
  no order of its own, each key once. `Map<K, V>.new()` hashes with the process's key, so its
  order differs from run to run; `withHasher(seed)` takes a hasher, which is a value the map
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
  `new()`, `withHasher(seed)`, `insert(v)` (whether it was not there), `contains(v)`, `remove(v)`
  (whether it was there), `length()`, `isEmpty()`, `clear()`; `Iterable` over its values, in no
  order of its own.
- Every iterator's **`toList()`** collects what it gives into a `List` (I4).

A value that hashes is **`Hashable`**, `fn hash<H :: [Hasher]>(&h: H): void`, a child of
`Equatable`: it writes its parts into the hasher, and equal values write the same — nothing checks
it. An integer writes its word (`writeInt`, `writeUint` for the unsigned), a `bool` a byte, a
`char` its code point as a word, a `string` its bytes and then 255, which no UTF-8 text holds. A
`float` is none (10 SL-26); an array, a view, a `List`, a `Map` and a `Set` are none either (10
C8): their slots can be written. A type's own hash is synthesized ([05 §14](05-interfaces.md)).

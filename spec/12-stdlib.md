# 12. Standard library contract

**Base.** Lyric 5.0 [§12](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/12-stdlib.md) applies, with the deviations below.

**Status.** The core written (S2), the standard library's modules (S7a), its iterators (S7c6),
collections (S7d), the strings' members, reading values from text, builders of text, the
format language and `std.fmt` (S7e), the number tower (S7f1), `std.math` (S7f2); the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

## Written (S2, the core)

1. **The prelude's output** ([07 I8](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)): `print(x)` and
   `println(x)` write one value of a core type — `int`, `float`, `bool`, `char`, `string` — as
   text, `println` with a line end; `println()` writes the line end alone. They need no import.
   Other values follow with `Display`.

## Written (S7, the standard library's core)

2. **Modules of the standard library** ([12 Src](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)). `import std.<m>` names a
   module of the standard library, which comes with the toolchain: a path that begins with `std`
   is never a file of the program nor a package (Lyric 5 §4), and one the library does not have is
   `LYS-RES0003`. Its modules are compiled with the program; what one of them keeps `internal`
   stays its own, and only they reach the VM's natives. Its modules and the rights they ask for
   ([17](17-host.md) rule 1) so far: `std.fs` — `exists(path): bool`; `std.os` —
   `env(name): ?string`; `std.fmt` — `format(template, args: Display...)` (rule 12), no right;
   `std.math` (rule 14), no right. The rest come with the milestones that build them.
3. **The adapters of every iterator** (Lyric 5 12 §Iteration; S7c6b1). `std.iter` holds them,
   members of blanket blocks over `I :: [Iterator]` that reach every module without an import —
   the loader adds the module to a program that names one of them: `it.map(f)`, `filter(p)`,
   `take(n)`, `skip(n)`, `takeWhile(p)` — ended for good once `p` failed —, `skipWhile(p)`,
   `stepBy(n)` — the first value and then every `n`th, `n` below 1 a panic (`LYS-RT0008`) —,
   `enumerate()`, each value with its position from 0, `inspect(f)`, `zip(other)` with an
   `Iterable`, `chain(other)` of the same items, `mapNotNull(f)`, `flatMap(f)` and, over an
   iterator of `Iterable`s, `flatten()`, `dedupBy(same)` and, of an `Equatable` item, `dedup()`,
   `scan(init, f)` — `init` first —, `peekable()` with `peek()`, and `rev()` of a `DoubleEnded`
   iterator ([07](07-statements.md) rule 8), and `cycle()` of a `Clone` iterator — its values over
   and over, from a clone each time, none where it has none: a list's walk and a range's clone
   ([05](05-interfaces.md) rule 19). Each gives a class of its own under Lyric 5's name
   (`MapIter`, `FilterIter`, …), lazy: a pull takes from the iterator below what it needs. A
   program imports a class where it writes the type, `import std.iter { MapIter }` (`LYS-SEM0011`
   otherwise). An adapter over a `Closeable` iterator is `Closeable` and passes `close()` on —
   `rev` excepted —, so a loop that leaves `gen().map(f)` early closes the coroutine; `zip` and
   `chain` close both of theirs where both are; `cycle` passes no `close()` on, as Lyric 5's.
4. **The terminators of every iterator** (Lyric 5 12 §Iteration; S7c6b2), `std.iter`'s too: each
   walks the iterator — a class one where it stands, so what a terminator leaves stays left — to
   an answer. `count()`; `fold(init, f)` and `reduce(f)`, the latter `null` without a value;
   `first()`, `last()` and `nth(n)`, `null` where there is no such value, a negative `n`
   included; `any(p)`, `all(p)` (`true` for none) and `none(p)`, stopping at the value that
   decides; `find(p)` and `position(p)`; `forEach(f)`, a function as any — there is no `inline
   fn` ([03](03-types.md) rule 11), so a `return` in its lambda leaves the lambda; `toArray()` and
   `toList()`, the values in a list in one pass, a `List<T>` being a `T[]`; `minBy(key)` and
   `maxBy(key)` over a `TotalOrder` key, the first of equal ones, `null` without a value;
   `partition(p)`, two lists in order; `chunks(n)`, the last shorter, and `windows(n)`, none where
   there are fewer, `n` below 1 a panic (`LYS-RT0008`); `join(sep)`, each value as `{x}` writes
   it — every value prints ([03 Eq](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)) — with `sep` between each two. Of an element kind:
   `sum()` and `product()` of a `Num`'s values (rule 13), its `zero` and its `one` where there is
   none; `average()` of `int` or of `float` values, a `float` summed as one, `null` where there is
   none; `min()` and
   `max()` of an `Ordered` value, the first of equal ones, `null` without a value. Where the
   items are of no such kind the terminator is not there (`LYS-SEM0012`). `sorted()` of a
   `TotalOrder` item and `sortedBy(cmp)` put the values in a list, stably sorted ([03](03-types.md)
   rule 16; S7c6c2); `groupBy`, `toMap` and `toSet` are std.collections' (rule 6).
5. **Maps** (Lyric 5 12 §Collections; Script [12 Src](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md); S7d2). `std.collections`
   holds `class Map<K :: [Hashable], V>`, whose names are the prelude's: the loader adds the
   module to a program that names `Map` or writes a map literal ([03](03-types.md) rule 14).
   `import std.collections { Map }`, as Lyric 5's own modules write it, names the prelude's own,
   `{ Map as Dict }` under a name of its own — its types and `List`; a name it does not declare
   is `LYS-RES0004`, the module named as a whole `LYS-RES0003` (S7d4). A
   map holds each key once, in the order the keys came — a key taken out and put back comes last.
   `m[k]` is the value under `k` or `null`, `m[k] = v` puts `v` there, `m[k] = null` takes `k`
   out (`IndexSet<K>` of `?V`), `k in m` asks the keys. Its members are Lyric 5's:
   `Map.new()`, `Map.withCapacity(n)` — a negative `n` a panic —, `Map.from(pairs)`, a later
   value of a key replacing the earlier one; `insert(k, v)` and `remove(k)`, the value replaced
   or taken, `null` where there was none; `get(k)`, `containsKey(k)`, `getOr(k, d)`,
   `getOrInsert(k, make)`, `update(k, f)` — whether there was a value —, `retain(p)` — how
   many went —, `length()`, `isEmpty()`, `clear()`. A map is an `Iterable` of its entries,
   `(K, V)`, walked in their order, as `entries()`, `keys()` and `values()` are; a key put in or
   taken out, or the map cleared, while an iterator walks makes its next pull panic
   (`LYS-RT0016`) — writing the value of a key that is there is no change. Pairs collect into a
   map (`FromIterator<(K, V)>`). Two maps are equal where they hold the same keys under equal
   values, in any order, where `V` is an `Equatable`; a map is a `Clone` where `K` and `V` are, a
   map of the clones in the same order. Its Debug form is `{"a": 1, "b": 2}`, `{}` empty. A key
   that is no `Hashable` — a `float`, a list — is refused (`LYS-SEM0028`).
6. **Sets** (Lyric 5 12 §Collections; S7d3). `std.collections` holds `class Set<T :: [Hashable]>`,
   a map's keys, in the order the values came; a program that names `Set`, `Deque` or `Heap`
   gets the module as one that names `Map` does. `Set.new()`, `Set.of(xs)`, `Set.withCapacity(n)` — a negative `n` a
   panic —; `insert(v)`, whether `v` was not there, `remove(v)`, whether it was, `contains(v)` and
   `x in s`, `length()`, `isEmpty()`, `clear()`. A list literal where a set is taken builds one
   (`FromArrayLiteral<T>`), `let s: Set<int> = [1, 2, 2]`, so do `collect()` and `toSet()`. Its
   operations are methods that make a new set, this one's values first, or answer a question:
   `union`, `intersect`, `difference`, `symmetricDifference`, `isSubset` — the empty set is a
   subset of every set —, `isSuperset`, `isDisjoint`. A set is an `Iterable` of its values in
   their order; a value put in or taken out while it is walked makes the next pull panic,
   `LYS-RT0016` naming the set. Two sets are equal where they hold the same values, in any
   order; a set is a `Clone` where `T` is; its Debug form is `{1, 2}`; a value that is no
   `Hashable` — a `float`, a set — is refused (`LYS-SEM0028`). Over every iterator, std.collections
   gathers as Lyric 5's does, a program that names one of them getting the module: `groupBy(key)`,
   a map from each key, in the order the keys came, to its values in their order; `toMap()` of an
   iterator of pairs, a later value of a key replacing the earlier one; `toSet()` of hashable
   values. Where the items are of no such kind the member is not there (`LYS-SEM0012`).
7. **Deques and heaps** (Lyric 5 12 §Collections; S7d4). `class Deque<T>` takes and gives values
   at either end — `pushBack`, `pushFront`, `popFront`, `popBack`, `peekFront`, `peekBack`, the
   last four `null` where it is empty —, `Deque.new()`, `Deque.withCapacity(n)`, `length()`,
   `isEmpty()`; `d[i]` is the value `i` places from the front (`Index<int>`, never written,
   `LYS-SEM0019`), a panic outside `0 ≤ i < length()` (`LYS-RT0003`, a list's text). It is an
   `Iterable` front to back — a push or a pop while it is walked makes the next pull panic,
   `LYS-RT0016` naming the deque —, equal where its values are, in order, where `T` is an
   `Equatable`, a `Clone` where `T` is; its Debug form is a list's, `[1, 2]`. `class Heap<T ::
   [TotalOrder]>` is a binary min-heap: `push(v)`, `peek()` and `pop()` the least value or `null`,
   `Heap.new()`, `Heap.withCapacity(n)`, `Heap.of(xs)` built in linear time, `length()`,
   `isEmpty()`; its Debug form is its values as it holds them, a list's; a `Clone` where `T` is.
   A list literal builds either where it is taken, `let d: Deque<int> = [1, 2]`, so does
   `collect()`.
8. **Strings and characters** (Lyric 5 12 §Strings, §Characters; Script [03 Str](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md); S7e1).
   A string is UTF-8: `length()` counts its bytes, `charCount()` its characters, `isEmpty()`.
   `s[i]` is the character that begins at byte `i` — outside the bytes, or at a byte that
   continues a character, a panic (`LYS-RT0003`); `^n` is no index of a string, a bound of a range
   alone (`LYS-SEM0114`), and a character is never written through the index (`LYS-SEM0019`).
   `s[a..b]`, in a range's every form, `^n` among its bounds, is a **new string** of those bytes
   (03 Str), a bound outside them or inside a character a panic (`LYS-RT0003`). `chars()` gives
   the characters from either end, `charIndices()` each with the byte it begins at;
   `string.fromChars(it)` joins an iterator's characters. A **pattern** is a string, a
   character or a test of characters, `fn(char) -> bool` (S7e2), `interface Pattern` of the
   prelude with Lyric 5's members `matchAt`,
   `matchBefore` and `nextIn` over a string's bytes: `contains(p)`, `startsWith(p)`,
   `endsWith(p)`; `find(p)` and `rfind(p)`, the byte of the first and the last match or `null`,
   an empty pattern at 0 and at the length; `count(p)`, none overlapping another; `c in s` for a
   character; `trimMatches(p)`, `trimStartMatches(p)`, `trimEndMatches(p)`, again and again;
   `stripPrefix(p)` and `stripSuffix(p)`, the rest or `null`; `replace(p, with)` and
   `replaceN(p, with, n)` — a pattern that matches the empty text panics. `split(sep)` gives the
   parts in order, empty ones kept, `splitN(sep, n)` at most `n`, the last the rest,
   `splitOnce(sep)` the parts before and after the first or `null`, `matches(p)` the matches,
   `lines()` the lines — split at `\n`, a `\r` before it taken off, no empty line after a last
   `\n` —, each a new string; a separator that matches the empty text panics (S7e2). `trim()`,
   `trimStart()`, `trimEnd()` take off the white space — the property White_Space —, `isBlank()`
   holds for nothing but it; `toUpper()` and `toLower()` map each character simply, one for one,
   no locale; `padStart(width, fill = ' ')` and `padEnd(…)` count characters; `s * n` is the text
   `n` times, `n * s` refused, a negative `n` a panic (`LYS-RT0007`). A character has its
   `category()` (`UnicodeCategory`), `isAlpha()`, `isDigit()`, `isAlphanumeric()`,
   `isWhitespace()`, `isUpper()`, `isLower()`, `isControl()` of any script, `toUpper()`,
   `toLower()`, the ASCII tests, `toDigit(radix)` and `char.fromDigit(n, radix)` — `null` where
   there is no such digit, a radix outside 2–36 a panic. A scalar's or the string's static is
   called through its name, `char.fromDigit(…)`, `string.fromChars(…)`.
9. **Values from text** (Lyric 5 12 §Parsing; S7e2). `interface Parse { static fn parse(s:
   string): Self }`: `bool.parse(s)` takes `true` and `false` exactly, `int.parse(s)` and
   `int.parse(s, radix)` an optional sign, ASCII digits of the base and `_` between two of them,
   `float.parse(s)` a float's form — an optional sign, then `inf`, `nan`, or digits with an
   optional fraction and exponent —, read to the nearest float; `s.parse<T>()` is `T.parse(s)`,
   `T` from where the result goes, `let n: int = s.parse()`. A text that is none throws a
   **`ParseError`** — its `kind` `Empty`, `Invalid` for a character outside the form however many
   digits run before it, `Overflow` for a well-formed number beyond the type's range; `detail` and
   `offset` where the parser says more; `message()` Lyric 5's words. A radix outside 2–36 panics.
10. **Builders of text** (Lyric 5 12 §Strings; S7e3). `class StringBuilder` builds a text a part
   at a time in one buffer that grows, no chain of concatenations: `StringBuilder.new()`,
   `appendStr(s)`, `appendChar(c)`, `append(v)` of any `Display` through its `showTo`, `length()`
   in bytes, `clear()`, `toString()`. `Display` and `Debug` write into one
   ([05](05-interfaces.md) rule 21). The VM holds its text, so its Debug
   form is its type, `<StringBuilder>`, as a task's is ([10](10-concurrency.md) rule 19).
11. **The format language** (Lyric 5 12 §2 rules 1–3; S7e4b). A hole names a format after a
   colon, `{x:>8}`, `{n:#x}`, `{f:.2f}`, `{v:?}`, in Lyric 5's language,
   `[[fill]align][sign][#][0][width][grouping][.precision][type]`, checked where it is written: an
   `int` takes all but a precision and a float's type, a `float` all but `#` and an integer's type,
   a `string` fill, alignment, width and a precision, a `char`, a `bool` and any other value fill,
   alignment and width on its text — a `Display`'s `show()`, else its Debug form —, `?` the same on
   its Debug form; a spec that is no format or holds a part the type does not take is refused
   (`LYS-SEM0164`). The text is Lyric 5's own formatting, its defaults and its rounding — half away
   from zero on the value's exact binary digits. A type with formats of its own conforms to
   `interface Format { fn format(spec: string, out: StringBuilder) }` and reads the spec as written,
   unchecked, `?` staying its Debug form; the scalars and the string conform, and a spec they read
   at run time is checked as the compiler checks one, its fault a panic (`LYS-RT0008`).
12. **Templates read at run time** (Lyric 5 12 §2 rule 5; S7e4c). `std.fmt.format(template: string,
   args: Display...): string` reads its template when it runs, in the language of rule 11: `{}`
   takes the next value and `{i}` the i-th from 0 — the two mix, `{}` counting only itself —, either
   with `:spec`, `?` for the value's Debug text; `{{` and `}}` write a brace, and a value no hole
   names is left out. A value is passed as a `Display`; one that reads specs itself, a `Format` —
   the scalars too —, takes its spec, any other has its text padded. What the compiler refuses in
   an f-string panics here (`LYS-RT0008`), in Lyric 5's words: a brace left open or closed without
   being opened, a value named that is not given, a spec that is no format or holds a part the
   value's type does not take. Every value has a Debug text, so `?` never panics for want of one.
13. **The number tower** (Lyric 5 12 §Numbers; S7f1b). The prelude declares `Num` — `Equatable`,
   `Ordered`, `Add` … `Rem` each `<Out = Self>` ([05](05-interfaces.md) rule 22), `Display`,
   `Debug`, `Parse`, `Default`; `static let zero, one: Self`, `isZero()` —, `Signed` (`Num`,
   `Neg<Out = Self>`), `Integer` (`Num`, `TotalOrder`, `Hashable`, the bit operators; `min`,
   `max`, `bitWidth`, `isSigned`) and `Float` (`Signed`; `epsilon`, `infinity`, `nan`, `min`,
   `max`, `leastPositive`, `fromBits(b)`). `int` is a `Num`, a `Signed` and the `Integer`, `float`
   a `Num`, a `Signed` and the `Float`. A constant stands at the scalar's name, `int.max`,
   `float.epsilon` (`LYS-SEM0012` for one it has not). An integer's `checkedAdd` … `checkedRem` give
   `null` where the result does not fit — a zero divisor, `min / -1`; a remainder by `-1` is `0` —,
   `saturatingAdd`, `…Sub`, `…Mul` hold at `min` or `max` by the sign the result would have,
   `wrappingAdd` … `wrappingRem` reduce as `+%`, `-%`, `*%` do, `min / -1` wrapping to `min`;
   `pow(n)` multiplies by squaring, an overflow panicking as `*` does; `leadingZeros()`,
   `trailingZeros()`, `popCount()` count bits at the width, `bitWidth` for zero, and
   `rotateLeft(n)`, `rotateRight(n)` rotate modulo it, a negative `n` the other way. A float's
   `isNan()`, `isInfinite()`, `isFinite()` tell the value, `toBits()` gives its 64 bits.
   `x.clamp(lo, hi)` is a default of `Ordered`: `lo` below it, `hi` above it, the value itself
   between, a value unordered with the bounds as it is; `lo` above `hi` panics (`LYS-RT0008`).
14. **What one computes with numbers** (Lyric 5 12 §`std.math`; S7f2). `std.math` holds free
   functions, generic over the tower, and the constants `pi`, `e` and `tau`, typed `float`. Over
   `Float`: `floor(x)`, `ceil(x)`, `round(x)` — a half away from zero —, `trunc(x)`; `sqrt(x)`,
   `cbrt(x)`, `exp(x)`, `ln(x)`, `log2(x)`, `log10(x)`; `sin`, `cos`, `tan`, `asin`, `acos`,
   `atan`, `sinh`, `cosh`, `tanh`, in radians; `atan2(y, x)`, the angle of the point (x, y), -π to
   π; `hypot(x, y)`; `pow(x, e)`. They are Lyric 5's own functions: a script computes the bits a
   compiled program does, on every platform. `lerp(a, b, t)` is `a` at `t = 0` and `b` at `t = 1`
   exactly. Over `Signed`: `abs(x)`, `0.0` for `-0.0`, and `signum(x)`, `-1`, `0` or `1` in the
   type, a float's NaN staying NaN. Over `Ordered`: `min(a, b)` and `max(a, b)`, `a` where the two
   are equal or unordered. Over `Integer`: `gcd(a, b)` and `lcm(a, b)`, never negative, `gcd(0, 0)`
   is `0`; a result beyond the type overflows and panics (`LYS-RT0002`), as `abs(int.min)` does.
   A program's own `Float` reaches what is written over the tower — `lerp`, `abs`, `signum`,
   `min`, `max` —; an elementary function computes in `float`, and such a value at one is
   `LYS-SEM0028`.
15. **Conversions** (Lyric 5 12 §Conversions; S7f3). The prelude declares `interface From<T> { static
   fn from(v: T): Self }`, a conversion into a type, which the type writes, `Cm.from(m)`, and
   `interface Into<T> { fn into(): T }`, which follows from it through `extend<T, U :: [From<T>]> T ::
   [Into<U>]` ([05 rule 23](05-interfaces.md)): `let c: Cm = m.into()`, the type the position expects
   choosing the target. A constraint `T :: [Into<X>]` holds for every type `X` is a `From` of, and a
   value of `Into<X>` is made from such a type. No type is a `From` of itself unless it writes that,
   and `?Cm` is another target than `Cm`. `as` converts numbers only.
16. **`BigInt`** (S7f4; Lyric 5 has none, [02 T1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md)). `std.math` holds `struct BigInt`, a
   whole number of any size up to 2^31 bits. It is a `Signed`, `TotalOrder`, `Hashable`, `Clone`,
   `Default`, `From<int>`, `FromIntLiteral`, `Shl` and `Shr`, not an `Integer`, which is a fixed width.
   `BigInt.zero` and `BigInt.one`; `+`, `-`, `*`, `/`, `%`, unary `-`, of two `BigInt`s: `/` truncates
   and `%` takes the dividend's sign, as an `int`'s do, and a zero divisor panics (`LYS-RT0001`).
   `x << n` and `x >> n` take an `int`, `>>` rounding toward negative infinity; a negative count, and a
   result past 2^31 bits from a shift or a product, panic (`LYS-RT0002`). `BigInt.parse(s)` and
   `BigInt.parse(s, radix)` read what `int.parse` reads and throw its `ParseError`, `Empty` or
   `Invalid`, never `Overflow`. `x.toString()`, `x.toString(radix)`, lowercase; a radix outside 2 to 36
   panics. `x.toInt()` is the `int` where it fits, else `null`; `x.toFloat()` the nearest float, a tie
   to the even one, past the range an infinity. `x.pow(e)`, a negative exponent panicking; `x.gcd(y)`,
   never negative; `x.divRem(y)`; `x.bitLength()`, the bits of the magnitude, `0` for zero. A literal in
   a place of the type is an `int`'s, so a longer one is `LYS-PAR0007` and comes from `parse`; an
   operand is no place with a target type ([03 Lit](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)), so `x + 1` is `LYS-SEM0003`.

   **What it costs** ([01 S5c](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)). A native knows its cost from its operands and takes it
   from the budget **before** it works; where the budget does not cover it, the instance is suspended
   at that call and nothing is computed. With `n` and `m` the operands' words of 32 bits, one unit
   being what a backward jump or a call costs: `+`, `-`, a comparison, `-x`, a hash, `>>`: `1 + max(n,
   m) / 8`; `<<` by `c`: `1 + (c / 32 + n + 1) / 8`; `*`: `1 + n * m / 8`; `/`, `%`: `1 + (n - m + 1) *
   m / 8`, `1 + m / 8` where `n` is below `m`; `toString`: `1 + n * n / 4`; `parse` of `b` bytes, with
   `w = b / 8 + 1`: `1 + w * w / 4`. `toInt`, `toFloat`, `bitLength` cost nothing of their own.
17. **`Bytes`** (S7f5; [02 T1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [09 Y7](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)). `class Bytes` is binary data, what `uint8[]` is in Lyric 5: a list
   of bytes that grows and changes in place, named without an import. An element is an **`int` from 0
   to 255**: `b[i]` reads one, `b[i] = v` sets one, and a value outside that range, set, pushed, filled
   or given in a list, panics (`LYS-RT0002`). An index outside panics (`LYS-RT0003`). `^n` counts from
   the end, as on a list. `b[a..e]`, in a range's every form, is a **new `Bytes`** (03 S). `b"…"`
   ([§1 D3](01-lexical.md)) makes a new one each time it is evaluated. It is an `IndexSet<int>`,
   `Iterable`, `Contains<int>`, `Add`, `TotalOrder`, `Hashable`, `Clone`, `Default`, `Display` and
   `FromArrayLiteral<int>`. It compares by its elements, then its length, and prints as the list of its
   numbers, `[65, 0]`. `Bytes.new()`, `Bytes.withCapacity(n)`, `Bytes.zeroed(n)`, `Bytes.of(xs)`,
   `Bytes.from(it)`; `length`, `isEmpty`, `get`, `first`, `last`, `push`, `pop`, `pushAll`, `clear`,
   `truncate`, `fill`, `reverse`, `reversed`, `indexOf`, `contains`, `startsWith`, `endsWith`, `iter`,
   `toList`, of a list's meaning. What else a list can do goes through `toList()` and `Bytes.of`. What
   the field of a `Bytes` or a `BigInt` holds is the VM's object: a script can read it and give it back,
   but asking it for anything, its Debug form too, panics (`LYS-RT0007`).

   `s.toBytes()` gives a string's bytes as a new `Bytes`. `string.fromUtf8(b)` gives the text the bytes
   are and throws a **`Utf8Error`** with its `offset`, the first byte that is not well-formed, an
   `Error` as Lyric 5's is. `string.fromUtf8Lossy(b)` replaces each maximal part that is not
   well-formed by U+FFFD.

   **What it costs.** A native of `Bytes` that walks `n` bytes costs `1 + n / 32` and takes it before
   it works, as rule 16 says: `Bytes.zeroed`, `toBytes`, `Bytes.of`, `toList`, a slice of `n` bytes,
   `pushAll` of `n` bytes, a comparison over the shorter's `n`, a hash, `fill`, a byte string's making.
   `fromUtf8` is two such natives, the check and the text; `fromUtf8Lossy` one. `length`, an index, a
   set and a push cost nothing of their own. The rest is written in Script and costs what its loops
   and calls cost.
18. **Random numbers** (Lyric 5 12 §Random numbers; S7f6). `std.random` holds `class Random`, Lyric 5's
    ChaCha8 under it: `Random.seeded(seed)` gives **the stream Lyric 5's generator gives** that seed,
    an `int` being read as its 64 bits, and it asks for no right, a seeded stream being determinism's
    own ([01 S8](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)). `nextInt()`, the draw, `nextUint64` having no type here; `nextInRange(r)`,
    `nextFloat()`, `nextBool()`, `nextBytes(into)` into a `Bytes`, `nextNormal(mean = 0.0, stdDev =
    1.0)`, `shuffle(s)`, `choice(s)`, `sample(s, k)`, of a list, taking the draws Lyric 5's do. An empty
    range, and a `k` outside the list, panic (`LYS-RT0008`).

    What draws from the system is the module **`std.random.system`**, of the right `os`
    ([17 rule 1](17-host.md)): `fresh()`, Lyric 5's `Random.fresh()`, and the free forms `nextInRange`,
    `nextFloat`, `shuffle` over the program's one generator, keyed when the module is loaded. A program
    without that import, and without the other rights, repeats itself. A draw costs what a call costs.
19. **Input and output over bytes** (Lyric 5 12 §Input and output; S7g1). **`IoError`** is the one error
    input and output throw: `kind: IoErrorKind`, `path: ?string`, `detail: string`, `inner: ?Error`, its
    `message()` the kind in words, then the path and the detail where there are any: `not found: data.txt
    (opened to read)`. `IoErrorKind` names `NotFound`, `PermissionDenied`, `AlreadyExists`, `IsDirectory`,
    `NotDirectory`, `InvalidInput`, `InvalidData`, `UnexpectedEof`, `TimedOut`, `ConnectionRefused`,
    `ConnectionReset`, `AddrInUse`, `BrokenPipe`, `Closed`, `Unsupported`, and `Other { code }`, a system's
    code no kind names. The two are **the prelude's**, since `readLine()` throws them, and `import std.io {
    IoError }` names what every module sees; `std.io` itself holds the rest, of no right. A later release may
    name another kind: a `match` over it writes a `_`.

    **`Reader`** has `read(into: Bytes): int`: it fills `into` from the front and answers how many bytes it
    put there, **0 only at the end**, and at once for empty bytes; fewer than `into` holds is no end.
    **`Writer`** has `write(from: Bytes): int`: it takes from the front and may take fewer; `flush()` hands on
    what it holds back, the default does nothing. **`Seek`** has `seek(to: SeekFrom): int`, `SeekFrom.Start(n)`,
    `.End(n)` or `.Current(n)`, and answers the position from the start. `read`, `write` and `flush` throw
    `[IoError, Cancelled]`, `seek` `IoError`; an implementation throws what it may less (§6 rule 6). Bytes have
    no view: what Lyric 5 hands as a slice, a Script reader takes whole, and from a place inside bytes
    through a slice, a copy, or `b.copyInto(into, at, from, to)`, which copies `from..to` to `at` in `into`,
    does not grow it, may have one bytes on both sides, and charges as a slice does (rule 17). A range
    outside either panics (`LYS-RT0003`).

    What every reader can do: `readExact(into)` fills it whole or throws `UnexpectedEof`, the bytes that came in
    the detail; `readToEnd()` is everything in new `Bytes`; `readToString()` the same as UTF-8, bytes that are
    no UTF-8 throwing `InvalidData`, the `Utf8Error` as the cause. What every writer can do: `writeAll(from)`
    until all of it is taken, a writer that takes no byte of bytes that have some throwing `Other { code = 0 }`
    rather than being asked forever; `writeString(s)`, the text's UTF-8. **`copy(r, w): int`** copies all `r`
    holds into `w` and answers how many.

    **`ByteReader.new(b)`** reads `b`, not copied, and seeks: a position past the end reads nothing, one before
    the start panics; `position()`. **`ByteBuffer.new()`** appends what is written and reads from the front
    what was not yet read, with `length()` and `toBytes()` of what it holds. **`BufReader.new(r)`** reads `r`
    8 KiB at a time; a read at least as large, while the buffer is empty, goes to `r` directly.
    **`BufWriter.new(w)`** holds back what it is handed until its buffer is full, a `flush()` or a `close()`; a
    write at least as large goes to `w` directly, after what is held. A flush that throws keeps what `w` did
    not take. `close()` flushes and leaves `w` open.

    **`TextReader.new(r, skipBom: false)`** reads UTF-8 through a buffer of its own. `readLine()` is the next
    line without its end, a `\n` or a `\r\n`, a `\r` alone being text, or `null` at the end; a last line without an
    end is a line, the end of the last line starts none. `lines()` iterates the same, `chars()` the
    codepoints, `readToEnd()` is the rest. A codepoint split between two reads waits for its rest. Bytes that
    are no UTF-8 throw `InvalidData`, a `Utf8Error` as the cause whose offset counts from the reader's start;
    a line that throws is consumed. A byte order mark is text unless `skipBom` drops it from the front.
    **`TextWriter.new(w)`**: `write(s)`, `writeLine(s)` that and a `\n` on every system; it holds nothing back.
20. **The console** (Lyric 5 12 §The console; S7g2): the program's standard input, output and error, of no
    right. `print`, `println`, `eprintln` and `readLine` are the prelude's, and `import std.io { … }` names what
    every module sees; **`eprint`**, **`flush`**, **`stdin`**, **`stdout`** and **`stderr`** are `std.io`'s.
    `eprint(v)` and `eprintln(v)` write `v`'s text on the standard error as `print` and `println` on the output.

    Each stream is buffered as Lyric 5's: the output a line at a time where it is a terminal, a block at a time
    otherwise, the error always a line at a time. **`flush()`** writes what both hold, the output's first, and
    drops a failure. What they hold is written at every end of the program: its end, a panic's report, an error
    that leaves it, the output before the report. Output through one pipe shows the modes: the error's lines
    come as they are written, the output's block at the end or at a flush.

    **`readLine()`** is the next line of the standard input without its end, a `\n` or a `\r\n`, `null` at the end
    of the input. It throws `IoError` where the read fails, or `InvalidData` for bytes that are no UTF-8, the
    offset in its detail, no cause; the line is consumed. **`stdin()`** is a `Reader` over the one buffer of the
    input, with `readLine()`, `lines()`, an iterator of the same, and `read(into)`, which takes what a line's
    read left first; 0 at the end, and at once for empty bytes. All three wait (§10 rule 18), so a cancel ends
    them: they throw `[IoError, Cancelled]`, where Lyric 5's console is not cancelled. `read` is charged by the
    bytes of `into`, as a native of `Bytes` is.

    **`stdout()`** and **`stderr()`** are `Writer`s over the buffers `print` and `eprint` write into, so what the two
    write keeps its order. `write` takes all it is handed, `flush()` throws what the system says, a pipe nobody
    reads being `BrokenPipe`; the console is not `Closeable`. `write` is charged by its bytes. A write to the
    console does not wait: a full pipe holds up the instance, for `print` and for these alike. A standard output
    nobody reads ends a printing program as Lyric 5's does, the error's lines written first; a `Writer` of
    `stdout()` throws instead.
21. **Paths** (Lyric 5 12 §Paths; S7g3): `std.path`, of no right: a path is a string, there is no `Path` type, and
    these take one apart and put one together lexically, as Go's `path/filepath` does; none asks the file system.
    **`separator`** is `\` on Windows and `/` elsewhere. On Windows both separate, a path may start with a volume, a
    drive `C:` or a share `\\server\share`, two names compare without regard to the case of ASCII letters, and what
    these build they build with `\`.

    **`normalize(p)`** is Go's `Clean`: separators run together, `.` dropped, a `..` takes the element before it, is
    dropped above the root and kept in a relative path, no separator at the end but the root's, and `.` for nothing.
    **`join(parts...)`** joins the parts that are not empty by the separator and normalizes, empty for no such part;
    on Windows a drive alone joins without one, `C:a`. **`fileName(p)`** is the last element, `.` for nothing, the
    separator for one of separators alone; **`parent(p)`** the rest, normalized; **`extension(p)`** the last element's
    extension with its dot, from its last dot, of `.bashrc` all of it; **`stem(p)`** the last element without it;
    **`withExtension(p, ext)`** the path with another, a dot added to `ext` where it has none, dropped for an empty one.

    **`isAbsolute(p)`**: it starts with the root, on Windows a drive with the root, or a share. **`relative(base,
    target): ?string`** is the path that names `target` from `base`, `.` for the same place, `null` where none exists:
    one rooted and the other not, two volumes, a base that climbs above where the target is. **`components(p)`** lists
    the root with its volume, then the elements, without the empty ones and `.`, keeping `..`; nothing is normalized.
22. **Files** (Lyric 5 12 §Files; S7g4): `std.fs`, of the right `file`. **`File.open(path)`** opens to read,
    **`File.create(path)`** to write, made where it is not there, cut to nothing where it is,
    **`File.openWith(path, options)`** as an **`OpenOptions`** says: `read`, `write`, `append` (writes at the end),
    `create`, `truncate`. Options that read and write nothing, cut without writing from the start, or create without
    writing are `InvalidInput`, before the system is asked.

    A file is a `Reader`, a `Writer` and a `Seek` at its position, and `Closeable`. `read` and `write` may take part of
    the `Bytes`, as rule 19 allows. What a file cannot do is an `IoError` with its path and what was done, `opened to
    read`, `opened to write`, `read`, `written`, `sought`, `closed`: `not found: data.txt (opened to read)`; other
    failures are `Other { code }`, the system's number. Whether a directory opens as a file and fails at the read, or
    fails to open, is the system's. After `close()` every call throws `Closed`, a second `close()` does nothing; a `File`
    built by a script holds no file and panics (`LYS-RT0007`).

    A file's call waits as rule 20 says, charged before it starts, by the path's bytes, by the bytes of what it reads
    or writes, or as one; the other tasks go on. It ends in a bounded time and no cancel ends it: in a cancelled task
    it runs to its end, and the next wait throws `Cancelled`. So a `File` declares `IoError` alone; its `readToEnd`,
    `readToString`, `writeAll` and `writeString` are its own for that, as are the conveniences.

    **`fs.readText(path)`** is the file's UTF-8, bytes that are none `InvalidData` with the path and the decoder's error
    as the cause, a byte order mark text; **`fs.readBytes(path)`**, **`fs.writeText(path, text)`** and
    **`fs.writeBytes(path, bytes)`** make or cut the file as `File.create` does, **`fs.appendText(path, text)`** writes at
    its end and makes it where it is not there. Each closes its file on every way out; what the close throws counts
    where nothing went wrong before. **`fs.lines(path)`** gives the lines as `TextReader.readLine` gives them, through a
    **`FileLinesIter`** that is `Closeable`: it closes the file at its end and at its first error, a loop that leaves it
    early closes it, and so does `close()`. After its end or an error it gives no more; after `close()` a call throws
    `Closed`, and what it had read ahead is not given.
23. **Directories** (Lyric 5 12 §Directories; S7g5): `std.fs` further, of the same right; each call of the
    system's as a file's (rule 22): the other tasks go on, a cancel does not end it, and it declares
    `IoError` alone. **`fs.metadata(path)`** says what a path names, through links: `size`, `isFile` and
    `isDir` — neither for what is neither —, `readonly`, and `isSymlink`, whether the path itself is a link; a
    link that leads nowhere is not found. `modified` comes with `std.time`. **`fs.exists(path)`** is
    whether `metadata` answers. **`fs.createDir`**, **`fs.remove`**, **`fs.removeDir`** and
    **`fs.rename(from, to)`** say what they cannot do with the path and `made`, `removed`, `renamed to <to>`;
    a directory that is not empty is `Other` with the system's code. **`fs.readDir(path)`** gives
    `DirEntry`s, `name`, `path` — the directory's joined with the name —, `isFile`, `isDir`, `isSymlink` of the
    entry itself, and `metadata()` that follows it; its iterator lets the directory go at its end, at an
    error, at a `for` that leaves early and at `close()`, after which it throws `Closed`. **`fs.canonicalize`**
    is the path as the system names it, and must be there; **`fs.absolute`** asks nothing more of the file
    system than the working directory. **`fs.createDirAll`** makes every directory above that is not there;
    something else there is `NotDirectory`. **`fs.removeAll`** removes all that is in it: a link is removed,
    never followed into, nothing there is nothing to do, and it removes what it can and throws the first
    error. **`fs.copy(from, to)`** answers the bytes copied; from a directory `IsDirectory`, onto the same file by
    `canonicalize` `InvalidInput`, before anything is written. **`fs.walk(path)`** gives what is under the path:
    depth first, a directory before what is in it, each directory's entries in the byte order of their names,
    links not followed, nothing held open; an error ends it. **`fs.tempDir()`** and **`fs.tempFile()`** make
    a new place under the system's directory for temporary files and answer its path; neither is removed
    by itself. These calls take from the budget as a file's do, by the bytes of their paths, before they
    start; what is put together here takes for each call it makes. A `ReadDirIter` a script built itself
    panics with `LYS-RT0007`.

## Deviations (skeleton, written with later milestones)

- An adapter is a class, as Script's iterators are (a pull changes it); the functions it takes
  throw what they throw, without a `throws` clause ([12 Src](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).
- `join` takes every item, written as `{x}` writes it — a `Display` its `show()`, any other
  value its Debug form —, where Lyric 5's asks a `Display`: every value prints in Script.
- One integer and one float type (03 K3): `Integer`'s and `Float`'s members are `int`'s and
  `float`'s, written there, no defaults of the interface; no `exact` and `clamping`, which narrow
  to another integer type; `fromBits` and `toBits` take and give the bits as an `int`, Script
  having no `uint64`; `pow` takes an `int` and panics on a negative one (`LYS-RT0007`), Lyric 5's
  taking a `uint`.
- A builder has none of Lyric 5's `sized`, `putInt` and the other members f-strings write
  through: Script's f-strings concatenate. `Format.format` takes the spec as a `string`, Script
  having no `StringView`; a width or a precision of more than nine digits is no spec.
- A string's slice is a new string, never a view (03 Str); `toBytes()` and `string.fromUtf8` take and
  give a `Bytes` (rule 17). A string's parts and lines are new strings, not views; `T.parse(s)`
  takes a string. A string's `contains` takes every pattern; `c in s` asks it for a character,
  but a string is no `Contains<char>` to a constraint (STATUS P29).
- A map keeps the order its keys came in ([03 Eq](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)) and has no hasher parameter `H`: one hasher,
  the prelude's ([05](05-interfaces.md) rule 20); `Map.from` takes a list. The VM keeps where
  each hash lies; the program hashes the keys and compares them — keys of `int`, `char`, `bool`
  and `string` too, whose way through the VM alone (STATUS P27) is measured with P21 (S7k). A
  set keeps the order its values came in and has no hasher parameter either; `Set.of` takes a
  list.
- Lyric 5's API adapted to Lyric-Script's types, plus the batteries `cli`, `csv`, `log`, `fs.glob`, and `reflect`; no `sync`, `thread`, `ffi`, `meta`, `syntax`, `build` ([12](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).

**Conformance.** `conformance/cases/12-stdlib/` (`since: 1.0.0`).

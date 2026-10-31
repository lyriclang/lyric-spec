# 12. Standard library contract

**Base.** Lyric 5.0 [§12](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/12-stdlib.md) applies, with the deviations below.

**Status.** The core written (S2), the standard library's modules (S7a), its iterators (S7c6),
collections (S7d), the strings' members and reading values from text (S7e1–S7e2); the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

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
   `env(name): ?string`. The rest come with the milestones that build them.
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
   `sum()`, `product()` and `average()` of `int` or of `float` values, Script's two numbers —
   zero, one and `null` where there is none, `average()` a `float` summed as one —; `min()` and
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

## Deviations (skeleton, written with later milestones)

- An adapter is a class, as Script's iterators are (a pull changes it); the functions it takes
  throw what they throw, without a `throws` clause ([12 Src](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).
- `join` takes every item, written as `{x}` writes it, where Lyric 5's asks a `Display` — every
  value prints in Script, its `Display` comes with S7e; `sum` and `product` stand on `int` and
  `float` items, not on a `Num` (STATUS P25).
- A string's slice is a new string, never a view (03 Str); `toBytes()` and `string.fromUtf8` come
  with `Bytes` (S7f). A string's parts and lines are new strings, not views; `T.parse(s)`
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

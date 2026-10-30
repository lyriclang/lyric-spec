# 12. Standard library contract

**Base.** Lyric 5.0 [§12](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/12-stdlib.md) applies, with the deviations below.

**Status.** The core written (S2), the standard library's modules (S7a); the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

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
   rule 16; S7c6c2); `groupBy`, `toMap` and `toSet` come with the map and the set (S7d).

## Deviations (skeleton, written with later milestones)

- An adapter is a class, as Script's iterators are (a pull changes it); the functions it takes
  throw what they throw, without a `throws` clause ([12 Src](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).
- `join` takes every item, written as `{x}` writes it, where Lyric 5's asks a `Display` — every
  value prints in Script, its `Display` comes with S7e; `sum` and `product` stand on `int` and
  `float` items, not on a `Num` (STATUS P25).
- Lyric 5's API adapted to Lyric-Script's types, plus the batteries `cli`, `csv`, `log`, `fs.glob`, and `reflect`; no `sync`, `thread`, `ffi`, `meta`, `syntax`, `build` ([12](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).

**Conformance.** `conformance/cases/12-stdlib/` (`since: 1.0.0`).

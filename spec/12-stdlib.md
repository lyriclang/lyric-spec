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
   iterator ([07](07-statements.md) rule 8). Each gives a class of its own under Lyric 5's name
   (`MapIter`, `FilterIter`, …), lazy: a pull takes from the iterator below what it needs. A
   program imports a class where it writes the type, `import std.iter { MapIter }` (`LYS-SEM0011`
   otherwise). An adapter over a `Closeable` iterator is `Closeable` and passes `close()` on —
   `rev` excepted —, so a loop that leaves `gen().map(f)` early closes the coroutine; `zip` and
   `chain` close both of theirs where both are. `cycle()` comes with `Clone` (S7c6c), the
   terminators with S7c6b2.

## Deviations (skeleton, written with later milestones)

- An adapter is a class, as Script's iterators are (a pull changes it); the functions it takes
  throw what they throw, without a `throws` clause ([12 Src](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).
- Lyric 5's API adapted to Lyric-Script's types, plus the batteries `cli`, `csv`, `log`, `fs.glob`, and `reflect`; no `sync`, `thread`, `ffi`, `meta`, `syntax`, `build` ([12](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)).

**Conformance.** `conformance/cases/12-stdlib/` (`since: 1.0.0`).

# 8. Expressions

**Base.** Lyric 5.0 [§8](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/08-expressions.md) applies, with the deviations below.

**Status.** The core written (S2); the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

## Written (S2, the core)

1. **Mixed arithmetic.** An arithmetic operation or a comparison with an `int` and a `float`
   operand widens the `int`; `int / int` stays the integer division
   ([03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)). `+` joins two strings; it joins nothing else to a string
   (`LYS-SEM0003`) — an f-string does.
2. **`as`** converts between `int`, `float` and `char` alone (`LYS-SEM0006`).

## Written (S7, the core collections)

3. **Indexing a list** ([03 Index](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)). `xs[i]` is the element at the `int`
   index `i`, counted from 0; `xs[i] = v` writes it, and `xs[i] op= v` reads and writes it with
   the list and the index evaluated once. An index below 0, or at the length or above, is a
   panic, `LYS-RT0003` (Lyric 5's), the list unchanged. `xs[a..b]` and `xs[a..=b]` are a
   **slice**: a new list of those elements ([03 S](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)), a panic (`LYS-RT0003`) where the range is not
   within `0..=length()` or ends before it begins. In the brackets `^n` counts from the end —
   the length less `n`, `^1` the last element, `^0` past it — at an index, at a write and at an
   end of a range, the list evaluated once (Lyric 5 03 T14); a range may leave out its ends:
   `xs[a..]` is `xs[a..^0]`, `xs[..b]` is `xs[0..b]`, `xs[..]` the whole list. `^` counts from the
   end in a list's brackets only. Indexing a map comes with S7d, a string with S7e.
4. **Indexing a type of one's own** (03 Index; Lyric 5 `Index<K>`, `IndexSet<K>`; S7c2). The
   prelude declares `interface Index<K> { type Output; fn index(k: K): Self.Output }` and
   `interface IndexSet<K> :: Index<K> { fn setIndex(k: K, v: Self.Output) }`. `x[k]` is
   `x.index(k)` where `x`'s type is an `Index` — on the type, through a constraint, through an
   interface value —, else `LYS-SEM0007`; `x[k] = v` is `x.setIndex(k, v)` where it is an
   `IndexSet`, else `LYS-SEM0019`; `x[k] op= v` reads and writes with `x` and `k` evaluated once.
   `^` counts from the end of a list alone (`LYS-SEM0007`).

## Deviations (skeleton, written with later milestones)

- Mixed `int`/`float` arithmetic widens to `float`; `int / int` stays integer division; `as` only between `int`, `float` and `char`; no prefix `&`, no `comptime` ([03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [09](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).

**Conformance.** `conformance/cases/08-expressions/` (`since: 1.0.0`).

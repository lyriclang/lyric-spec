# 9. Patterns

**Base.** Lyric 5.0 [§9](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/09-patterns.md) applies, with the deviations below.

**Status.** Written for the forms S3 builds, and list patterns (S7b3); type patterns with the
interfaces (S3f).

## Written (S3)

1. **The forms.** Lyric 5 §1–§4 apply to the forms there are: a bare name, `_`, literals, ranges
   over int and char literals, variants unqualified (`.Num(v)`, `.Rect { w = 0, h }`) and
   qualified (`Shape.Num(v)`), field patterns over a struct or class, tuples, alternatives
   `P | Q`, guards `P if e`, at every depth and through an optional. The codes are Lyric 5's:
   `LYS-SEM0029` for a pattern that cannot match the value's type, `LYS-SEM0031` for a payload
   form the variant does not have, `LYS-SEM0032` for alternatives binding different names,
   `LYS-SEM0097` for a name bound twice, `LYS-SEM0111` for a bare name that spells a variant.
2. **Where a pattern stands.** In an arm of `match`, after `let`/`var` — `let P = e else { … }`,
   its `else` leaving on every path, and without `else` only what matches every value of its
   type — a field pattern over a struct of such too, `let P { x, y } = p` (S7d2) —
   (`LYS-SEM0098`) —
   and in `if (let P = e)` and `while (let P = e)`, where a bare name keeps taking the value of
   an optional (Lyric 5 03 §3.2 rule 5); an `if let` whose pattern cannot fail is warned about
   (`LYS-SEM0104`).
3. **Coverage.** A `match` statement or value covers every value of its scrutinee's type, or it
   is refused with a value no arm takes, written as a pattern (`LYS-SEM0050`); a guarded arm
   covers nothing. An arm no value reaches is warned about (`LYS-SEM0112`) under Lyric 5 §4's
   rule.
4. **Arms** stand apart by `,` or a line end. A line that begins with `.` goes on the line before
   (01 NL rule 3), so a value arm before a `.Variant` arm on the next line ends with `,`
   (`LYS-PAR0035`); after a block arm none is needed.

## Written (S7, the core collections)

5. **List patterns** (Lyric 5 §9's array patterns): `[p, q]` matches a list of exactly those
   elements, `[p, q, ..]` one of at least them, `..` at any place among the elements — `[first,
   ..rest]`, `[a, .., z]` — and one at most (`LYS-PAR0033`). An element before the `..` stands at
   its position from the front, one after it from the end. `..name` binds the elements between
   as a new list ([09 Y6](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)); `[..rest]` takes every list. The length is tested before
   any element is read. Against a value that is no list, `LYS-SEM0029`; through an optional as
   every pattern. For coverage a list column counts lengths: each length up to the first that
   no pattern without `..` reaches and every pattern with `..` covers, that one standing for every
   longer list — `[]` and `[_, ..]` cover all, `[]` and `[a]` leave `[_, _, ..]` out.

## Deviations

- `..rest` binds a copy ([09 Y6](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).

**Conformance.** `conformance/cases/09-patterns/` (`since: 1.0.0`).

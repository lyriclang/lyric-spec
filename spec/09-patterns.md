# Patterns

> **Partly written.** §1 to §4 were written with milestone **M3** of the Lyric 5 plan (slices S4
> to S6), the type patterns with **M4**, the type-set pattern with the catch-up block N (N2c),
> spec-first: each rule lands here with its conformance case before or with its implementation.
> Source of the decisions:
> [08 Syntax Y6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md),
> [03 Type system T9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md).

## Scope

Literal, binding (a bare name always binds), variant (`.Red`), field, tuple, array with rest, type and or patterns; exhaustiveness.

**Conformance.** `conformance/cases/09-patterns/`.

## 1. Where a pattern stands

1. A pattern stands in an arm of `match`, after `let` or `var` in a binding
   (`let .Num(n) = s else { … };`, [07](07-statements.md)), and in `if (let P = e)` and
   `while (let P = e)`.
2. A pattern is tried against the **scrutinee**; it **matches** or it does not, and when it
   matches its **bindings** hold parts of the value. A pattern that matches every value of the
   scrutinee's type is **irrefutable**.
3. The arms of a `match` are tried in the order they are written, and the first that matches
   wins. An arm may carry a **guard**, `Pattern if expr`, evaluated with the pattern's bindings
   in scope only when the pattern matched; the arm is taken only when the guard is `true`.
4. In a binding, `let` or `var` before the pattern decides the mutability of **all** its
   bindings. A binding **copies** the part it names, as any binding does
   ([03 §2.1](03-types.md#21-values-and-references)): writing through a `var` binding of a
   struct payload leaves the scrutinee as it was; a reference bound is the object.
5. `let P = e else { … };` binds the names of `P` when it matches and runs the block
   otherwise; the block **leaves** — by `return`, `throw`, `break`, `continue` or a panic — on
   every path, or the statement is refused (`LYR-SEM0098`), since after it the names are
   bound. Without `else` the pattern is irrefutable, or the statement is refused. An
   `if (let P = e)` whose pattern is irrefutable is a warning (`LYR-SEM0104`).

## 2. The forms

1. **Wildcard.** `_` matches every value and binds nothing.
2. **Binding.** A **bare name** binds the whole value it stands against, always, whatever the
   name spells. A bare name that spells a variant of the scrutinee's enum is refused
   (`LYR-SEM0111`), and the diagnostic names the two forms that test the variant: it would
   otherwise match every value under the variant's name, and a typo in a variant would match
   in silence.
3. **Literal.** An integer, float, character, string, `bool` or `null` literal matches the
   value equal to it, by the equality of the scrutinee's type; a negative number literal is a
   literal. A `null` literal stands against an optional only ([03 §3.2](03-types.md#32-tests-and-narrowing)).
   A float literal never matches NaN.
4. **Range.** `a..b` and `a..=b` over integer and character literals match the values of the
   range, `-5..=-1` included.
5. **Variant.** `.Red`, `.Num(v)` and `.Rect { w = 0, h }` match one variant of the
   scrutinee's enum, the enum unnamed ([03 §4.2](03-types.md#42-the-enum-the-position-names));
   the qualified `Signal.Red`, `Shape.Num(v)` and `Shape.Rect { … }` say the same with the enum
   named, and both forms may stand in one `match`. A tuple variant's pattern has one
   sub-pattern per payload element. A struct variant's pattern names fields: `w = P` tests the
   field `w` against `P`, and a bare `h` binds the field `h` to the name `h`. A field left out
   is not read; the pattern **may leave fields out**. A name the variant does not have, a
   payload form the variant does not have and a variant the enum does not have are refused
   (`LYR-SEM0015`, `LYR-SEM0031`, `LYR-SEM0029`). The dotted form on a scrutinee that is no
   enum is refused (`LYR-SEM0029`).
6. **Field.** `Point { x = 0, y }` over a struct or a class names the type the scrutinee
   already has, reads the fields it names and no others, and matches when every field pattern
   does. `Point { x, y }` tests nothing and is irrefutable.
7. **Or.** `P | Q` matches when either alternative does; the alternatives are tried in order.
   Every alternative binds the **same names at the same types** (`LYR-SEM0032`).
8. A name binds **once** in a pattern (`LYR-SEM0097`): `.Rect { w = n, h = n }` is refused,
   not read as one of its halves. An or-pattern's alternatives repeat the names by rule.
9. A pattern tests and binds at **every depth**: `.Some(.Num(n))`, `.Rect { w = 0 }` inside
   an or-pattern, a literal under a field. There is no depth at which a form is refused for
   being nested.
10. **Array.** `[a, b, c]` matches an array, a view or an inline array ([03 §5](03-types.md))
    of exactly that many elements, each against its pattern; `[first, ..rest]`, `[.., last]`
    and `[first, .., last]` match one long enough for the elements beside the rest. At most
    one rest stands in a pattern, and `..rest` **binds a view** of the elements it covers —
    a `Slice<T>`, sharing them, never a copy.
11. **Tuple.** `(a, _)` matches a tuple ([03 §6](03-types.md)) of that many elements, each
    against its pattern; `let (a, b) = t;` binds through the same pattern, and a nested tuple
    is taken apart in place: `((a, b), c)`. The arity is the type's, or the pattern is refused
    (`LYR-SEM0029`).
12. **Type.** `c: Circle` and `_: Circle` stand against an **interface value** and match when
    it holds a value of that type ([05 §9](05-interfaces.md#9-any-type-tests-and-type-patterns));
    `c` binds that value **as that type** — the object for a class, a copy for a struct or an
    enum. On a scrutinee whose type is no interface the pattern is refused (`LYR-SEM0131`):
    the static type answers already.
13. **Type set** (08 Y6; N2c). `s in [Circle, Rect]` and `_ in [Circle, Rect]` stand against an
    interface value and match when it holds a value of **one of the types**, tested in order —
    the form of `catch (e in [A, B])` ([06 §4](06-errors.md#4-the-try-block-and-its-clauses)),
    under the same list rule: one type bare, `s in Circle`, several in brackets, an empty list
    refused (`LYR-PAR0049`). `s` binds as the one type of a set of one, as `s: Circle` does; of
    a larger set it binds the **interface value** itself, which **carries the set** as a catch
    binding does (05 K7): a `match` over a `let` binding of it is exhaustive with an arm per
    type, and a `throw` of it throws the set. On a scrutinee whose type is no interface the
    pattern is refused (`LYR-SEM0131`).

## 3. Exhaustiveness

1. A `match` is **exhaustive**: its arms cover every value of the scrutinee's type, or the
   `match` is refused (`LYR-SEM0050`). The diagnostic names a **witness**: a value no arm
   matches, written the way a pattern is written — `.Rect { … }`, `.Some(false)`, `null` —
   so that what it names can be added as an arm.
2. The values are enumerated for an enum (its variants, each with its payload enumerated in
   turn), for `bool` (`true`, `false`) and for an optional (`null` and the values of the inner
   type); a field pattern enumerates through its fields. An array or a view is enumerated by
   its **length classes**: an arm whose fixed positions all bind without testing covers its
   length, or every length from there up when it carries a rest, and the witness is the
   smallest length nothing covers; an inline array has one length. A tuple is enumerated
   **through its columns**: the arms cover it when every combination of the elements' values
   does, and the witness is written as a tuple. Every other type — `int`, `string`, `float`,
   `char`, a class — is **open** and needs a `_` or a binding arm.
3. A guarded arm covers nothing: whether its guard holds is not known to the check.
4. A scrutinee of type `?E` admits `null` and the variants of `E` in one `match`; presence is
   established before a variant is examined, and the arms are still tried in order.

A type pattern covers one conformer, a type-set pattern each of its types. Over an open interface the set of conformers is open, so a
match of type patterns needs `_` (`LYR-SEM0050`); over a **sealed** interface
([05 §10](05-interfaces.md#10-sealed-interfaces)) the set is closed, and unguarded type
patterns for every conformer make the match exhaustive — the diagnostic names the conformer
missing as the pattern to add, `_: Rect`.

## 4. Unreachable arms

1. An arm no value can reach is a **warning** (`LYR-SEM0112`), not an error: every arm after
   an unguarded arm that is irrefutable, and an unguarded arm that repeats a unit variant, a
   literal or `null` an unguarded arm above already tests. A payload pattern and a guarded arm
   keep a case open.
2. Together with §2.2, a misspelt variant in a bare name gets two messages and no silent way
   through: the binding it would be is refused when the spelling is a variant, and shadows
   the arms below it — reported as unreachable — when it is not.

# 3. Types and conversions

Lyric is statically typed with no implicit conversions: two different types never assign to each
other without an explicit construct, and a value carries no runtime type tag — every dispatch
the language performs is resolved at compile time, with one exception (interface values,
chapter 5).

## 3.1 The primitive types

| Type | Meaning |
|---|---|
| `int` | 64-bit signed integer, two's complement |
| `uint` | 64-bit unsigned integer |
| `int8 int16 int32 int64` | width-named signed integers |
| `uint8 uint16 uint32 uint64` | width-named unsigned integers |
| `float` | IEEE 754 binary64 |
| `float32 float64` | width-named IEEE 754 |
| `bool` | `true` / `false` |
| `char` | one Unicode scalar value (a code point, never a UTF-16 unit) |
| `string` | an immutable sequence of code points |
| `void` | the absence of a value; a return type only |

Every row is a **distinct type**. `int` and `int64` have identical width and identical runtime
representation and still do not assign to each other; the same holds for `float`/`float64` and
`uint`/`uint64`. The unnamed widths (`int`, `uint`, `float`) are the language's defaults —
literals without a suffix have them — and the width-named types exist for layouts and
boundaries. Crossing between any two numeric types is `as` (§3.6).

One deliberate accommodation: an **unsuffixed numeric literal adapts to its context type**
when its value fits — in an annotated binding (`let n: int8 = 100;`), as an argument, and as
the other operand of a binary expression (`x + 1` with `x: int8`). A value that does not fit
is the ordinary assignment error (`let n: int8 = 200;`), a suffixed literal has exactly its
suffix's type, and adaptation applies to LITERALS only, never to expressions or variables:
`let a = 100; let b: int8 = a;` is an error.

## 3.2 Integer arithmetic overflows by wrapping

**Integer arithmetic is unchecked two's-complement wrapping arithmetic.** `+`, `-`, `*` on a
signed or unsigned integer type produce the low bits of the mathematical result at the
operand width; overflow is not an error, not undefined, and not configurable. The most negative
value of a signed type has no positive twin: negation and `absInt` return it unchanged.

Division and remainder truncate toward zero, and the remainder follows the sign of the
dividend. Division by zero is a panic. (`divFloor`/`modFloor` in the standard library provide
the flooring pair; they are library functions, not operators.)

*This is a decision, frozen here (2026-08-19): wrapping is deterministic and identical on every
platform, which is the property this language values above overflow detection. A future checked
mode would be a new construct, never a change to these operators.*

## 3.3 Composite types

- `?T` — an optional. `??T` is not a type: the grammar refuses the nesting, and no inference
  produces it — `null` is the one empty value at every depth. `?T` is not `T`; using the value
  requires narrowing (chapter 7), `!` (panic on empty), or `??` (fallback).
- `T[]` and `T[N]` — arrays: reference values of fixed length; `T[N]`'s length is part of the
  type. Element access panics out of bounds. `string` is NOT indexable, by decision: code-point
  access is O(n), and an index operator would hide a quadratic loop.
- `(A, B, …)` — tuples, taken apart by destructuring.
- `fn(A, B) -> R` — function values; closures capture by reference.
- `Coroutine<T>` — a suspended computation yielding `T` (chapter 10).
- Ranges (`a..b`, `a..=b`) are an internal iteration form, not a nameable type.

## 3.4 Declared types

`struct` (value semantics), `class` (reference semantics), `enum` (tagged variants, with or
without payloads), `interface` (chapter 5). Generic declarations are monomorphized: each
distinct type-argument tuple is its own type with its own layout (chapter 8), which is what
lets values stay untagged.

## 3.5 Type aliases, transparent and opaque

`type Name = T;` names a type: `Name` and `T` are interchangeable everywhere, and the alias
never appears in a diagnostic where `T` serves. An alias must not expand through itself
(`LYR-SEM0064`).

`opaque type Name = T;` creates a new **identity** over the same layout:

- nothing converts implicitly in either direction (`LYR-SEM0001` names the types);
- the explicit `as` to exactly `T` and back is the only crossing (§3.6); two opaque aliases of
  the same underlying do not cast sideways;
- `==`/`!=` compare two values of the SAME opaque alias by their underlying; every other
  operator, ordering included, is refused (`LYR-SEM0003`);
- an opaque alias satisfies no constraint, not even one its underlying satisfies;
- an f-string does not render it (`LYR-SEM0006`);
- at runtime the value IS its underlying: the cast is free, and in a native signature the
  alias resolves to the underlying — a host sees the plain value, a script cannot forge one.

## 3.6 Conversions: `as`

`as` is the only conversion construct, and it is total over exactly these cases:

1. **numeric ↔ numeric** — between any two of the numeric primitives (and `char`, which
   converts as its code point). Narrowing keeps the low bits (wrapping, §3.2); int → float
   rounds to nearest; float → int truncates toward zero.
2. **opaque ↔ its underlying** — identity at runtime (§3.5).
3. **declared conversions** — `v as T` where the type of `v` conforms to `Into<T>`
   (`std.core`): the cast IS the call `v.into()`, resolved like any method (chapter 6's
   operator rule).

Everything else is an error (`LYR-SEM0006`) whose message names the `Into` route.

## 3.7 Assignability

`a = b` (and argument passing, returns, initializers) requires the types to be **equal**:
structurally for composites, by declaration identity for named types, by symbol for opaque
aliases and type parameters. The two deliberate widenings:

- `T` assigns to `?T`;
- `null` assigns to any `?T`.

There is no numeric widening, no subtyping between declared types, and no variance: `int[]`
and `?int[]` are unrelated. A concrete type assigns to an interface TYPE it conforms to by
constructing an interface value (chapter 5); an interface value does not convert to another
interface type, parent included.

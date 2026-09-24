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
when its value fits. The contexts, exhaustively: an annotated binding's initializer, a call
argument, a struct or variant field initializer, a `return` value, a parameter default, and
the other operand of a binary expression (`x + 1` with `x: int8`; `??` counts). **Since 2.1
the context PROPAGATES structurally**: into the elements of an array literal
(`let xs: int64[] = [1, 2, 3];`) and into the arms of a `match` or if-expression standing in
a context position (`let m: int64 = if (c) 1 else 2;`) — with a context the arms and elements
check against it; without one they unify among themselves as before (§6.9). A leading `-`
folds into the literal, so `let n: int8 = -8;` and `-9223372036854775808` are literals, not
unary expressions.

"Fits" is exact. For an integer target the value is in range; for a FLOAT target — an integer
literal adapts to `float`/`float32` too — the value must be exactly representable at the
target width: `let g: float = 9007199254740993;` (2⁵³+1) is the ordinary assignment error,
never a silent rounding. A value that does not fit is that same error (`let n: int8 = 200;`),
and an unannotated context types the literal `int`, so a magnitude beyond `int`'s range is an
error there — not a bit reinterpretation. A suffixed literal has exactly its suffix's type,
and adaptation applies to LITERALS only, never to expressions or variables:
`let a = 100; let b: int8 = a;` and `takes64(1 + 1)` are errors.

## 3.2 Integer arithmetic overflows by wrapping

**Integer arithmetic is unchecked two's-complement wrapping arithmetic.** `+`, `-`, `*` on a
signed or unsigned integer type produce the low bits of the mathematical result at the
operand width; overflow is not an error, not undefined, and not configurable. The most negative
value of a signed type has no positive twin: negation and `absInt` return it unchanged.

Division and remainder truncate toward zero, and the remainder follows the sign of the
dividend. Division by zero is a panic. The one overflowing division, `min / -1`, WRAPS to
`min` like every other overflow (`min % -1` is 0) — it is not a second panic case.
(`divFloor`/`modFloor` in the standard library provide the flooring pair; they are library
functions, not operators.)

*This is a decision, frozen here (2026-08-19): wrapping is deterministic and identical on every
platform, which is the property this language values above overflow detection. A future checked
mode would be a new construct, never a change to these operators.*

## 3.3 Composite types

- `?T` — an optional. `??T` is not a type: the grammar refuses the nesting, and no inference
  produces it — `null` is the one empty value at every depth. `?T` is not `T`; using the value
  requires narrowing (chapter 7), `!` (panic on empty), or `??` (fallback).
- `T[]` — arrays: reference values of fixed length. The length is a property of the VALUE,
  never of the type — a type written with one (`int[3]`) is refused (`LYR-PAR0043`, since
  3.4.1; the value is built with `[x] * n`). Element access panics out of bounds. `string` is
  NOT indexable, by decision: code-point access is O(n), and an index operator would hide a
  quadratic loop.
- `(A, B, …)` — tuples, taken apart by destructuring.
- `fn(A, B) -> R` — function values; closures capture by reference.
- `Coroutine<T>` — a suspended computation yielding `T` (chapter 10).
- Ranges (`a..b`, `a..=b`) are an internal iteration form, not a nameable type.

## 3.4 Declared types

`struct` (value semantics), `class` (reference semantics), `enum` (tagged variants, with or
without payloads), `interface` (chapter 5). Generic declarations are monomorphized: each
distinct type-argument tuple is its own type with its own layout (chapter 8), which is what
lets values stay untagged.

**An initializer settles every field.** A field declared with a default (`Field` in §2 takes an
optional `= Expr`) may be left out and takes it; a field without one must be given a value, and
an initializer that leaves any out is refused (`LYR-SEM0106`, since 4.6.0), naming all of them
at once rather than one per attempt. With `LYR-SEM0015` for a field the type does not have and
`LYR-SEM0070` for one given twice, that is a single rule read from three sides: an initializer
mentions each of its type's fields at most once, and every field without a default at least
once. A value with an unset field does not exist at any point, which is why there is no
partially built object to observe and no zero value to fall back on.

## 3.4a `mut` methods, and what an immutable binding protects

`mut fn` declares that a method may write its receiver. On a **struct** it is enforced: a
non-`mut` method assigning to `this.f` is `LYR-SEM0019`. On a **class** the effect is unspecified,
and the reference implementation enforces nothing — a non-`mut` method may write its receiver's
fields freely.

The keyword is part of the contract on BOTH regardless: §5.1's conformance test compares
signatures exactly, `mut` included, so an interface method declared `mut` is satisfied only by a
`mut` implementation. On a class that is a promise nothing else checks. `LYR-SEM0108` marks a
non-`mut` class method that writes `this` (since 4.6.0; §12.5); **5.0 settles what `mut` means on
a class.**

**The binding side is the same question from the other end.** `let` is immutability of the
BINDING and not of the value (§7.1): a `let` of a class value permits `mut` calls and field
writes through it. For a STRUCT the same rule has a consequence with no obvious reading —
`let p = P { … }; p.x = 5;` compiles, although `p` itself can never be reassigned and the struct
is a value. A parameter is an immutable binding by the same rule and behaves the same way.
`LYR-SEM0109` marks a field written through either (since 4.6.0; §12.5).

**5.0 settles what a struct is**, and one answer settles all of it. The candidate on the table is
`mut struct` — a struct is immutable unless declared otherwise — under which an immutable
binding's fields are not writable, a parameter raises no separate question, and "shared" becomes
indistinguishable from "copied", so `?Struct` stops being a third question. Nothing here commits
to that answer; what the warnings commit to is that the places exist and can be found.

## 3.5 Type aliases, transparent and opaque

`type Name = T;` names a type: `Name` and `T` are interchangeable everywhere, and the alias
never appears in a diagnostic where `T` serves. An alias must not expand through itself
(`LYR-SEM0064`).

`opaque type Name = T;` creates a new **identity** over the same layout:

- nothing converts implicitly in either direction (`LYR-SEM0001` names the types);
- the explicit `as` to exactly `T` and back is the only crossing (§3.6); two opaque aliases of
  the same underlying do not cast sideways;
- **making one is the declaring module's privilege** (since 3.8): the INWARD cast,
  `value as Name`, warns outside the module that declares `Name` (`LYR-SEM0093`), and 4.0
  refuses it — a handle is issued, not assembled, and a value that must be rebuilt from a
  stored number takes a constructor function the declaring module offers. The OUTWARD cast
  stays free everywhere: reading the number breaks no promise the alias makes;
- `==`/`!=` compare two values of the SAME opaque alias by their underlying; every other
  operator, ordering included, is refused (`LYR-SEM0003`);
- an opaque alias satisfies no constraint, not even one its underlying satisfies;
- an f-string does not render it (`LYR-SEM0006`);
- at runtime the value IS its underlying: the cast is free, and in a native signature the
  alias resolves to the underlying — a host sees the plain value. *(Through 3.7 any module
  that could see the alias could also forge a value with the inward cast, so the "a script
  cannot forge one" this bullet used to claim was only true of scripts that import nothing.
  The privilege rule above is the clock that closes it: a warning through 3.x, refused at
  4.0.)*

The last point is the reason the name has to be carried separately where it matters: a consumer
reading the shape of a compiled type sees the underlying and could not refuse a handle it must
refuse. A module therefore records the alias's NAME for the fields declared with it
(§13 OpaqueFields, format 3.5); this changes nothing about the type, and a consumer that ignores
it sees what it saw before.

## 3.6 Conversions: `as`

`as` is the only conversion construct, and it is total over exactly these cases:

1. **numeric ↔ numeric** — between any two of the numeric primitives (and `char`, which
   converts as its code point; a value outside the scalar range panics `LYR-VM0012` AT the
   cast). Narrowing between integers keeps the low bits (wrapping, §3.2); int → float rounds
   to nearest; float → int truncates toward zero and SATURATES at the target's bounds — an
   infinite or out-of-range value yields the nearest bound, and NaN yields 0. Never undefined,
   never a panic.
2. **opaque ↔ its underlying** — identity at runtime; the inward direction is the declaring
   module's privilege (§3.5: `LYR-SEM0093` outside it since 3.8, refused at 4.0).
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

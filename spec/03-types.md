# Types and values

> **Partly written.** §1 and §2 were written with milestone **M3** of the Lyric 5 plan (slices S1
> and S2); the rest follows with the slices of M3, spec-first: each rule lands here with its conformance case before
> or with its implementation. Source of the decisions:
> [02 Value model](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/02-wertmodell.md), [03 Type system](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md).

## Scope

Scalars and their aliases, widening and coercions, overflow, `as`, structs and classes, mutability, optionals, arrays, `Slice<T>`, `StringView`, ranges, tuples, enums, generics by monomorphization.

## 1. Scalars

The number tower, `bool` and `char`
([03 T1, T2](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)).

**Conformance.** `conformance/cases/03-types/`.

### 1.1 The scalar types

1. The integer types are `int8`, `int16`, `int32`, `int` (signed, two's complement) and
   `uint8`, `uint16`, `uint32`, `uint` (unsigned), of the width their name says; `int` and
   `uint` are 64 bits wide. The float types are `float32` and `float`, IEEE 754 binary32 and
   binary64. `bool` holds `true` and `false`. `char` holds one Unicode scalar value.
2. `int64`, `uint64` and `float64` are **aliases** of `int`, `uint` and `float`: the same type
   under a second name, not a distinct type. A diagnostic names the type as `int`, `uint`,
   `float`.
3. There is no `usize`: at the C boundary `size_t` is `uint` ([13](13-abi.md)).

### 1.2 Literals

1. An unsuffixed integer literal takes the integer type its position expects — an
   initializer with a written type, an argument, a return, an operand beside a typed operand;
   without one it is `int`. An unsuffixed float literal likewise takes the float type its
   position expects, `float` otherwise.
2. A literal that does not fit its type is an error, not a wrapped value: `let x: uint8 = 300`
   is refused, and so is `-129` as an `int8`.
3. An integer literal takes a float type only when the float holds its value exactly:
   `let f: float = 9007199254740993` (2⁵³ + 1) is an error, never a silent rounding.
4. An integer literal never takes `char`: `let c: char = 65` is an error. A `char` is written
   as a character literal, or reached through `uint32` (§1.4).

### 1.3 Widening

1. At a **coercion site** — an initializer with a written type, an assignment, an argument, a
   return, an arm under a written context type — an integer value stands where a wider integer
   type is expected when the wider type's range contains the narrower one's: `int8 → int16 →
   int32 → int`, `uint8 → uint16 → uint32 → uint`, and an unsigned type into every signed type
   of greater width (`uint8 → int16`, `uint16 → int32`, `uint32 → int`). `float32` stands
   where `float` is expected. The value is converted; nothing else changes.
2. Nothing else is implicit: no narrowing, no signed into unsigned, no `uint` into `int`, no
   integer into a float (`let f: float = n` with `n: int` is an error: an integer stays an
   integer), no float into an integer, no `float` into `float32`, nothing into or out of `char`
   or `bool`.
3. Widening happens at coercion sites only, never inside an expression: the operands of an
   operator have one type, and `a + b` with `a: int8` and `b: int` is an error. Arms of an
   `if` or `match` without a context type unify exactly. Coercion follows the inference, it
   does not take part in it ([03 T8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)).

### 1.4 `as`

1. `x as T` converts between any two number types and always succeeds:
   - integer to integer: the value modulo 2ᵂ of the target width, reinterpreted in the
     target's signedness (`300 as uint8` is `44`, `-1 as uint8` is `255`, `128 as int8` is
     `-128`); a widening is exact;
   - integer to float: the nearest representable value, ties to even;
   - float to integer: toward zero; a value outside the target's range gives the nearest
     bound; NaN gives `0`;
   - float to float: IEEE rounding to nearest, ties to even.
2. `char` converts to `uint32` and from `uint32` and to no other type. `c as uint32` is the
   scalar value. `n as char` yields the character with that scalar value and **panics** with
   `LYR-RT0009` when `n` is a surrogate (`0xD800..0xDFFF`) or above `0x10FFFF`
   ([13 §1.4](13-abi.md)). A `char` meets `int` through `uint32`: `c as uint32 as int`.
3. `bool` converts to nothing and from nothing by `as`.
4. `as` is the one conversion operator. It never fails on numbers, so it never answers an
   optional; a checked narrowing is a method ([03 T1d](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md), form with the standard library).

### 1.5 `char` and `bool` are not numbers

1. `char` has no arithmetic and no bit operators, and does not compare with a number: `c + 1`,
   `-c`, `c << 1`, `c++`, `c < 98`, `c == 97` are errors. Two `char` values compare with `==`,
   `!=` and the four orderings, by scalar value.
2. `bool` has the logical operators and equality, and nothing of arithmetic.

### 1.6 Arithmetic and overflow

1. On integers, `+ - * / %` and unary `-` **panic on overflow** with `LYR-RT0002`, in every
   build profile: a result outside the type's range, an unsigned result below zero,
   `MIN / -1`, `MIN % -1`, `-MIN`. Division and remainder by zero panic with `LYR-RT0001`.
   `/` rounds toward zero and `%` takes the sign of the dividend, as C does.
2. `<<` and `>>` panic with `LYR-RT0002` when the count is negative or not below the width of
   the left operand's type. Otherwise bits shifted out are discarded, `>>` on a signed type
   is arithmetic (the sign is kept) and on an unsigned type logical. Both operands have the
   operator's type, as for every binary operator.
3. The **wrap operators** `+%`, `-%`, `*%` (and the compounds `+%=`, `-%=`, `*%=`) compute the
   result modulo 2ᵂ of the type's width and never panic. They bind like `+`, `-` and `*`. They
   are defined on integer types only: a float or a `char` operand is an error
   ([08 Y4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)).
4. `& | ^ ~ << >>` and the wrap operators take integers; the arithmetic operators take
   integers and floats.
5. On floats, `+ - * / %` and unary `-` are the IEEE 754 operations in round-to-nearest-even:
   there is no overflow and no division fault — `1.0 / 0.0` is `inf`, `0.0 / 0.0` is `NaN` —
   and `%` is the remainder of the truncated division (`fmod`), `3.0 % 2.5` is `0.5`. An
   implementation computes each operation as written: no contraction of `a * b + c` into a
   fused multiply-add, no reassociation, no fast-math, unless a build asks for it explicitly
   ([01 L10](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)).
   The same program computes the same bits on every Tier 1 target.
6. A profile that removes the overflow checks does not exist in 5.0. An implementation may
   offer one as an explicit option; it never is the default of any profile.

### 1.7 The text of a number

What an f-string hole and the converters of `std.string` write ([12 §1](12-stdlib.md)):

1. An integer is its decimal digits, with a leading `-` when negative.
2. A float is the **shortest** decimal text that reads back as the same value: `0.1`, `1`
   (an integral value carries no fraction), `-0`, `0.30000000000000004`, `1e+21`, `1e-07`;
   `inf`, `-inf` and `NaN` for the values that are no number. A `float32` is written as the
   `float` it widens to: `0.1` as a `float32` prints `0.10000000149011612`.
3. `bool` is `true` or `false`; `char` is the character itself, UTF-8 encoded.

## 2. Structs and classes

Two forms of a composite type, chosen once at the type
([02 M1–M5, M9, M10, M14](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/02-wertmodell.md)).

**Conformance.** `conformance/cases/03-types/`.

### 2.1 Values and references

1. A `struct` is a **value**: it is stored where it is declared — in a local, inline in the
   object or the struct that holds it — and a binding, an assignment, an argument and a return
   **copy** it. A copy is shallow: a reference held in a field is copied as a reference.
2. A `class` is an **object** reached through a **reference**: a binding, an assignment, an
   argument and a return pass the reference, and every holder sees the one object.
3. A struct has no identity. A class has: two references are the same object or they are not
   (§2.5).

### 2.2 Fields and places

1. A field is **fixed** once the value holding it is built, unless it is declared `var`:
   `var balance: int`. The rule is one for structs and classes.
2. An assignment, a compound assignment, `++` and `--` write a **place**. A field `a.f` is a
   place that may be written when `f` is declared `var` **and** `a` may be changed in place:
   - a local is a place when it is bound with `var`; a `let` freezes a struct to the bottom —
     no field of it, and no field of a struct it holds, is written through it;
   - a **parameter is a `let`**;
   - a **reference starts the chain anew**: when `a` is of a class type, the object is the
     place, whatever the binding or the field that holds the reference says — `let c: C` does
     not keep `c.count = 1` from writing the object, and neither does a fixed field of class
     type on the way;
   - an element of an array is a place in the array, whatever holds the array;
   - `this` is a place inside a `mut fn` and nowhere else (§2.3).
3. A **temporary** is not a place: the result of a call that answers a struct cannot be
   written into, and no `mut fn` can be called on it. The program is refused; the value is
   never copied in silence so that the write has somewhere to go. A call that answers a class
   answers a reference, and that is a place.
4. Writing what is not a place is `LYR-SEM0019`; the diagnostic says which part of the chain
   refuses: the field without `var`, the `let` or the parameter at the root, the method
   without `mut`, the temporary.

### 2.3 Methods and `mut fn`

1. In a method of a struct, `this` **is the caller's value**, not a copy of it: what a method
   writes through `this`, the caller sees, and a write that happened before a panic stays.
2. A method that writes `this` — a field of it, `this` as a whole, or by calling a `mut fn`
   on it — is declared **`mut fn`**, on a class as on a struct. A method without the word that
   does so is refused (`LYR-SEM0019`).
3. A `mut fn` is called on a place (§2.2): on a struct bound with `let`, on a parameter of a
   struct type and on a temporary the call is refused. On a class it is called through any
   reference.
4. `this = value` in a `mut fn` of a struct replaces the caller's value as a whole. The
   `this` of a class method is the reference the caller holds and is never replaced.
5. A `mut fn` of a struct has something to write: the struct has a `var` field, or the method
   replaces `this`, or it calls a `mut fn` on `this`, or an interface of the struct declares
   the method `mut`. Otherwise the declaration is refused (`LYR-SEM0023`).

### 2.4 Construction

1. The **initializer** `T { field = value, … }` builds a value of a struct or a class. Every
   field without a default is given; one diagnostic names all that are missing
   (`LYR-SEM0106`). The written values are evaluated in the order they are written, then the
   defaults of the omitted fields in the order of their declaration. A default does not see
   `this`.
2. A field of an optional type `?T` has the default `null` without saying so.
3. There are **no constructors**. A type name in call position, `T(args)`, is the call
   `T.new(args)` of the type's `static fn new` — an ordinary static function, which may
   validate, answer any type, and hand out an object that exists already. A type that declares
   no `static fn new` is not callable (`LYR-SEM0013`).

### 2.5 Identity and equality

1. `same(a, b)` answers whether two references are one object. Both arguments are references
   — class values, arrays, coroutines — of one type. On a value it is an error
   (`LYR-SEM0003`), not `false`: a struct has no identity to ask about.
2. `==` and `!=` mean value equality and nothing else ([05](05-interfaces.md)): a class
   without it has no `==`, and never falls back to identity.

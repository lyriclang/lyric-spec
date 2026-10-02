# Types and values

> **Partly written.** §1 to §8 were written with milestone **M3** of the Lyric 5 plan (slices S1
> to S7); the rest follows with the slices of M3, spec-first: each rule lands here with its conformance case before
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

### 2.5 `with`

1. **`p with { x = 3, y = 4 }`** is a **copy** of the struct `p` with the named fields
   replaced, of `p`'s type; `p` is unchanged. It is the way to change a fixed field: no
   `var` is needed, since nothing is written in place
   ([02 M6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/02-wertmodell.md)).
2. The values are evaluated left to right and see the **old** `p`: `p with { x = p.y, y = p.x }`
   swaps. A field named twice (`LYR-SEM0070`) and a field the type does not have
   (`LYR-SEM0015`) are refused.
3. A **path** reaches into a struct the value holds by value: `line with { to.x = 9 }` is
   `line with { to = line.to with { x = 9 } }`. Every segment but the last names a struct
   (`LYR-SEM0116`).
4. `with` stands on a **struct** only: on a class — an object is changed in place, or cloned
   ([05](05-interfaces.md)) — and on a tuple, which has no field names, it is refused
   (`LYR-SEM0116`).
5. `with` is a postfix: `p with { x = 1 }.x` reads the copy's `x`, and `q + p with { … }` is
   `q + (p with { … })`. As a statement it has no effect and is refused like any other value
   (`LYR-SEM0022`).

### 2.6 Identity and equality

1. `same(a, b)` answers whether two references are one object. Both arguments are references
   — class values, arrays, coroutines — of one type. On a value it is an error
   (`LYR-SEM0003`), not `false`: a struct has no identity to ask about.
2. `==` and `!=` mean value equality and nothing else ([05](05-interfaces.md)): a class
   without it has no `==`, and never falls back to identity.

## 3. Optionals

A value or nothing ([03 T4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md),
[01 V5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)).

**Conformance.** `conformance/cases/03-types/`.

### 3.1 The type

1. `?T` holds a value of `T` or nothing, written `null`. `T` is any type, an optional included:
   `??T` is a type, and its three states are distinct — nothing, a `?T` that is `null`, a `?T`
   that holds a value. Levels do not collapse: a generic `?T` at `T = ?int` is `??int`.
2. At a coercion site ([§1.3](#13-widening)) a value stands where an optional of its type is
   expected, and is wrapped once for every level the expected type has more: an `int` where
   `??int` is expected is a present `?int` that holds the value; a `?int` there is a present
   `??int` whatever it holds. `null` is the absence at the **outermost** level of the type
   expected.
3. There is no implicit way down: a `?T` does not stand where a `T` is expected, nor a `??T`
   where a `?T` is. The ways down are a test (§3.2), `??` and `!` (§3.3).
4. *(Informative.)* An optional of a class value or of a string occupies the one word of the
   reference, null when there is no value. Any other optional holds its value and a flag.

### 3.2 Tests and narrowing

1. `x == null` and `x != null` ask whether the outermost level of `x` holds a value. They are
   asked of an optional only: on a type that is never `null` the test is refused
   (`LYR-SEM0059`).
2. A **bare type parameter is opaque**: on an expression of type `T` there is no `== null`,
   no `??`, no `??=`, no `!` and no `null` pattern, whatever an instantiation binds `T` to. The
   body of a generic is checked at its declaration; it asks these of a `?T`.
3. Where a test has proven a name present, the name has the type **one level down**: inside
   the `then` of `if (x != null)`, in the body of `while (x != null)`, on the right of
   `x != null &&`, after `if (x == null) { return …; }` and the other forms that leave. A
   second test narrows again: a `??int` proven present is a `?int`, and proven present once
   more an `int`.
4. Narrowing belongs to the binding. An assignment to a `var` ends it: from there on the name
   has its declared type again.
5. `if (let v = e)` and `while (let v = e)` bind `v` to the value of the optional `e` when
   there is one, one level down, and take the branch only then.
6. A narrowed name is the value where it lies, not a copy of it: through a narrowed `var` of
   type `?S`, with `S` a struct, a `var` field of the struct is written in place
   ([§2.2](#22-fields-and-places)).
7. **Equality.** `a == b` on two `?T` is true when both hold nothing, or both hold a value and
   the values are equal through `T`'s own equality ([05 §12](05-interfaces.md) rule 5 — the
   scalars natively); `!=` is its negation. A `T` on one side coerces up to `?T` (§3.1): `x == 5`
   with `x: ?int` asks whether `x` holds a 5. A `T` without `Equatable` gives its optional no
   equality (`LYR-SEM0059`). There is **no ordering** on an optional: `<` and its siblings are
   refused (`LYR-SEM0003`), and `null` orders with nothing.

### 3.3 `??`, `!` and `?.`

1. `a ?? b` is the value of `a` when it holds one, **one level down**, and `b` otherwise. `b`
   is evaluated only when `a` holds nothing. The operator is right-associative. On a left side
   that is never `null` it is refused (`LYR-SEM0005`).
2. `a ??= b` assigns `b` to `a` when `a` holds nothing, and evaluates `b` only then.
3. `x!` is the value of `x`, one level down, and **panics** with `LYR-RT0004` when `x` holds
   nothing ([13 §1.4](13-abi.md)). On a type that is never `null` it is refused
   (`LYR-SEM0005`).
4. `a?.m` reads the member `m` of the value of `a` when there is one, and is `null` otherwise.
   Chains **flatten**: the result is an optional of the member's type, and when the member's
   type is itself an optional, it is that type — `a?.b?.c` can be absent in one way only and
   is a `?C`, not a `??C`. `a?.f(args)` calls the method under the same rule and evaluates the
   arguments only when `a` holds a value.
5. Nothing is assigned through `?.`: `a?.f = v` is refused (`LYR-SEM0019`). Narrow first.

## 4. Enums

One of several variants, each with a payload or none
([01 V5, V6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[02 M13](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/02-wertmodell.md),
[03 T9](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)).

**Conformance.** `conformance/cases/03-types/`.

### 4.1 Variants and payloads

1. An `enum` declares its **variants**, each of which is a **unit** variant (`Red`), a
   **tuple** variant with positional payload (`Num(int)`, `Tagged(string, Point)`) or a
   **struct** variant with named fields (`Rect { w: int, h: int }`). One enum may mix the
   three forms. After the variants, separated by `;`, an enum declares methods, `mut fn`
   included, as a struct does ([§2.3](#23-methods-and-mut-fn)).
2. A value of the enum is exactly one variant with that variant's payload. A unit variant is
   written by its name, `Signal.Red`; a tuple variant is called, `Shape.Num(3)`; a struct
   variant is built with the initializer, `Shape.Rect { w = 1, h = 2 }`, under the rules of
   [§2.4](#24-construction). A variant is not a type: `Num` names no type, and a payload is
   read by a pattern ([09](09-patterns.md)) and in no other way.
3. An enum is a **value** ([§2.1](#21-values-and-references)): stored inline, copied by a
   binding, an assignment, an argument and a return, without identity. `this` in a method is
   the caller's value; a `mut fn` replaces it whole with `this = value`
   ([§2.3](#23-methods-and-mut-fn)), which is how a method moves a value to another variant.
4. A value type cannot hold itself: an enum whose payload holds the enum by value — directly,
   through a struct, a tuple or an optional — is refused (`LYR-SEM0056`); the diagnostic
   names the cycle. A recursive payload lies behind a reference: `Box<T>` of `std.core`, a
   class of one's own, or an array. `enum Tree { Leaf(int), Node(Box<Tree>, Box<Tree>) }`.
5. *(Informative.)* An enum occupies a tag and the union of its payloads, inline. An optional
   of an enum is the enum with a tag no variant has ([§3.1](#31-the-type)).

### 4.2 The enum the position names

1. **`.Red`** is the member `Red` of the enum the position expects, the enum unnamed: a unit
   variant as it stands, the callee of `.Num(3)`, the head of `.Rect { w = 1, h = 2 }`. The
   position expects an enum where a value of one is required: an initializer with a written
   type, an assignment, an argument, a return, an arm under a context type, a field of an
   initializer, a default, and either side of `==` and `!=` when the other side has the enum
   type. An expected `?E` names `E`: `let o: ?Signal = .Green` is a present optional.
2. Where the position expects no particular type, or a type that is not an enum, the form is
   refused (`LYR-SEM0113`), and the diagnostic says to name the enum. The qualified form
   `Signal.Red` stands everywhere, whatever the position expects.
3. In a pattern the same form tests the variant ([09 §2](09-patterns.md)); a bare name never
   does.

## 5. Arrays, views and inline arrays

Elements in a row: behind a reference, through a view, or as a value
([01 V10](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[03 T13, T14](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md),
[10 C2, C7, N8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)).

**Conformance.** `conformance/cases/03-types/`.

### 5.1 `T[]`

1. `T[]` is an **object** of a fixed length holding its elements inline and contiguous — a
   struct element lies in the array, not behind it — reached through a **reference**
   ([§2.1](#21-values-and-references)): a binding, an assignment, an argument and a return share
   the one array. The length is a property of the value, not of the type.
2. `[a, b, c]` builds an array of its elements; `[]` takes its element type from the position.
   `[x] * n` builds an array of `n` elements each a copy of `x` — a value copied, a string
   shared — and panics with `LYR-RT0007` when `n` is negative; `xs * n` is the only order.
   `xs + ys` builds a new array of the elements of both ([10 C7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md)).
   An element that is or holds an object — a class, an array, a view, a function value, an
   interface value, directly or inside a struct, an enum, a tuple, an optional or an inline
   array — is repeated by **`clone`** ([05 §14](05-interfaces.md)), never shared into every slot:
   its type conforms to `Clone`, or the repetition is refused with `arrayOf` as the way out
   (`LYR-SEM0136`). A string is shared; nobody can tell.
3. `xs.length()` is the length, a **call** with its parentheses like every length in the
   language ([10 N8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/10-stdlib.md));
   the bare name is refused (`LYR-SEM0012`). The length and the index are the two primitives of
   an array; every other member is written in the standard library.
4. `xs[i]` is the element at `i`. The index is an **`int`**: a narrower integer widens to it as
   at any coercion site ([§1.3](#13-widening)), a `uint` or a `uint64` is converted with
   `as`, nothing else stands there (`LYR-SEM0007`). An index outside `0 ≤ i < length()`
   **panics** with `LYR-RT0003`, in every profile — a negative index like any other; there is
   no counting from the end by sign. An element is a place in the array, whatever holds the
   array ([§2.2](#22-fields-and-places)): `xs[i] = v` and `xs[i].f = v` write the array
   through a `let` as through a `var`.
5. **`^n`** inside the brackets counts from the end: `xs[^1]` is the last element, `xs[^n]`
   stands for `xs[xs.length() - n]` with `xs` evaluated once. It is sugar for that
   subtraction and nothing more — no type, no value of its own: outside `[…]`, or as a part
   of a larger index expression, it is refused (`LYR-SEM0114`). `^0` as an index panics as
   `length()` does; as the end of a range (§5.2) it is the length.

### 5.2 `Slice<T>`

1. `Slice<T>` is a **view** of the elements of an array — a pointer into them and a length,
   a value of two words that is copied by a binding and **shares the elements**: what is
   written through a view is written in the array, and what is written in the array is seen
   through every view of it. `Slice` is a primitive of `std.core`, visible without an import.
2. `xs[a..b]` is the view of the elements from `a` up to but not including `b`; `xs[a..=b]`
   includes `b`; `xs[..b]`, `xs[a..]` and `xs[..]` leave the start, the end or both open.
   The bounds are indices as in §5.1, `^n` among them, and satisfy `0 ≤ a ≤ b ≤ length()`
   or the expression **panics** with `LYR-RT0003`, in every profile; `xs[n..n]` is the empty
   view, `xs[length()..]` too.
3. A view is indexed, measured and counted from the end as the array is (§5.1), its elements
   are places in the array, `v[a..b]` is a view of the same array, and an array pattern
   matches it ([09 §2](09-patterns.md)).
4. At a coercion site an array stands where a view of its element type is expected and gives a
   view of itself, whole; a view never stands where an array is expected (`LYR-SEM0001`).
5. There is no lifetime: the array lives as long as any view of it does, and a view kept in an
   object or returned from a function is as good as one in a local ([01 L1](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)).
6. `StringView`, the view of a string's bytes, is written with the strings ([12](12-stdlib.md)).

### 5.3 `T[N]`

1. `T[N]` is a **value** of exactly `N` elements, `N` a positive decimal literal, laid out
   inline where it lies — in a local, in a struct, in an object, in an element of an array —
   with the size and the identity of a struct ([§2.1](#21-values-and-references)): a binding,
   an assignment, an argument and a return **copy** it. The length is part of the type:
   `int[3]` and `int[4]` are two types, and neither stands for `int[]` nor `int[]` for
   them. `T[N][M]` is an inline array of inline arrays; `T[N][]` is an array of inline arrays.
2. It is built from a literal of exactly `N` elements, or from `[x] * N` with the literal
   count `N`, where a `T[N]` is expected; another length is refused (`LYR-SEM0001`).
3. It is indexed, measured and counted from the end as an array is (§5.1), with the same
   check. An element is a place when the array is one — a `var` local, a `var` field of a
   place, an element of an array — as a field of a struct is ([§2.2](#22-fields-and-places));
   a `let` freezes it (`LYR-SEM0019`).
4. A view of an inline array (§5.2) is taken where the array lies in the **heap** — a field of
   an object, an element of an array or of a view, a struct inside those — never of a local,
   a parameter, or a field of a struct local, whose frame may end before the view
   (`LYR-SEM0115`); such an array is copied or passed whole. A value type cannot hold itself
   through an inline array ([§4.1](#41-variants-and-payloads)).
5. An array pattern of the one length covers the type ([09 §3](09-patterns.md)).

## 6. Tuples

Positional elements in one value
([03 T16](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md),
[01 V11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)).

**Conformance.** `conformance/cases/03-types/`.

1. `(A, B)` and on, from two elements — there is no tuple of one and no empty tuple (`void`
   stays what it is) — is a **value** of positional elements laid out inline where it lies,
   copied like a struct ([§2.1](#21-values-and-references)); it has no identity. `(1, "a")`
   builds one. Its elements are not written; the tuple is replaced whole.
2. `t.0`, `t.1`, … read the elements by position; a position the tuple does not have is refused
   (`LYR-SEM0012`).
3. A written type may **label** its elements: `(x: int, y: int)`, and `p.x` reads `p.0`. A
   label is a name for the reader and no part of the type: `(x: int, y: int)` and `(int, int)`
   are **one type**, a value of either stands where the other is expected, and the label is
   seen through the type of the binding it was written on, not through another's. A label
   twice in one type is refused.
4. A tuple is taken apart by a pattern ([09 §2](09-patterns.md)) and by `let (a, b) = t;`.
   Equality, hashing and display come with the interfaces ([05](05-interfaces.md)).

## 7. Ranges

The values `a..b` and `a..=b`
([03 T13 A3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)).

**Conformance.** `conformance/cases/03-types/`.

1. `a..b` is a value of `Range<T>` and `a..=b` of `RangeInclusive<T>`, structs of `std.core`
   holding their bounds as `start` and `end`; `T` is the bounds' one type, a number type. The
   open forms `a..`, `..b` and `..` are the structs `RangeFrom<T>`, `RangeTo<T>` and
   `RangeFull` and are written inside `[…]` only, where they take a view ([§5.2](#52-slicet)).
2. In a **`for` head**, `for (i in a..b)` and `for (i in a..=b)` with the range written there
   are the counted loop: no value is built, and `for (i in ..b)` is refused. A range held in
   a binding is walked as an `Iterator` ([05](05-interfaces.md)).
3. A range is an ordinary value everywhere else: bound, stored in a field or an array, passed
   and returned. A range is not an integer (`LYR-SEM0001`).

## 8. Function values

Functions as values, and the lambdas that make them
([03 T17](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md),
[01 V8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[02 M8](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/02-wertmodell.md),
[08 Y11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)).

**Conformance.** `conformance/cases/03-types/`.

### 8.1 The type

1. `fn(A, B) -> R` is the type of a function value taking `A` and `B` and answering `R`;
   `fn() -> void` takes nothing and answers nothing; `fn(A) -> R throws E` may throw, its set part
   of the type ([06 §8](06-errors.md#8-function-values-that-throw)). A free function, a lambda and
   a method bound to its object are values of it alike (V8): what a value of the type is made of is
   not observable. The type has no variance: `fn(int) -> int` and `fn(int8) -> int` are two types.
   That a value throwing less fits a type throwing more is a coercion of its own (06 §8 rule 3), not
   a variance.
2. A value of a function type is **called** with `f(a, b)`; it is copied by a binding, held in
   a field, an array or an optional, passed and returned. Two function values are not compared.
3. *(Informative.)* A function value is a pointer to the code and the environment it runs in,
   two words; a function without an environment costs no allocation.

### 8.2 Lambdas

1. A lambda is written in **three forms** (Y11 F1): parenthesized, `(n: int): int => n + 1`,
   with the types and the return type as written or, when the position expects a function
   type, taken from it (F11); bare, `x => x * 3`, one parameter, its type from the position;
   trailing, `xs.map { it * 2 }` — a block after a call's parentheses, or after the callee
   alone, is the call's **last argument**, its one parameter the implicit `it`, or none when
   the position expects a function of none.
2. A trailing block may name its parameters before `=>`: `fold(xs, 0) { acc, x => acc + x }`,
   `{ (k, v) => v }` with a pattern (F2). The body is then the rest of the block.
3. The body is an expression or a block; a block's last expression without `;` is its value
   (F3). `return` leaves the lambda, never the enclosing function; `break` and `continue`
   belong to loops inside the lambda (F5).
4. Without a position that expects a function type, the parameters of a bare or trailing
   lambda have no type and are refused (`LYR-SEM0045`); the parenthesized form writes them.

### 8.3 Captures

1. A lambda uses the bindings of the scopes around it. A captured **`let`** — a parameter
   included — lies in the closure as a **copy** taken when the lambda is made, which nothing
   can tell from the original since it cannot change; a captured **`var`** lies in a **box**
   the closure and the enclosing scope share, from its declaration on: what either side writes,
   the other reads (M8).
2. A loop binding is fresh per pass: the closures of `for (i in 0..3) { fs = fs + [() => i]; }`
   answer 0, 1 and 2 (M8 C1).
3. `this` of a class is captured as the shared reference; `this` of a struct as a copy of the
   value (M8 C2).

### 8.4 Functions and methods as values

1. A **free function** named without a call is a value of its type; a **static function**
   named through its type, `Point.new`, likewise (F10). A generic function is not a value
   until instantiated ([§9.4](#94-instantiated-functions-as-values)).
2. `obj.method` without a call is a closure **bound** to `obj` (F10): it holds the object — a
   class shared, a struct copied at the binding — and calls the method on it; its type is the
   method's without the receiver. It is called like any function value, and a call through it
   on a struct's copy changes the copy.
3. `arrayOf(n, f)` of `std.core` builds an array of `n` elements, the element at `i` the value
   of `f(i)` — fresh elements each, where `[x] * n` copies one ([§5.1](#51-t)).

## 9. Generics

Type parameters, their inference, and what an instance is
([03 T5–T8, T17, T18](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md),
[01 C3](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md)).

**Conformance.** `conformance/cases/03-types/`.

### 9.1 Type parameters and instances

1. A function, a struct, a class, an enum and an interface may declare **type parameters**,
   `fn ident<T>(x: T): T`, `struct Pair<A, B> { … }`; a parameter may carry **constraints**,
   `<T :: [Show, Eq<T>]>`, the interfaces an argument must satisfy ([05](05-interfaces.md)).
   Inside the declaration a value of type `T` has the members its constraints give it and no
   others (T18): the body is checked once, at the declaration, not per instance.
2. An **instance** names the arguments: `Pair<int, string>`, `ident<int>`. Two argument lists
   that differ are two types with no relation between them (T3): nothing coerces
   `Pair<int, string>` to `Pair<int8, string>`, and a `T[]` at `T = int8` is an `int8[]`, laid
   out as one.
3. The number of arguments is the number of parameters (`LYR-SEM0026`); an argument that does
   not satisfy its parameter's constraints is refused (`LYR-SEM0028`), written or inferred
   alike.
4. *(Informative.)* Every instance is compiled as code of its own — **monomorphization** —
   with `T` replaced throughout: an `int8` field takes one byte, a call on a `T` is a direct
   call. The compiler collects the instances of a program and compiles each once (C3).
5. A type parameter may carry a **default** (T18): `interface Add<Rhs = Self> { … }`,
   `class Map<K, V, H = DefaultHasher>`. A use that writes fewer arguments takes the defaults
   for the trailing ones, resolved where the type is declared — `Self` there is the conforming
   type, so `Vec2 :: [Add]` is `Vec2 :: [Add<Vec2>]`, and the constraint `T :: [Add]` is
   satisfied by either spelling.
6. A constraint may fix an **associated type** of its interface, `T :: [Iterator<Item = int>]`,
   and the declaration names one as a type path, `T.Item` ([05 §8](05-interfaces.md#8-associated-types)).
7. A type parameter may stand for **`void`** — a lambda that returns nothing binds it so,
   `run(() => { println("x"); })`. A value of type `void` is nothing: a parameter, a local, a
   field or an element of that type holds nothing, a `?void` holds only whether one was given,
   and a call of a function that returns nothing gives that value wherever one is expected —
   passed, stored, wrapped, returned. *(Informative: such a place costs one byte.)*

### 9.2 Inference at a call

1. A call of a generic function may **omit** the type arguments: `ident(3)` is `ident<int>(3)`.
   Each argument's type binds the parameters that occur in the parameter type it is passed
   to, at any depth — `firstOf([1, 2])` binds `T = int` through `T[]` — and a lambda's type
   binds through `fn(T) -> U` once its own parameters are known from the position.
2. What the arguments leave open, the **expected type** of the call's position binds (T8):
   `let xs: int[] = empty();`, `return empty();`, `count(empty())`. The arguments bind first
   and the position never overrides them: `let xs: int[] = ident("x");` is the assignment's
   error, not a different instance.
3. A parameter that occurs in no argument and not in the expected type is not inferred:
   `let xs = empty();` is refused (`LYR-SEM0060`), with the instruction to write it.
4. Type arguments may be **written**, `empty<int>()`; written ones bind before any argument,
   and an argument that does not fit them is the argument's error, `ident<int>("x")`. A
   **placeholder** `_` stands for one argument the inference fills (T8): `collect<_, string>(1, f)`
   writes `U` and infers `T`. A placeholder nothing determines is refused as in rule 3.
5. `_` stands only in a list of type arguments — of a call, of an initializer ([§9.3](#93-generic-types-in-an-initializer)),
   of an instantiated function ([§9.4](#94-instantiated-functions-as-values)). Anywhere else,
   `let p: Pair<_, int> = …` included, it is refused (`LYR-SEM0117`).

### 9.3 Generic types in an initializer

1. An initializer of a generic type takes its arguments from what is **written**,
   `Pair<int, string> { first = 1, second = "x" }`, else from the **context** — a binding with
   a type, an argument, a return, a field — `let p: Pair<int, string> = Pair { first = 1, second = "x" };`.
   Without either it is refused (`LYR-SEM0026`): the field values alone do not choose an
   instance.
2. A written list may hold placeholders: `Pair<_, string> { first = 3, second = "x" }`. A
   placeholder is filled from the context when the position names an instance, else from the
   **field values**, each checked with as much of its field's type as is known; a value that
   fixes no type of its own (`[]`, `null`) fills nothing (`LYR-SEM0060`).

### 9.4 Instantiated functions as values

1. A generic function with its arguments written, `ident<int>`, is a **value** of the
   instance's type, `fn(int) -> int` (T17): held, passed and called like any function value
   ([§8](#8-function-values)). A static method through its type likewise, `Counter.make<bool>`;
   an instance method through its type is no value (`LYR-SEM0055`) — it becomes one through
   its object, `obj.method` ([§8.4](#84-functions-and-methods-as-values)).
2. A placeholder in the list is filled from the **function type the position expects**:
   `let s: fn(string) -> string = ident<_>;`, `apply(ident<_>, 4)` with `apply(f: fn(int) -> int, …)`.
   Where the position expects no function type, or one still holding an open parameter of
   its own, the argument is written.
3. The bare name of a generic function is no value (`LYR-SEM0052`): a function value is
   monomorphic.
4. The arguments of the value form follow [§9.1](#91-type-parameters-and-instances) rule 3 —
   their number, also for a function that is not generic (`plain<int>`), and their
   constraints.

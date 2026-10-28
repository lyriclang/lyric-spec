# 3. Types

**Base.** Lyric 5.0 [§3](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/03-types.md) applies, with the deviations below.

**Status.** The core (S2), the optionals, `var x = null`, tuples, enums with payloads, function
values and generics (S3) written; the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

## Written (S2, the core)

1. **Scalars.** `int` is 64 bits, `float` 64 bits; `bool` and `char` are Lyric 5's. A width type
   of Lyric 5 — `int8` … `int64`, `uint`, `uint8` … `uint64`, `float32`, `float64` — is refused
   where it is named (`LYS-SEM0900`) ([03 K3](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
2. **Widening.** An `int` value where a `float` is taken — a binding, an argument, a field, a
   return, a branch of an `if` beside a `float` one — is widened; nothing narrows on its own
   (`LYS-SEM0001`) ([03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
3. **Structs and classes.** A struct's fields are never written: an assignment to one is refused
   (`LYS-SEM0019`), and so is `var` on one (`LYS-SEM0901`). A class is the mutable reference: its
   `var` fields are written by any code that holds it, its methods without `mut fn` (§7).
4. **Omitted return types** (Kotlin's rule, [09 Ret](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)): `fn f(…) = e`
   has the type of `e`; a block body without a written type is `void`. A function whose type
   depends on itself through its own body is refused until the type is written (`LYS-SEM0010`).
5. A code means what Lyric 5's `LYR-SEM` code of the same number means; Lyric-Script's own
   codes start at 0900 (§16). `LYS-NYI0001` names a form a later milestone of the
   plan builds; it leaves the toolchain before 1.0.

## Written (S3)

6. **Optionals.** Lyric 5 §3.1–3.3 apply as written: `?T` and `??T`, `null`, `!` (on null the
   panic `LYS-RT0004`), `??`, `?.`, `??=`, `== null`, narrowing after a test and after a branch
   that never comes out, `if let`, `while let`. The codes are Lyric 5's: a null operator on a
   value that is never null is `LYS-SEM0005`, `== null` there `LYS-SEM0059`, an assignment
   through `?.` `LYS-SEM0019`.
7. **Narrowing ends at a write** (Lyric 5 §3.2). An assignment to a narrowed binding ends its
   narrowing; a loop that writes it has it narrowed in none of its turns. A module-level `var` is
   never narrowed — a script's top-level bindings are the module's (§7) — and a module-level
   `let` is narrowed like a local.
8. **`var x = null`** without a written type takes the type of the first use in its function
   — the script's code counting as one — that fixes one: an assignment or a `??=` of a value of
   type `T` (or `?T`), or the binding standing where a type `?T` is taken (an argument, a
   return, a typed binding, a field). `x` is then a `?T` from its declaration on, and every use
   is checked as such: uses before the fixing one in the source are allowed where they fix
   nothing (`x == null`) and checked against `?T`. Where nothing in the function fixes the type,
   the declaration is refused with the type to write (`LYS-SEM0010`); `let x = null` is refused
   so too, as in Lyric 5. Lyric 5 infers no binding from a later use ([03 Leer](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md));
   the empty literals `[]` and `[:]` take the same way with S7.
9. **Tuples.** Lyric 5 §6 rules 1–5 apply: `(A, B)` from two elements (`(1,)` is refused,
   `LYS-PAR0010`); labels `(x: A, y: B)`, no part of the type and seen through the type they
   were written on; `t.0` and `t.x` (`LYS-SEM0012` for an element the tuple lacks); elements
   never written (`LYS-SEM0019`); `let (a, b) = t` and `var (a, b) = t`, nested and with `_`
   (`LYS-SEM0058` where the pattern does not fit, `LYS-SEM0097` for a name twice); a literal
   takes the types an expected tuple gives its elements, and an element that gives no type of
   its own where none is expected is refused (`LYS-SEM0010`). Rule 6 — equality, hashing,
   display — comes with the synthesis (S3h), `for ((a, b) in …)` with the collections (S7).
10. **Enums with payloads.** Lyric 5 §4.1 rules 1–2 and §4.2 apply: tuple variants
   `Num(int)` and struct variants `Rect { w: int, h: int }` beside unit ones, built as
   `Shape.Num(3)`, `Shape.Rect { w = 1, h = 2 }` and `Shape.Empty`, a payload read by a pattern
   only; `.Red`, `.Num(3)` and `.Rect { … }` where the position expects the enum, else refused
   (`LYS-SEM0113`). Unlike Lyric 5 (§4.1 rules 3–4) an enum with a payload is a **reference** to
   an immutable value, as a struct is (rule 3): it holds itself without a box —
   `enum Tree { Leaf(int), Node(Tree, Tree) }`.
11. **Function values.** Lyric 5 §8.1–§8.4 and §8.6 apply, without `inline fn` (§8.5) and,
   until the errors come (S4), without `throws` in a function type: `fn(A, B) -> R`; lambdas in
   the three forms — `(n: int): int => n + 1`, `x => x * 3`, a trailing block with `it` or its
   parameters named before `=>` — their parameters' types written or from the position
   (`LYS-SEM0045`), a `return` in one whose result nothing gives refused (`LYS-SEM0010`); a free
   or static function named without a call, and `obj.method` bound to `obj`; a call through any
   value of a function type, a field's included (`LYS-SEM0013` on what is none); captures — a
   `let` copied, a `var` in a box both sides share, fresh in each pass of a loop (02 C1),
   `this` copied; a local `fn` that calls itself. Two function values are not compared
   (`LYS-SEM0059`). A brace after a name that is no type's opens a trailing block (§2 D4).
12. **Generics.** Lyric 5 §9.1 rules 1–3 and §9.2 rules 1, 3 apply to functions, structs,
   classes and enums: `fn f<T :: [C]>(…)`, `struct Pair<A, B> { … }`; a generic is checked once,
   a value of `T` has its constraints' members and no others (`LYS-SEM0012`); the arguments of a
   call bind the type parameters at any depth, a lambda's after the others, and what nothing
   binds is refused (`LYS-SEM0060`), as is an argument its constraints do not admit
   (`LYS-SEM0028`) and a wrong count (`LYS-SEM0026`). An initializer of a generic type binds its
   arguments from its fields' values or takes the instance the position expects; a unit variant
   of a generic enum takes it from the position. Type arguments may be written at a call,
   `none<int>()` (§9.2 rule 4): a `<` after a name or a member opens them where its matching `>`
   stands before `(`. A generic function as a value, `Self`, static and associated members come
   with the descriptors (S3i).
   Unlike Lyric 5 (§9.1 rule 4), an instance is not compiled per argument list: the types whose
   values are objects of the VM share one copy, whose constraint calls go through the value's
   table; every other type has a copy of its own (11 Gen).
13. *Informative.* The VM holds a `?T` of a reference type as the reference, `null` as none; any
   other `?T` as the slots of `T` and one presence slot after them; a tuple as its elements'
   slots in order, inline; an enum without payloads as an `int`, one with payloads as an object
   of a VM type per variant whose first scalar is the variant's number; a function value as an
   object whose first scalar names its function and whose fields hold its captures, called by
   `call.v`
   ([11 V2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)).

## Deviations (skeleton, written with later milestones)

- Scalars `int` (64-bit), `float` (64-bit), `bool`, `char`; no width family; `Bytes` and `BigInt` in `std`; `int` widens to `float` ([02 T1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- `struct` values are always immutable (`with`), `class` is the mutable reference; recursive structs need no `Box`; no `&T` ([02 T7](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- One sequence type `T[]` that grows (`List<T>` an alias), copying slices; no `Slice`; `StringView` an alias of `string` ([03 S, Str](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- No unions; optionals as in Lyric 5; literal protocols for every literal kind; empty literals typed by their first use in the function; Kotlin's rule for omitted return types ([02 T4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [09 Ret](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).
- Structs, enums and tuples are `Equatable`/`Hashable` without asking when their fields are; `{x}` falls back to `Debug`; `float` is `TotalOrder`; `Map`/`Set` iterate in insertion order ([03 Eq](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [05 Fl](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md), [01 S8](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).

**Conformance.** `conformance/cases/03-types/` (`since: 1.0.0`).

# 3. Types

**Base.** Lyric 5.0 [§3](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/03-types.md) applies, with the deviations below.

**Status.** The core (S2), the optionals and `var x = null` (S3) written; the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

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

## Written (S3, optionals and `var x = null`)

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
9. *Informative.* The VM holds a `?T` of a reference type as the reference, `null` as none; any
   other `?T` as the slots of `T` and one presence slot after them
   ([11 V2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)).

## Deviations (skeleton, written with later milestones)

- Scalars `int` (64-bit), `float` (64-bit), `bool`, `char`; no width family; `Bytes` and `BigInt` in `std`; `int` widens to `float` ([02 T1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- `struct` values are always immutable (`with`), `class` is the mutable reference; recursive structs need no `Box`; no `&T` ([02 T7](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- One sequence type `T[]` that grows (`List<T>` an alias), copying slices; no `Slice`; `StringView` an alias of `string` ([03 S, Str](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- No unions; optionals as in Lyric 5; literal protocols for every literal kind; empty literals typed by their first use in the function; Kotlin's rule for omitted return types ([02 T4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [09 Ret](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).
- Structs, enums and tuples are `Equatable`/`Hashable` without asking when their fields are; `{x}` falls back to `Debug`; `float` is `TotalOrder`; `Map`/`Set` iterate in insertion order ([03 Eq](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [05 Fl](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md), [01 S8](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).

**Conformance.** `conformance/cases/03-types/` (`since: 1.0.0`).

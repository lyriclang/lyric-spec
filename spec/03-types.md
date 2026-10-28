# 3. Types

**Base.** Lyric 5.0 [§3](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/03-types.md) applies, with the deviations below.

**Status.** Skeleton (S0). The rules are written with the milestone that builds them; until then the design documents decide.

## Deviations

- Scalars `int` (64-bit), `float` (64-bit), `bool`, `char`; no width family; `Bytes` and `BigInt` in `std`; `int` widens to `float` ([02 T1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- `struct` values are always immutable (`with`), `class` is the mutable reference; recursive structs need no `Box`; no `&T` ([02 T7](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- One sequence type `T[]` that grows (`List<T>` an alias), copying slices; no `Slice`; `StringView` an alias of `string` ([03 S, Str](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- No unions; optionals as in Lyric 5; literal protocols for every literal kind; empty literals typed by their first use in the function; Kotlin's rule for omitted return types ([02 T4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [09 Ret](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).
- Structs, enums and tuples are `Equatable`/`Hashable` without asking when their fields are; `{x}` falls back to `Debug`; `float` is `TotalOrder`; `Map`/`Set` iterate in insertion order ([03 Eq](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [05 Fl](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md), [01 S8](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).

**Conformance.** `conformance/cases/03-types/` (`since: 1.0.0`).

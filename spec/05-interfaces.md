# 5. Interfaces

**Base.** Lyric 5.0 [§5](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/05-interfaces.md) applies, with the deviations below.

**Status.** Written for what S3 builds: interfaces, their values, extends, delegation, `is`, sealed
interfaces, equality and the Debug form; `Self`, static members, associated types and generic
members with the descriptors (S3i), the family written in a list and the operator interfaces
with the prelude's interfaces (S7), the qualified call and members per interface (§3 rule 4,
§4) with the milestones that build them.

## Written (S3)

1. **Interfaces and conformance.** Lyric 5 §1 rules 1–3 apply: `interface I :: [P] { … }` with
   abstract members and defaults, parents; a struct, a class or an enum conforms in its list —
   one interface bare, `:: I`, several in brackets — or in `extend T :: [I] { … }`; every
   abstract member of the chain with its exact signature (`LYS-SEM0020`, `LYS-SEM0042`); a
   list names interfaces only (`LYS-SEM0078`). A default's `this` is the interface value, so a
   call on it dispatches again (§2 rule 3).
2. **Interface values** (§2, §11): a value of a conforming struct, class, enum or built-in type
   where the interface is expected; a call through it runs the conformer's method. Two are not
   compared (`LYS-SEM0059`). A child interface's value is a value of each parent.
3. **Extend blocks** (§6 rule 1) add methods and conformances to a type of the program or a
   built-in one — `extend int :: [Named] { … }`, `extend string { … }`, `this` the value; an
   interface is not extended (`LYS-SEM0124`).
4. **Delegation** (§5): `I by field` forwards every abstract member of the chain the type does
   not write to the field, read at each call, and the forwarded member is the type's too; the
   field holds a value of the interface (`LYS-SEM0123`); an enum delegates nothing
   (`LYS-PAR0047`).
5. **`Any`, `is`, type patterns** (§9): `x is T` on an interface value, with its narrowing — a
   box gives its value back — and `c: Circle` in a `match`; on a value of a known type, or
   against a type no interface value holds, refused (`LYS-SEM0131`). `Any` is a name of the
   prelude in Lyric-Script (Lyric 5 imports it from `std.core`).
6. **Sealed interfaces** (§10 rules 1–2): type patterns for every conformer cover a match without
   `_`; the witness names the conformer missing (`_: Rect`). A script is one module, so every
   conformer stands in the interface's.
8. **Equality without a list** ([03 Eq](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md); Lyric 5 §14 rules 2–3): `==` and `!=` compare a
   struct, an enum or a tuple part by part, without a conformance written — a struct's fields in
   declaration order, an enum's variant first and then its payload, a tuple's elements in order
   — when every part compares; an optional compares its value. A class compares only as an
   `Identity` (`class C :: [Identity]`), by its reference; any other class, a
   function value and an interface value do not compare, and neither does a type holding one
   (`LYS-SEM0059`, the part named). `Identity` is a name of the prelude, as `Any` is.
9. **The Debug form, given unasked** (Lyric 5 §14 rules 2–3 and 7): every value prints. A
   scalar and a string print as themselves; `{x}` and `println(x)` print any other value in its
   Debug form — `P { x = 1, name = "a" }`, `E.B(3)`, `E.R { w = 4 }`, `E.A`, `(1, "a")`, an
   optional as its value or `null`, a string inside it quoted and a `char` in single quotes, a
   class's fields as a struct's. Until the descriptors (S3i) an interface value prints as
   `<I>`, its interface's name, and a function value as `<fn>`.
10. *Informative.* An interface value is the conformer's own reference; a scalar's, a string's or
   a plain enum's value lies in a box of its type. Each type's descriptor carries its table of
   slots — every interface method of the program has one — and the interfaces it conforms to;
   `call.i` runs the receiver's function of a slot, `is.t` and `is.i` answer `is`.

## Deviations

- Synthesis from the compiler's fixed list; derivable interfaces of one's own through reflection in default bodies ([05 Syn](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- A struct becomes an interface value shared, not copied; `Clone` matters for classes ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).

**Conformance.** `conformance/cases/05-interfaces/` (`since: 1.0.0`).

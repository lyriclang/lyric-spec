# 5. Interfaces

**Base.** Lyric 5.0 [§5](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/05-interfaces.md) applies, with the deviations below.

**Status.** Written for what S3 builds: interfaces, their values, extends, delegation, `is`, sealed
interfaces, equality and the Debug form, `Self` and static members, associated types; their
bounds, fixations and value form, and generic members with the descriptors (S3i), the family written in a list and the operator interfaces
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
   class's fields as a struct's, a generic type's under its declared name, `Pair { a = 1 }`.
   An interface value and a value of a type parameter print the form of the value they hold —
   through a slot every type's table fills (S3i) —, alone a string as itself and inside another
   value quoted, as for any value; a function value prints as `<fn>`.
10. **`Self` and static members** (§7 rules 1–3): `Self` is the conforming type — in an
   interface the conformer, written as its own type by an implementation (`LYS-SEM0042`); in a
   struct, a class, an enum or an extend block the type itself. An interface may declare
   `static fn` members, implemented by a static of the conformer's (`LYS-SEM0042` otherwise) and
   reached through a type parameter, `T.parse(s)` — on a value of it not (`LYS-SEM0055`), nor a
   method through the type; a static with a body is a default, copied for each conformer. An
   interface that names `Self` beyond the receiver, declares a static or a generic member, or
   extends one that does, is a constraint only (`LYS-SEM0126` where it is written for a value).
   A type parameter satisfies what its constraints and their parents are, also where it is
   handed to another generic. `static let` members, and generic members of an interface that
   names `Self`, come later.
11. **Associated types** (§8 rules 1–4): an interface declares `type Item`, with a default
   `type Item = T` or none; a conforming type answers in its body or its extend block,
   `type Item = int` — without an answer and a default it is refused (`LYS-SEM0128`), an answer
   no interface of the type asks for too (`LYS-SEM0129`). Inside the interface the associated
   type is `Self.Item`, an implementation writes the answer; through a constraint it is
   `T.Item`, which a constraint of `T` declares (`LYS-SEM0128` otherwise). An interface that
   declares one is a constraint only (rule 10). Unlike Lyric 5's copies (§9.1 rule 4), the shared
   copy of 11 Gen does not serve a type parameter such an interface constrains: an answer's slots
   differ by type, so each argument gets a copy of its own. Bounds, paths through an answer
   (`T.Iter.Item`), fixations (`Iterator<Item = int>`) and the value form come later.
12. *Informative.* An interface value is the conformer's own reference; a scalar's, a string's or
   a plain enum's value lies in a box of its type. Each type's descriptor carries its table of
   slots — every interface method of the program has one — and the interfaces it conforms to;
   `call.i` runs the receiver's function of a slot, `is.t` and `is.i` answer `is`.

## Deviations

- Synthesis from the compiler's fixed list; derivable interfaces of one's own through reflection in default bodies ([05 Syn](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- A struct becomes an interface value shared, not copied; `Clone` matters for classes ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).

**Conformance.** `conformance/cases/05-interfaces/` (`since: 1.0.0`).

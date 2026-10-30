# 5. Interfaces

**Base.** Lyric 5.0 [§5](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/05-interfaces.md) applies, with the deviations below.

**Status.** Written for what S3 builds: interfaces, their values, extends, delegation, `is`, sealed
interfaces, equality and the Debug form, `Self` and static members, associated types; their
bounds, fixations and value form, and generic members with the descriptors (S3i), the family written in a list and the operator interfaces
with the prelude's interfaces (S7), members per interface in separate blocks (§3 rule 4) with
S7.

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
   handed to another generic. A type's constant, `static let zero: P = P { x = 0 }` with its type
   and its value (`LYS-SEM0010` otherwise), is set before the script's own statements (Lyric 5 04
   §1 rule 2) and read as `P.zero`; an interface asks one of its conformers without a value
   (`LYS-SEM0127`), `static let zero: Self`, read through a type parameter, `T.zero`. A constant of
   a generic type, and generic members of an interface that names `Self`, come later.
11. **Associated types** (§8 rules 1–4): an interface declares `type Item`, with a default
   `type Item = T` or none; a conforming type answers in its body or its extend block,
   `type Item = int` — without an answer and a default it is refused (`LYS-SEM0128`), an answer
   no interface of the type asks for too (`LYS-SEM0129`). Inside the interface the associated
   type is `Self.Item`, an implementation writes the answer; through a constraint it is
   `T.Item`, which a constraint of `T` declares (`LYS-SEM0128` otherwise). An interface that
   declares one is a constraint only (rule 10). Unlike Lyric 5's copies (§9.1 rule 4), the shared
   copy of 11 Gen does not serve a type parameter such an interface constrains: an answer's slots
   differ by type, so each argument gets a copy of its own. A bound, `type Iter :: [Iterator]`,
   is met by every answer (`LYS-SEM0160`); through `T.Iter` the associated type has the bounds'
   members and satisfies what they are (`LYS-SEM0027` for a member none gives), and a path goes
   on through them, `A.Iter.Item`. A constraint may fix one (§8 rule 5),
   `T :: [Iterator<Item = int>]`: inside, `T.Item` is that type wherever it stands; an argument
   whose answer is another is refused (`LYS-SEM0028`), a name the interface does not declare too
   (`LYS-SEM0128`). The **value form** (§8 rule 6): `Iterator<Item = int>`, every associated type
   fixed, is the type of a value — a member typed by one has the fixed type, `next(): ?int` — and a
   type stands for it where it conforms and answers alike (`LYS-SEM0001` otherwise). An associated
   type left open keeps the interface a constraint only (`LYS-SEM0126`); a member that names
   `Self` itself, a static or a generic member keeps it one whatever is fixed — `Self.Item`
   alone does not.
12. **Generic extend blocks** (§13 rules 1–4): `extend<T :: [Show]> Box<T> { … }` adds members
   to every instance whose arguments meet the block's constraints — on another one the member is
   not there (`LYS-SEM0134`) —, and `extend<T :: [Show]> Box<T> :: [Show] { … }` its
   conformance to those alone (**conditional conformance**; `Box<int>` is no `Show` where `int`
   is none, `LYS-SEM0028`). A type conforms to an interface once, from whichever site
   (`LYS-SEM0133` at the second). The target is the type at the block's parameters, in its order;
   `extend<T> T[] { … }` (or `List<T>`) adds members to every list, `this` the list (S7b2a). A
   block on one instance, a list's conformances and the blanket blocks (rules 6–9) come with
   the collections (S7).
13. **One method set and the qualified call** (§3 rules 1–3, §4): a type's own member answers
   every conformance's member of its name; two defaults of one name from two interfaces, which the
   type does not write itself, are refused at its declaration (`LYS-SEM0043`) — it writes the
   member, one function for both. `I.m(x, …)` calls the member of `I` with `x` as its receiver,
   the implementation `x`'s type has for `I`: on a value of a type, through a type parameter,
   through an interface value; the receiver conforms (`LYS-SEM0125`) and comes first
   (`LYS-SEM0014`); a static member is not called through its interface (`LYS-SEM0231`). One
   name implemented apart per interface in separate blocks (§3 rule 4, `LYS-SEM0122`) comes with
   S7.
14. *Informative.* An interface value is the conformer's own reference; a scalar's, a string's or
   a plain enum's value lies in a box of its type. Each type's descriptor carries its table of
   slots — every interface method of the program has one — and the interfaces it conforms to;
   `call.i` runs the receiver's function of a slot, `is.t` and `is.i` answer `is`.

## Written (S7, the core collections)

15. **Generic interfaces** (§5; S7c1a): `interface I<T, …> { … }` declares type parameters, with
   constraints as a generic function's; its members may name them. `I<int>` — written in a
   conformance (`:: [I<int>]`, in an extend block's too), a constraint (`T :: [I<int>]`), a
   parent (`interface J<T> :: I<T>`), or as a value's type — is an interface of its own: a type
   conforms to it by members whose signatures are the members' at those arguments
   (`LYS-SEM0042` otherwise), and a value of it is no `I<string>` (`LYS-SEM0001`). The arguments
   are written, as many as the parameters (`LYS-SEM0026`). A generic type conforms at its own
   parameters, `class Cell<T> :: Store<T>`, and each instance at its arguments (`Cell<int>` is a
   `Store<int>`). A call through an `I<int>` value or a `T :: [I<int>]` reads the members at
   `int`. `Self` stands in a generic interface as in any (rule 10) — a member over `Self` binds
   it with the interface's parameters, `static fn make(items: T[]): Self` through
   `B :: [Maker<int>]` —, and a default member may read the parameters: each conformer runs its
   copy at its instance's arguments, through its table too, and so does each instance of a
   generic conformer (S7c1b).

## Deviations

- Synthesis from the compiler's fixed list; derivable interfaces of one's own through reflection in default bodies ([05 Syn](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- A struct becomes an interface value shared, not copied; `Clone` matters for classes ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).

**Conformance.** `conformance/cases/05-interfaces/` (`since: 1.0.0`).

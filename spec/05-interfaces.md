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
   — when every part compares; an optional compares its value, a list its elements in order.
   Such a value **is** an `Equatable`: the prelude declares `interface Equatable { fn equals(o:
   Self): bool }` (Lyric 5 §12 rule 5; S7c5a), a constraint only (rule 10). A class compares as
   an `Identity` (`class C :: [Identity]`), by its reference, or as the `Equatable` it declares —
   through its own `equals`, else field by field; any other class, a function value and an
   interface value do not compare, and neither does a type holding one (`LYS-SEM0059`, the part
   named). A type's own `equals(o: Self): bool` is what `==` calls; `x.equals(y)` is `x == y`
   where the type has none. Over a type parameter `==` asks `T :: [Equatable]` (`LYS-SEM0059`
   otherwise) and compares as the argument's type does — a parameter so constrained gets a copy
   per argument type, not a shared one (11 Gen). The comparing methods of a list are the
   prelude's `extend<T :: [Equatable]> T[] :: Contains<T>` ([03](03-types.md) rule 16). `x in xs`
   is `xs.contains(x)` through the right operand's `Contains<T>` (`interface Contains<T> { fn
   contains(x: T): bool }`, Lyric 5 §12 rule 10; S7c5c3), `x` evaluated first and adapting to `T`,
   `x !in xs` its negation; without it `in` is refused (`LYS-SEM0059`) — over a string and a map it
   comes with S7e and S7d. A conditional conformance to an instance of a generic interface holds
   where the condition does, at compile time and at run time (S7c5c3). `Identity` is a name of the
   prelude, as `Any` is.
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
   (`LYS-SEM0127`), `static let zero: Self`, read through a type parameter, `T.zero`. A member of
   an interface that names `Self` may have type parameters of its own (S7c4c1), bound by its
   call's arguments; a constant of a generic type comes later.
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
   `extend<T> T[] { … }` (or `List<T>`) adds members to every list, `this` the list (S7b2a), and
   `extend<T> T[] :: [I] { … }` makes every list an `I` (S7c3), for a value of `I` and a
   constraint alike. A **blanket block** (§13 rule 7; S7c4c2), `extend<T :: [Named]> T { … }`,
   adds its members to every type its constraints admit — a struct, class, enum, built-in type
   or list, an interface value, and in a generic body a type parameter whose constraints admit
   it: the receiver binds the parameter the target names, a fixation in a constraint the others
   (`extend<I :: [Iterator<Item = T>], T> I`), `this` is the receiver; a parameter neither binds
   is refused (`LYS-SEM0170`). A member the type has itself — written, from another block, an
   interface's default, left to a field — comes first and is warned about where it stands
   (`LYS-SEM0168`); generic code that reaches the name through the block's constraints calls
   the block's, for that type too. Two blanket blocks that give a type one name are refused at
   its call (`LYS-SEM0121`); it holds no constant (`LYS-SEM0124`). Its static members are reached through a type it reaches,
   `Cat.kind()`, or a type parameter, `T.kind()` (S7c4c3a). A blanket block may **conform**
   (rule 8; S7c4c3a), `extend<T :: [Named]> T :: [Greets] { … }`: it gives the interface and its
   chain to every type its constraints admit, its signatures checked at `T` (`LYS-SEM0042`,
   `LYS-SEM0020`), the associated types answered in its body or by a fixation in its list —
   `extend<I :: [Iterator]> I :: [Iterable<Iter = I>]`, §8 rule 3 (`LYS-SEM0128`,
   `LYS-SEM0129`); such a type meets a constraint on the interface, and a value of the interface
   made from it has the block's members in its table. A type that conforms to one of the chain
   itself where the block reaches it is refused at its conformance, a second blanket block that
   gives one of a chain at the block (`LYS-SEM0133`) — a list, a generic type the VM holds, and
   one a conformance on a condition reaches, on that condition (S7c4c3b), among them. A **block
   on one instance** (rules 1–3; S7c4c3b), `extend Box<int> { … }`, `extend int[] { … }`, adds
   its members and conformances to that instance alone, checked at it — another instance has
   none of them (`LYS-SEM0012`), and one whose template conforms already, unconditionally or
   on a condition the instance meets, conforms at a second site (`LYS-SEM0133`). A parameter
   only the conformance names (rule 9) comes with `From`/`Into` (S7f); the other shapes of rule
   6 with the collections (S7).
13. **One method set and the qualified call** (§3 rules 1–3, §4): a type's own member answers
   every conformance's member of its name; two defaults of one name from two interfaces, which the
   type does not write itself, are refused at its declaration (`LYS-SEM0043`) — it writes the
   member, one function for both. `I.m(x, …)` calls the member of `I` with `x` as its receiver,
   the implementation `x`'s type has for `I`: on a value of a type, through a type parameter,
   through an interface value; the receiver conforms (`LYS-SEM0125`) and comes first
   (`LYS-SEM0014`); a static member is not called through its interface (`LYS-SEM0231`). A
   name implemented apart per conformance block, and the members of several instances of one
   generic interface side by side, are rule 18's.
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
   generic conformer (S7c1b). A member may have type parameters of its own, `static fn
   fromIter<I :: [Iterator<Item = T>]>(it: I): Self` (S7c4c2): a conformer's has as many,
   constrained by the same interfaces and fixations (`LYS-SEM0042` otherwise); called through a
   type parameter, the copy for its argument binds them from the call's arguments. An interface
   with such a member is a constraint only (rule 11, `LYS-SEM0126`).
16. **Ordering** (Lyric 5 §12 rule 6, §14 rules 2–3; S7c5b): the prelude declares
   `enum Ordering { Less, Equal, Greater }`, `interface Ordered :: Equatable { fn compare(o:
   Self): ?Ordering }` and `interface TotalOrder :: Ordered { fn totalCompare(o: Self): Ordering
   }`, constraints only, and gives both to `int`, `char` and `string` — and to `float`, unlike
   Lyric 5 ([05 Fl](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)): its `compare` is `null` where a NaN takes part, its
   `totalCompare` IEEE 754's total order, -NaN, -infinity, …, -0.0, 0.0, …, infinity, NaN (the
   sign of a computed NaN is the hardware's). `<`, `<=`, `>` and `>=` on another type read its
   `compare`: `.Less`, not `.Greater`, `.Greater`, not `.Less`; `null` makes all four false;
   without `Ordered` they are refused (`LYS-SEM0003`). A struct, class or enum that lists
   `Ordered` or `TotalOrder` without the member has it synthesized, lexicographic over its
   fields in declaration order — an enum's variant position first, then its payload —, the
   first part not `.Equal` deciding and a `compare` meeting `null` giving `null`; each part is
   one, else the conformance is refused (`LYS-SEM0020`). A type's own `compare` or
   `totalCompare` replaces the synthesis; `x.compare(y)` and `x.totalCompare(y)` stand on every
   conformer. Over a type parameter `T :: [Ordered]` the comparison is its argument's, in the
   copy (rule 8). A list, an optional and a tuple are no `Ordered`, as in Lyric 5.
17. **Operators** (Lyric 5 §12 rules 1–4 and 7; S7c5c2): the prelude declares `interface Add<Rhs
   = Self> { type Out = Self; fn add(rhs: Rhs): Self.Out }` and likewise `Sub` `sub`, `Mul`
   `mul`, `Div` `div`, `Rem` `rem`, `BitAnd` `bitAnd`, `BitOr` `bitOr`, `BitXor` `bitXor`,
   `Shl<Rhs = int>` `shl`, `Shr<Rhs = int>` `shr`, and `Neg` with `neg()`, `BitNot` with
   `bitNot()`. On a struct, a class or an enum, `a + b` is `a.add(b)` through the conformance the
   right operand's static type picks — `v * 2.5` takes `Mul<float>`, an `int` literal adapting to
   a `float` where the type takes that —, its result the conformance's `Out`; `-a` and `~a` go
   through `Neg` and `BitNot`; without the conformance the operator is refused (`LYS-SEM0003`).
   `a op= b` is `a = a op b` on a place whose type that `Out` is (`LYS-SEM0001` otherwise), what
   leads to the place evaluated once. The scalars keep their own arithmetic and conform besides —
   `int` to all, `float` to the arithmetic and `Neg`, `string` to `Add` —, so `T :: [Add<Out =
   T>]` takes them; under `T :: [Add]` alone `a + b` is a `T.Out`. A type may conform to several
   instances of an operator's interface, each answering its own `Out` (rule 18): `v * 3.0` takes
   `Mul<float>` and its answer.
18. **Several members of one name** (Lyric 5 §3 rules 1, 4–5, §8 rule 3, 08 §1.2; S7c5d). A
   type's members, its blocks' among them, share a name at different counts — a default widens a
   count to a range, a function's too (`LYS-SEM0085`) —, a call taking the one that takes as many
   arguments (`LYS-SEM0087` where none does). One name implemented apart in separate conformance
   blocks belongs to each block: the unqualified call is refused (`LYS-SEM0122`); the qualified
   call, an interface value, a constraint and a default of the interface reach each. Members of one
   name and count stand side by side where each answers its own instance of one generic interface
   — `struct Label :: [From<int>, From<string>]`, or an operator's conformance block,
   `extend V :: [Mul<float>]`, beside the type's own `mul` —; two answering one instance are
   refused (`LYS-SEM0085`). A call chooses among them by the arguments' types: the member whose
   parameters take them, of several the one whose parameters are those types, a literal its
   default type (`LYS-SEM0086` where none or several are left); a constraint chooses by the
   instance it names, an interface value by its table — each instance has slots of its own. A
   method read without a call is one of several where the position's function type says which
   (`LYS-SEM0089`). Any other second member of a name is refused where it is declared
   (`LYS-SEM0121`), a conformance block's beside the type's own at any count. An answer belongs to
   its conformance instance: a conformance block's answers are its conformances', the body's every
   conformance's — `Mul<float>` answers `Out = float` beside the type's `Mul`, and `T :: [Mul<float>]`
   reads that answer. The prelude gives `int` `Add<float>`, `Sub<float>`, `Mul<float>`,
   `Div<float>` and `Rem<float>`, `Out = float`, and `float` the same over `int` ([03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)):
   `T :: [Add<float, Out = float>]` takes either. A block on one instance (`extend Box<int>`)
   holds one member of a name (STATUS P22).
19. **`Clone` and `Default`** (Lyric 5 §14 rules 1–4; Script [05 D13](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md); S7c6c1). The prelude declares
   `interface Clone { fn clone(): Self }` and `interface Default { static fn default(): Self }`,
   constraints only; the scalars and `string` conform to both, a list to `Default` and, of a
   `Clone` element, to `Clone` — a new list of the elements' clones. A struct, a class or an enum
   that lists one without the member has it synthesized: `clone` copies the value parts — a
   scalar, a string, a struct, an enum, a function — and clones the reference parts, an object
   and a list, an optional's value and a tuple's elements alike, an enum's variant rebuilt with
   its payload so; a value without a reference part is itself. `default` takes each field's
   initializer, else its type's default: zero, `false`, `'\0'`, `""`, `null`, `[]`, a tuple of
   its elements' defaults, a type's `default()`. A reference part that does not clone, a field
   without an initializer whose type has no default, is refused at the declaration
   (`LYS-SEM0020`); an enum's `Default` too (`LYS-SEM0135`). A generic type clones and defaults
   where its arguments do: at its declaration a part over a type parameter is conditional, so
   `Box<NoClone>` has no `clone` (`LYS-SEM0012`) and is no `Clone` (`LYS-SEM0028` at a
   constraint). Through `T :: [Clone]` and `T :: [Default]`, `x.clone()` and `T.default()` are
   the argument's own; a member the compiler synthesizes — `equals`, `compare`, `clone` — is never
   called through a table, which holds none.

## Deviations

- Synthesis from the compiler's fixed list; derivable interfaces of one's own through reflection in default bodies ([05 Syn](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).
- A struct becomes an interface value shared, not copied; `Clone` matters for classes ([05](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md)).

**Conformance.** `conformance/cases/05-interfaces/` (`since: 1.0.0`).

# 5. Interfaces and conformance

An interface names the methods a type promises; a type **conforms** by implementing them; a
value of the interface's type carries any conforming value and reaches its implementation —
the language's one dynamic dispatch
([04 D1–D15](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/04-abstraktion.md),
[01 V7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[03 T5–T7, T10, T11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)).

## Scope

Declaring an interface and a conformance, the interface value, how a call resolves. Written with
M4 S1, S3, S4, S4b, S5a and S5b; the chapter grows with the milestone's slices — operator
interfaces (D6), generic extends (T7), synthesis (D7). Of the associated types (T6,
[§8](#8-associated-types)) the value form `Iterator<Item = int>` and an answer per interface
instance are not written yet. What is not written here yet is decided in the design documents,
not here.

**Conformance.** `conformance/cases/05-interfaces/`.

## 1. Interfaces and conformance

1. `interface I { … }` declares **instance methods**: abstract, `fn area(): int;`, or with a
   **default** body. A member carries no `pub` (`LYR-SEM0118`): an interface's members are
   public always (D14).
2. A struct, a class or an enum **conforms** in its interface list, `struct S :: [I, J] { … }`,
   or through an extend block, `extend T :: [I] { … }`; every entry names an interface
   (`LYR-SEM0078`). A conformance implements every abstract member of the interface's chain with
   an exact signature — arity, parameter types, return type, `mut` (`LYR-SEM0020`,
   `LYR-SEM0042`); a default may be left as it is, and an own member of the name overrides it.
3. An interface may name **parents**, `interface Labeled :: [Named]`: conforming to the child
   conforms to every parent, a parent's defaults are inherited, a parent constraint is satisfied
   by the child. The list holds interfaces only and no cycle (`LYR-SEM0078`), and a name stays
   one: a child does not redeclare a parent's member, two parents do not bring one name from
   two declarations (`LYR-SEM0079`); a name reached twice through one declaration — a diamond —
   is one member.

## 2. Interface values

1. A value whose static type is an interface holds **any conforming value** of a struct, a
   class or an enum: `let d: Damageable = Player.new(100);`. The transition happens at the
   positions of 03 T8 — a binding with a type, an argument, a return, a field, an array element
   under a context. *(Informative.)* It is a fat pointer: the data and the table of the concrete
   type's implementations, two words, by value (V7).
2. A **class** value is shared through the interface value: what one side writes, the other
   reads. A **struct** or an **enum** value is **copied** at the transition (D12) and lives in
   the interface value from then on: a `mut fn` called through it writes that copy, the original
   stays as it was, and a later change to the original is not seen. *(Informative.)* The copy
   lies in a box on the heap.
3. A call through the interface value runs the conforming type's implementation — the language's
   only **dynamic dispatch**. A default runs with `this` as the **interface value**, so a call on
   `this` inside it dispatches again: `fn isAlive(): bool { return this.getHp() > 0; }` reaches
   whichever `getHp` stands behind the value.
4. An interface value is held in a binding, a field, an array, an optional, passed and returned
   like any value, and answers every member of the interface's chain. Two interface values are
   not compared.

## 3. One method set

1. A type holds **one function per name** (D2): its own members, the methods its inherent
   extend blocks add, and the implementations of its conformances — an own member, a member of
   a conformance block, an interface's default, a member delegated to a field (§5). A name two
   of these would give it is refused where the second is declared (`LYR-SEM0121`): an
   extension beside an own member, two extensions, an extension beside a default of a conformed
   interface, a conformance block beside an own member.
2. An **own member is the implementation** of every conformance's member of that name, and
   overrides a default. Two defaults of one name from two interfaces, which the type does not
   write itself, are the type's to settle: it writes the member, one function for both
   (`LYR-SEM0043`, D3).
3. **Every path reads the same set** (R3): a call on the concrete type, a call through an
   interface value, a call through a constraint reach the one function.
4. The one exception is scoped (D3): a type may implement one name **separately per
   interface**, in separate conformance blocks — `extend C :: [I1] { fn greet() … }` beside
   `extend C :: [I2] { fn greet() … }`. The name then belongs to each block: the unqualified
   call `c.greet()` is refused and says how to qualify (`LYR-SEM0122`); through an interface
   value of `I1` or `I2`, and through the qualified call (§4), each is reached.

## 4. The qualified call

1. `I.m(x, …)` calls the member `m` of the interface `I` with `x` as its receiver — the
   implementation `x`'s type has for `I` (D2 R5). The receiver conforms to `I` (`LYR-SEM0125`
   otherwise) and comes first (`LYR-SEM0014`). It is the form that names what the unqualified
   call cannot (§3.4), and it is checked as the member call it is.

## 5. Delegation

1. A struct or a class may conform **by delegating** to one of its fields: `class Dog ::
   [Walker by legs] { var legs: Legs, … }` (D1). The field exists and conforms to the
   interface, or holds a value of it (`LYR-SEM0123` otherwise). Every abstract member of the
   interface's chain that the type does not write itself is **forwarded** to the field, as if
   `fn walk(d) { this.legs.walk(d); }` were written.
2. Own members win. The interface's defaults run on the outer type, as every default does, and
   reach the forwarded members through `this`. There is no passthrough of `this`: the field's
   implementation runs with the field as its receiver, never the outer value — a call on
   `this` inside it reaches the field's own members, which is why delegation has no fragile
   base.
3. A `var` field may be exchanged at run time; the next call forwards to the new value.
4. Two delegations that would answer one name are refused (`LYR-SEM0121`); an enum delegates
   nothing (`LYR-PAR0047`).

## 6. Extend blocks

1. `extend T { … }` adds methods to a type and `extend T :: [I] { … }` a conformance, in any
   module (03 T7 X3): there is no orphan rule — coherence is checked for the whole program. An
   interface is not extended directly (`LYR-SEM0124`); the generic form, `extend<T :: [I]> T
   { … }`, is the one (D15, with 03 §11).

## 7. `Self` and static members

1. In an interface, **`Self`** is the conforming type (03 T5): `fn equals(o: Self): bool`. An
   implementation writes its own type where the interface writes `Self` (`LYR-SEM0042`
   otherwise); through a constraint `T :: [I]`, `Self` is `T`. In a struct, a class or an enum,
   `Self` is the type itself — a generic one at its own parameters.
2. An interface may declare **static members**, `static fn parse(s: string): Self;`, without a
   body (`LYR-SEM0127`): every conforming type implements one with a static member of its own
   (`LYR-SEM0042`), and the member is reached through a type parameter alone, `T.parse(s)` —
   the conformer's own static, a direct call. On a value of the parameter it is not called
   (`LYR-SEM0055`).
3. An interface that names `Self` beyond the receiver, or declares a static member, is a
   **constraint only** (04 D9): no value of it arises — a table would hold no one function for
   such a member — and the transition says so (`LYR-SEM0126`). An interface with neither is a
   value as [§2](#2-interface-values) says.

## 8. Associated types

1. An interface may declare an **associated type**, `type Item;` (03 T6): a type every
   conforming type names, once. Where a type parameter of the interface is an input — chosen
   by whoever writes the conformance, `Add<int>` beside `Add<Vec2>` — an associated type is an
   output of the conformance: one answer per type, read off the type wherever it is used. The
   two combine, `interface Index<K> { type Output; fn get(k: K): Self.Output; }`.
2. Inside the interface the associated type is **`Self.Item`**. The declaration may carry a
   default, `type Out = Self;`, resolved with `Self` as the conforming type.
3. A conforming type **answers** in its body or in the conformance block: `type Item = int;`.
   A conformer without an answer, where the interface gives no default, is refused
   (`LYR-SEM0128`); an answer that no interface of the type asks for is refused
   (`LYR-SEM0129`); the answer is what the signatures read — `fn first(): Self.Item` is
   implemented by `fn first(): int` (`LYR-SEM0042` otherwise). The answer is one per type and
   interface: a second conformance block may repeat it, not change it (`LYR-SEM0129`). In a
   type's own body `Self.Item` is its answer.
4. Through a constraint the associated type is a **type path**, `T.Item`:
   `fn firstOf<T :: [Container]>(c: T): T.Item { return c.first(); }` — the answer of whatever
   `T` becomes, `int` at `firstOf(IntBox { … })`. The parameter's constraints declare it
   (`LYR-SEM0128` where none does). An interface is no head for the path: `Container.Item` is
   nobody's answer.
5. A constraint may **fix** an associated type: `T :: [Iterator<Item = int>]`. Inside the
   declaration `T.Item` is `int`; an argument whose answer is another type does not satisfy
   the constraint (`LYR-SEM0028`); a name no associated type of the interface carries is
   refused (`LYR-SEM0128`).
6. An interface declaring an associated type is a **constraint only** for now
   ([§7](#7-self-and-static-members) rule 3, `LYR-SEM0126`): the value form, the interface
   with its answer fixed as a fat pointer, comes with the iterators of M8a and is not written
   here.

## 9. `Any`, type tests and type patterns

1. **`Any`** is the empty interface of `std.core` (03 T10), visible without an import as
   every public type of `std.core` is. Every struct, class and enum value is an `Any` at the
   transition, nothing declared — the ordinary transition of [§2](#2-interface-values), a
   copy into a box for a struct or an enum. Nothing converts to `Any` unasked: only a position
   whose type is `Any` takes a value that way, and a scalar never (`LYR-SEM0001`). `Any[]` is
   the heterogeneous array.
2. **`x is T`** (03 T11) asks an interface value what it holds and answers a `bool`: for a
   struct, a class or an enum `T`, whether the value is one — a comparison of the descriptor
   the value's table begins with; for an interface `T` that is a value type
   ([§7](#7-self-and-static-members) rule 3), whether the concrete type conforms to it — a
   search of the conformance list behind that descriptor. `is` stands at the comparison level
   and does not chain.
3. The operand's static type is an **interface**. On a known type (`c is Circle` with
   `c: Circle`), on an optional (`?Shape`: test for `null` first), against a type a value is
   never behind an interface (`s is int`) and against a type parameter (`s is T`, O2: a
   dynamic test takes `Any`) the test is refused (`LYR-SEM0131`); against a constraint-only
   interface it is refused as a value of it is (`LYR-SEM0126`).
4. **Narrowing.** In the branch `x is T` guards, the name `x` **is a `T`** — the smart cast,
   the mechanism of the null test ([03 §3.2](03-types.md#32-tests-and-narrowing)):
   `if (s is Circle) { s.r }`, `s is Circle && s.r > 0`. The branch's end ends it, as an
   assignment to the name does; the other branch learns nothing. A read of the narrowed name
   takes the value out of the interface value: the object for a class, a **copy** for a struct
   or an enum (04 D12).
5. **Type patterns.** `c: Circle` and `_: Circle` in a `match` over an interface value test
   the same way and bind `c` as the type ([09 §2](09-patterns.md#2-the-forms) rule 12). A
   match of type patterns over an interface needs `_`: the set of conformers is open
   (`LYR-SEM0050`) — unless the interface is sealed ([§10](#10-sealed-interfaces)).
6. There is no `as?`: `as` is the bit-near conversion of scalars (03 T1d), and `is` with its
   narrowing is the downcast.

## 10. Sealed interfaces

1. **`sealed interface Shape { … }`** (04 D8) closes the set of its conformers: every struct,
   class and enum that conforms to it — in its own list or in a conformance block — and every
   interface that names it as a parent stands in the **module that declares it**
   (`LYR-SEM0132` elsewhere). `sealed` is a contextual word and stands before `interface`
   only (`LYR-PAR0048`).
2. A `match` of type patterns over a sealed interface value is **exhaustive without `_`** when
   every conformer has an unguarded arm; the diagnostic names the conformer missing, as the
   pattern to add (`LYR-SEM0050`, `_: Rect`). A conformer added later makes every such match
   without it an error — the point of sealing. Against an enum: an enum is closed variants
   with payloads, a sealed interface closed types with members of their own.
3. *(Informative.)* The compiler may dispatch such a match as a switch over the descriptors.

## 11. The child interface value as a parent value

1. A value of an interface is a value of each **parent** in its chain (04 D10, [§1](#1-interfaces-and-conformance)
   rule 4): `let d: Display = shape;` with `Shape :: [Display]` is a coercion at the ordinary
   sites — a binding, an argument, a return — never inside a container (`Shape[]` is no
   `Display[]`). The parent's table is found at the transition through the concrete type's
   conformance list; the data stays the same object or box.
2. Only up the chain: an unrelated interface and the way down are refused (`LYR-SEM0001`); the
   way down is `is` ([§9](#9-any-type-tests-and-type-patterns)).

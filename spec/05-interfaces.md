# 5. Interfaces and conformance

An interface names the methods a type promises; a type **conforms** by implementing them; a
value of the interface's type carries any conforming value and reaches its implementation —
the language's one dynamic dispatch
([04 D1–D15](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/04-abstraktion.md),
[01 V7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[03 T5–T7, T10, T11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)).

## Scope

Declaring an interface and a conformance, the interface value, how a call resolves. Written with
M4 S1, S3 and S4; the chapter grows with the milestone's slices — associated types (T6), `Any`,
type tests and `sealed` (T10, T11, D8), operator interfaces (D6), generic extends (T7),
synthesis (D7). What is not written here yet is decided in the design documents, not here.

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

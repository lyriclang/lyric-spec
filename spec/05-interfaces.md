# 5. Interfaces and conformance

An interface names the methods a type promises; a type **conforms** by implementing them; a
value of the interface's type carries any conforming value and reaches its implementation —
the language's one dynamic dispatch
([04 D1–D15](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/04-abstraktion.md),
[01 V7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[03 T5–T7, T10, T11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)).

## Scope

Declaring an interface and a conformance, the interface value, how a call resolves. Written with
M4 S1; the chapter grows with the milestone's slices — one method set and delegation (D1–D3),
`Self` and associated types (T5, T6), `Any`, type tests and `sealed` (T10, T11, D8), operator
interfaces (D6), generic extends (T7), synthesis (D7). What is not written here yet is decided in
the design documents, not here.

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

## 3. Resolution

1. Which implementation a member call on a **concrete** type reaches is fixed at compile time:
   an own member, else a visible extension method, else a default of a conformed interface's
   chain. *(The order of Lyric 4; 04 D2 makes the three one set, with M4 S3.)*
2. The table of a (type, interface) pair holds what rule 1 settled for every member of the
   chain; a call through an interface value reads it and searches nothing.

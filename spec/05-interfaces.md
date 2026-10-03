# 5. Interfaces and conformance

An interface names the methods a type promises; a type **conforms** by implementing them; a
value of the interface's type carries any conforming value and reaches its implementation —
the language's one dynamic dispatch
([04 D1–D15](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/04-abstraktion.md),
[01 V7](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[03 T5–T7, T10, T11](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/03-typsystem.md)).

## Scope

Declaring an interface and a conformance, the interface value, how a call resolves. Written with
M4 S1, S3, S4, S4b, S5a, S5b, S6, S7a and S7b; the chapter grows with the milestone's slices —
synthesis (D7). Of the associated types (T6, [§8](#8-associated-types)) the value form
`Iterator<Item = int>` is not written yet; of the operators (D6,
[§12](#12-the-operator-interfaces)) `in`, `[]` and the conversions `From`/`Into` wait for the
collections; a conformance of a built-in constructor (`T[] :: [Display]`, X2) waits for the
same. What is not written here yet is decided in the design documents, not here.

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
4. A default is **generic over `Self`**, the conformer (04 D9): `this` is the conformer's value,
   `Self` its type. Called on a conformer — on a value of the type, through a constraint, through
   a block (§13) — it runs as that type's own, also on a builtin, `extend int :: [Named]`, and for
   an interface that is a constraint only (§7 rule 3): a parameter `o: Self` takes the
   conformer, `Self.zero` reads its constant. `this` passes as the interface and as a parent of
   it, as a type parameter does. A **private helper** is the defaults' alone — through a
   constraint from anywhere else as well (04 §3 rule 8, `LYR-RES0009`) — and never a
   conformer's method of its name.

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
   only **dynamic dispatch**. A default called through it runs with `this` as the **interface
   value** — the interface is the conformer there (§1 rule 4) —, so a call on `this` inside it
   dispatches again: `fn isAlive(): bool { return this.getHp() > 0; }` reaches whichever `getHp`
   stands behind the value.
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
   value of `I1` or `I2`, and through the qualified call (§4), each is reached. One block that
   holds a name at two counts holds an overload set ([08 §1.2](08-expressions.md)), not two
   scopes.

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
2. A block adds **constants** too: a `static let` in it is the type's, under the type's name,
   as one in the type's body is — `extend int { static let answer: int = 42; }` makes
   `int.answer` (10 N1: a constant is a static member). A type holds one member of a name: a
   block's constant repeating a member of the type or of another block is refused
   (`LYR-SEM0121`). A generic block holds none (`LYR-SEM0159`): its constant would be one per
   instance, which is not decided.

## 7. `Self` and static members

1. In an interface, **`Self`** is the conforming type (03 T5): `fn equals(o: Self): bool`. An
   implementation writes its own type where the interface writes `Self` (`LYR-SEM0042`
   otherwise); through a constraint `T :: [I]`, `Self` is `T`. In a struct, a class or an enum,
   `Self` is the type itself — a generic one at its own parameters.
2. An interface may declare **static members** — `static fn parse(s: string): Self;` and
   `static let zero: Self;` — without a body or a value (`LYR-SEM0127`): every conforming type
   implements one with a static member of its own, in its body or in its conformance block
   (`LYR-SEM0042`; `LYR-SEM0020` where it has none). A `static let` answers with the type the
   interface writes, `Self` read as the conformer — `static let zero: int = 0;` in
   `extend int :: [Num]`. The member is reached through a type parameter alone, `T.parse(s)`,
   `T.zero` — the conformer's own static, a direct call or a read; of several of the name, the
   one that answers the member. On a value of the parameter
   it is not reached (`LYR-SEM0055`).
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
   default, `type Out = Self;`, resolved with `Self` as the conforming type, and a **bound**,
   `type Iter :: [Iterator];` (design 10 B6) — interfaces, written as a type parameter's
   constraints are (`LYR-SEM0078` otherwise), `Self` again the conforming type. Every answer
   conforms to the bound (`LYR-SEM0160`); an answer carries none of its own (`LYR-SEM0161`).
   `never` answers — as a default, an answer or a fixation — only an associated type bounded
   by `Error`, as the empty thrown set ([06](06-errors.md), design 05 E2 K4); elsewhere it
   would type a value that cannot exist (`LYR-SEM0145`).
3. A conforming type **answers** in its body or in the conformance block: `type Item = int;`.
   A conformer without an answer, where the interface gives no default, is refused
   (`LYR-SEM0128`); an answer that no interface of the type asks for is refused
   (`LYR-SEM0129`); the answer is what the signatures read — `fn first(): Self.Item` is
   implemented by `fn first(): int` (`LYR-SEM0042` otherwise). The answer belongs to the
   **conformance instance**: `Mul<int>` and `Mul<float>` of one type each answer `Out` for
   themselves ([§12](#12-the-operator-interfaces)); a second conformance block for the same
   instance is refused as a whole, its answers with it (`LYR-SEM0133`). In a type's own body
   `Self.Item` is its answer. A built-in conforms through its block alone and answers there. A
   **blanket or shape block** ([§13](#13-generic-extends) rules 6–8) answers in its body or by
   a fixation in its list — `extend<I :: [Iterator]> I :: [Iterable<Iter = I>]` — for every
   type it reaches: a type with no answer of its own is answered there, at the parameters it
   binds, and the block's signatures read the answer.
4. Through a constraint the associated type is a **type path**, `T.Item`:
   `fn firstOf<T :: [Container]>(c: T): T.Item { return c.first(); }` — the answer of whatever
   `T` becomes, `int` at `firstOf(IntBox { … })`. The parameter's constraints declare it
   (`LYR-SEM0128` where none does). An interface is no head for the path: `Container.Item` is
   nobody's answer. Through the path the associated type has **what its bound provides** — the
   members, `a.iter().next()`, and the constraints the bound reaches, `count(a.iter())` with
   `count<I :: [Iterator]>` — and nothing else: without a bound it has no member
   (`LYR-SEM0027`) and satisfies no constraint (`LYR-SEM0028`) until its answer is known. The
   path goes on through what each step provides: `A.Iter.Item` is the `Item` of what `A`'s
   `Iter` becomes, through `Iter`'s bound while that is open (`LYR-SEM0128` where the bound
   declares none), the answer on a type — `Bag.Iter.Item`. A blanket block reaches the
   associated type as it reaches a type parameter ([§13](#13-generic-extends)): bounded by
   `Iterator`, it is `Iterable` and has `iter()`.
5. A constraint may **fix** an associated type: `T :: [Iterator<Item = int>]`. Inside the
   declaration `T.Item` is `int`; an argument whose answer is another type does not satisfy
   the constraint (`LYR-SEM0028`); a name no associated type of the interface carries is
   refused (`LYR-SEM0128`).
6. An interface declaring an associated type is a **constraint only** for now
   ([§7](#7-self-and-static-members) rule 3, `LYR-SEM0126`): the value form, the interface
   with its answer fixed as a fat pointer, comes with the iterators of M8a and is not written
   here.
7. An interface's **parent list** is a constraint on `Self` and may **fix** a parent's
   associated type the same way: `interface Num :: [Add<Out = Self>] { … }`. Every conformer
   answers as fixed — another answer does not conform (`LYR-SEM0042`) — and through a
   constraint `T :: [Num]` the answer is the fixed type: `a + b` is a `T`.

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

## 12. The operator interfaces

1. The operators on a struct, a class or an enum are **method calls through the interfaces of
   `std.core`** (04 D6), one per operator: `a + b` is exactly `a.add(b)` through
   `Add<Rhs = Self> { type Out = Self; fn add(rhs: Rhs): Self.Out; }`, and likewise `-` `Sub`,
   `*` `Mul`, `/` `Div`, `%` `Rem`, `&` `BitAnd`, `|` `BitOr`, `^` `BitXor`, `<<` `Shl<Rhs = int>`,
   `>>` `Shr<Rhs = int>`; the unary `-x` is `x.neg()` through `Neg`, `~x` is `x.bitNot()`
   through `BitNot`. `!x` is `bool` only. The scalars keep their own arithmetic and conform
   besides, so a constraint `T :: [Add]` takes them.
2. **One resolution.** The conformance is chosen by the **static type of the right operand**:
   `v * 2` takes `Mul<int>`, `v * 2.5` takes `Mul<float>`; a literal adapts
   ([03 §9.2](03-types.md)), and two conformances a literal fits are an ambiguity to annotate
   (`LYR-SEM0083`). The result is the conformance's **`Out`** — `Self` unless the conformer
   answers otherwise. The homogeneous case is `struct Vec2 :: [Add]`; a heterogeneous
   conformance stands in a **conformance block** of its own with its answer,
   `extend Vec2 :: [Mul<float>] { type Out = float; fn mul(rhs: float): float { … } }`, beside the
   type's own `mul` ([§3](#3-one-method-set): the operand tells the two apart, and the block's
   stays reachable qualified).
3. Without the conformance the operator is **refused**, with the conformance to write
   (`LYR-SEM0003`): a method of the name alone is not the operator — nominal, not structural.
4. **`a += b`** and the other compound forms are `a = a.add(b)` on a `var` place whose type the
   answer is; there is no `AddAssign`. `++` and `--` stay the integers' own.
5. **Equality.** `a == b` on a struct, a class or an enum is `a.equals(b)` through
   `Equatable { fn equals(o: Self): bool; }`, `!=` its negation; both sides are the one type,
   and the scalars compare natively. Without the conformance `==` is refused (`LYR-SEM0059`).
6. **Ordering.** `<`, `<=`, `>` and `>=` read `a.compare(b)` through
   `Ordered :: [Equatable] { fn compare(o: Self): ?Ordering; }` with
   `enum Ordering { Less, Equal, Greater }`: `<` is `.Less`, `>` is `.Greater`, `<=` is not
   `.Greater`, `>=` is not `.Less`; **`null`** — the two are not ordered, as `float` with NaN —
   makes all four **false**. `TotalOrder :: [Ordered] { fn totalCompare(o: Self): Ordering; }`
   is what sorting and keys ask; `float` has none. Without `Ordered` an ordering is refused
   (`LYR-SEM0003`).
7. A generic body sees the answer the constraint fixes: `fn sum<T :: [Add<Out = T>]>(a: T, b: T): T`
   adds; under `T :: [Add]` alone `a + b` is a `T.Out`, which is not a `T`
   ([§8](#8-associated-types) rule 5).
8. `{x}` in an f-string renders through `Display { fn show(): string; }`; the scalars render
   natively and conform besides.

## 13. Generic extends

1. An extend block may carry **type parameters** of its own, `extend<T> List<T> { … }`
   (03 T7 X1), with constraints as a function's: `extend<T :: [Display]> List<T> { … }`. The
   target is a named type at the block's parameters, or one instance of it, `extend Box<int> { … }`,
   or a **built-in constructor** (X2, rule 6); a function type is no target (`LYR-SEM0047`).
   In the block, `this` is the target as written; `Self` stands for a plain target only.
2. A member of such a block is reached on every receiver the target **matches**: the receiver
   binds the parameters — `List<int>.first()` is an `int` — and the block's constraints must
   hold for what it bound; where they do not, the member is not there (`LYR-SEM0134`). A block
   on one instance adds to that instance alone (`LYR-SEM0012` elsewhere). A parameter the target
   does not name is bound where a **fixation** in another's constraint names it:
   `extend<I :: [Iterator<Item = T>], T :: [Num]> I` binds `I` to the receiver and `T` to its
   `Item`, whose constraints then hold or the member is not there.
3. **Conditional conformance.** `extend<T :: [Display]> List<T> :: [Display] { … }` gives the
   conformance to every instance whose arguments satisfy the block's constraints and to no
   other: `List<int>` is a `Display`, `List<Foo>` is not (`LYR-SEM0001`) — the form the
   library's containers take. A block on one instance conforms that instance alone. The
   signatures are checked at the block's target (`List<T>` with the block's `T`), as
   [§1](#1-interfaces-and-conformance) checks them at the type.
4. **Coherence** (X3, X4): one conformance per **type instance and interface instance** in the
   whole program, from whichever site — the type's own list, a block, a generic block. Two sites
   that could meet on one instance are refused where the second stands (`LYR-SEM0133`):
   `extend List<int> :: [Display]` beside `extend<T :: [Display]> List<T> :: [Display]`, a block
   beside the type's own declaration, two generic blocks over the same target. There is **no
   specialization**; two blocks on instances that never meet (`Box<int>`, `Box<string>`) stand.
   There is no orphan rule: a block may stand in any module.
5. *(Informative.)* A generic block's member is compiled per receiver instance, as a method of
   a generic type is; a table row for a conformance a block gives is built for the instances
   the program uses it on.
6. **The built-in constructors** (X2): `extend<T> T[] { … }`, `extend<T> ?T { … }`,
   `extend<T> Slice<T> { … }`, a tuple of fixed arity `extend<A, B> (A, B) { … }`, and the
   same at one element type, `extend int[] { … }`. The members are reached on every value of
   that **shape**, the shape binding the parameters as rule 2 says, the constraints checked
   the same way (`LYR-SEM0134`); `this` is the shape, so `this[0]` and `this.length()` stand
   in an array's block, `this == null` and `this!` in an optional's, `let (a, _) = this;` in a
   tuple's. `length()` stays the primitive ([03 §5](03-types.md)). An element of a tuple comes
   first, a block's member after. A shape **conforms** through a block that names the interface,
   `extend<T :: [Display]> T[] :: [Display] { … }` — every shape the block's constraints admit
   (rule 3), with the signatures checked at the shape, `Self` read as it (`LYR-SEM0020`,
   `LYR-SEM0042`). That is the one way a shape satisfies a constraint (`LYR-SEM0028`
   otherwise), and a member called through the constraint is the block's. Two blocks on
   overlapping shapes giving one interface — of either's chain — are two conformances
   (`LYR-SEM0133`). A value of the interface is not made from a shape yet (`LYR-SEM0047`).
7. **Blanket blocks** (04 D15): a block whose target is its own parameter, `extend<T :: [I]> T
   { … }`, adds its members to **every type its constraints admit** — the receiver binds `T`,
   `this` is the receiver: `x.greeting()` on every `Named`. A member of the type's own, of
   another block or of a default comes first; a blanket member of a name the type already has
   is refused at the block (`LYR-SEM0121`), and one the receiver's type does not admit is not
   there (`LYR-SEM0012`). In a generic body a type parameter whose constraints imply the
   block's receives it too (D2 R4). A shape receives a blanket member where it satisfies the
   block's constraints (rule 6). A member with type parameters of its own, `fn mapped<U>(…)`,
   is one function per receiver and per its own type arguments.
8. **Blanket conformance** (D15): `extend<T :: [I]> T :: [J] { … }` gives `J` to every type the
   constraints admit — the signatures checked at `T` — so a `Named` satisfies a constraint on
   `J` and a call through it is the block's member; a type it does not reach keeps its own.
   Such a block implements `J`'s whole chain, so it excludes, by interface: a type's own
   conformance to one of the chain where it reaches the type (X4); a shape's block giving one
   where it reaches the shape — the shape, or an overlapping one another block names, meeting
   its constraints, which a shape does through a block naming them alone (rule 6); and another
   blanket block giving one, even where no type could meet both (`LYR-SEM0133`). A value of
   `J` is not made through a blanket conformance yet (`LYR-SEM0047`).

## 14. Conformance synthesis

1. A conformance to one of the **family** — `Equatable`, `Hashable`, `Ordered`, `TotalOrder`,
   `Clone`, `Default`, `Display`, `Debug` — written in a struct's, class's or enum's own list
   **without the member** is **synthesized** from the fields (04 D7): `struct P :: [Equatable,
   Hashable] { x: int, y: string }` compares and hashes field by field, in declaration order.
   There is no `derive` word. A member the type writes itself replaces the synthesis for that
   member; the others are still synthesized. The list is fixed in 5.0; a synthesis of the
   program's own interfaces is [11](11-metaprogramming.md)'s question.
2. **Field by field, declaration order.** `equals` is the conjunction of the fields' equalities;
   `hash` mixes the fields' hashes in order; `compare` and `totalCompare` are lexicographic,
   the first field that is not `.Equal` decides, and a `compare` that meets `null` is `null`;
   `clone` copies the value fields and clones the reference fields — an array element by
   element, an optional's value, a tuple's elements; `default` takes every field's `default()`,
   or the field's own initializer where it has one, `[]` for an array, `null` for an optional
   and a tuple of its elements' defaults;
   `show` on request is the `debug` form; `debug` renders `P { x = 1, y = "a" }` with every
   field's `debug()`, an array as `[1, 2]`, an optional as its value or `null`, a tuple as
   `(1, "a")`, a string quoted and a char in single quotes. An **inline array** field is taken
   element by element.
3. **Enums** as structs, variant by variant: two values are equal when they are the same
   variant with equal payloads; the hash mixes the variant's position and its payload; the
   order is the **variant's position first**, then the payload lexicographically; `clone`
   rebuilds the variant; `debug` renders `E.B(3)`, `E.R { w = 4 }`, `E.A`. A `Default` of an
   enum is **refused** — no variant is the default (`LYR-SEM0135`).
4. **Generic types conditionally** (04 D7, Rust's derive bound): `struct Pair<T> :: [Equatable]`
   is `extend<T :: [Equatable]> Pair<T> :: [Equatable]`, so `Pair<int>` compares and
   `Pair<NoEq>` does not (`LYR-SEM0059` at the comparison, [§13](#13-generic-extends) rule 3);
   `Display` asks `Debug` of the parameters.
5. **The implied parents come along.** A type listing `Hashable` or `Ordered` alone gets
   `Equatable` synthesized too, `TotalOrder` brings `Ordered` and `Equatable` — unless the
   type lists them or writes their member. A conformance written in a block of its own beside
   such a list meets the synthesized one as two sites ([§13](#13-generic-extends) rule 4,
   `LYR-SEM0133`): list it, and the block is the one site.
6. **What is refused is said at the declaration.** A field whose type lacks the conformance
   the synthesis needs is an error at the type's conformance-list entry, the diagnostic of the
   missing operation prefixed with the synthesis it stands in and the field's line beside it
   (`note: synthesized as: && this.f == o.f`); a shape the synthesis has no form for — a
   `Slice<T>` or a function to `clone`, a function to `default` — is
   `LYR-SEM0135` with the field's type, and the member is written by hand.
7. **`Debug` is given unasked** to every struct, class and enum that writes none, **where the
   fields allow it**: a type holding an interface value, a function, or a type that has no
   `debug()` of its own gets none, silently — there was nothing asked and nothing to report —
   and `x.debug()` on it is `LYR-SEM0012`. Listing `Debug` asks, and then rule 6 names the
   field. `Display` is never automatic ([§12](#12-the-operator-interfaces) rule 8).
8. *(Informative.)* The synthesized member stands in an `extend` block of the type's own
   module, generated as source and compiled like one written; it is reached, overridden and
   qualified exactly as a block's member is. Hints about its style are nobody's to act on and
   are not reported.

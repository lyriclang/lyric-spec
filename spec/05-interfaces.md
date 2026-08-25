# 5. Interfaces and conformance

An interface declares instance methods — abstract (no body) or **default** (with body). Members
carry no `static`: dispatch goes through a method table, and a static member has no receiver.
An interface empty through its whole chain works as a **marker** — a constraint types conform
to (`std.core`'s attribute markers are exactly this) — but constructing a VALUE of it is
refused: there is nothing to dispatch on.

## 5.1 Declaring conformance

A struct, class or enum declares conformance in its interface list (`struct S :: [I, J]`), or a
module adds it through an extend block (`extend T :: [I] { … }`). **Every entry must be an
interface** (`LYR-SEM0078` since 2.15; before that a non-interface entry was skipped without a
word, so a declaration could claim a conformance nothing checked). Conformance requires one
matching implementation per abstract method of the interface — an own member or a visible
extension method (`LYR-SEM0020` otherwise, naming the implying interface when it came through a
chain) — with an **exact** signature match: arity, parameter types, return type, `mut`, and a
`throws` clause that is a subset of the interface's (`LYR-SEM0042`). Default methods may be
left unimplemented; an own member overrides a default.

A type conforms to a generic interface at specific arguments (`S :: [Eq<S>]`), and **since 3.0 it
may conform to one interface SEVERAL times** at different arguments: `Vec2 :: [Mul<Vec2, Vec2>]`
beside `extend Vec2 :: [Mul<float, Vec2>]`, or `Tag :: [Equatable<Tag>, Equatable<int>]`. Each
conformance is its own demand — conformance checking asks whether ANY visible method of the name
matches the signature THAT conformance wants, rather than the first one it finds — so two
conformances need two implementations, and one cannot answer both.

**A list may not repeat itself** (since 3.6.0): an entry naming what an earlier entry of the SAME
list already names, interface and arguments alike, is refused (`LYR-SEM0078`) — the list claims
two conformances where one exists, and there is nothing else it could mean. The rule reads the
ENTRIES, not their closures, and it holds for a parent list the same way. Everything reached twice
by other routes stays ONE conformance, deliberately: a parent written out beside its child
(`S :: [Hashable<S>, Equatable<S>]`, where the first entry's chain implies the second), a chain
arriving twice (§5.4), or an `extend` block declaring a conformance the type also declares itself.
The last one may stand in ANOTHER module — the orphan rule (§5.5) admits the interface's module —
and a library adopting a conformance that a downstream module had added by `extend` must not break
that module's build: a duplicate across declarations is redundant, never wrong.

What made several conformances possible is **overloading** (§4.3a), which arrived in the same
release: before it, two of them wanted two methods of one name on one type, and `LYR-SEM0042`
refused the second.

**Which implementation a call reaches** depends on what does the selecting, and every route has
something to select by: an operator picks the conformance by the type of its right operand (§6.1);
an ordinary member call picks by its arguments, as any overloaded call does (§4.3a), so a written
`v.mul(2.0)` resolves exactly where `v * 2.0` does; and an interface VALUE carries the instance it
was built for, so a value of `Equatable<int>` reaches the implementation that satisfied
`Equatable<int>` (§5.3, §5.4).

*(Through 3.0 this section named the four arithmetic interfaces of `std.core` as the single
exception to "one interface, once", on the reasoning that the operator's right operand is a
selector no other interface has and a member call therefore has only the NAME to go on. The
premise stopped holding in the release that wrote it — overloading gives a member call its own
selector — and the sentence describing `v.mul(2.0)` as ambiguous was wrong the day it shipped.
What is still true of `Add`, `Sub`, `Mul` and `Div` is that theirs is the only selection an
OPERATOR performs.)*

## 5.2 Interface inheritance

An interface may declare **parents**: `interface Labeled :: [Named]`, and since 2.16 more than
one. Conforming to the child implies conforming to every ancestor — abstract members of the
whole graph must be implemented, default methods of it are inherited, an ancestor constraint is
satisfied by the child, and throwability (`Throwable` anywhere above) carries through.

The list rules (`LYR-SEM0078`): only interfaces, and no cycles.

**Names must stay unambiguous** (`LYR-SEM0079`). Two rules, and they are the same rule seen from
two sides:

- a child may not redeclare a member it inherits — without override semantics the same call
  would dispatch differently through the child and through the ancestor;
- two parents may not contribute the same member name from DIFFERENT declarations — one slot
  cannot hold two methods, and no rule picks correctly between them.

A name reached twice through a **diamond** is not ambiguous and not refused: both paths lead to
one declaration, so there is nothing to pick. An implementation supplies it once.

*(Before 2.16 the list held one entry, on the reasoning that a parent's default method needs its
own slot indexes to remain valid behind a child-typed receiver. It does not: a vtable is keyed by
the pair (concrete type, interface), so every ancestor keeps its own numbering and nothing is
remapped. The rule was lifted after the reasoning was tested rather than repeated.)*

## 5.2a Members with type parameters of their own

Since 2.17 an interface member may declare type parameters: `fn map<U>(f: fn(T) -> U):
Iterator<U>`. Such a member is not dispatched — it is MONOMORPHIZED, like a generic function —
and three rules follow from that, all of them the same fact seen from different sides:

- **It must have a body.** A method table holds one function per slot, and a member with its own
  type parameters is one function per instantiation, so it gets no slot. An abstract one would
  promise a dispatch nothing can perform (`LYR-SEM0082`).
- **It may not be overridden.** Without a slot the target is chosen by the receiver's STATIC
  type, so an override would be reached through the concrete type and the default through the
  interface — one name, two functions (`LYR-SEM0082`).
- **It is reachable everywhere the ordinary members are**: through a constraint, and through an
  interface VALUE. The second is what a chain needs, and it is sound precisely because the first
  two rules make the default the only implementation.

**A caution that belongs to monomorphization rather than to interfaces.** A member without type
parameters whose result type is built from the interface's own — `fn chunks(): Iterator<T[]>` —
demands an instance for the next element type, and that one for the one after: the set of
instantiations is infinite and the compilation does not terminate. An implementation must report
this rather than run out of memory. A GENERIC member has no such problem, because it is
instantiated per use rather than per instance.

## 5.3 Interface values

A value whose static type is an interface is a **fat pointer**: a reference plus its method
table. Constructing one is the assignment of a CONCRETE conforming value to an interface-typed
location; scalars cannot be interface values (no reference), and structs, classes and enums
can. Calls through an interface value are the language's **only dynamic dispatch**.

An interface value answers every member of its interface's chain. It does **not** convert to
another interface type — the parent included: implication holds for the implementing type, not
for fat pointers. Take the concrete value through the parent where a parent-typed value is
needed.

*(Through 2.16 this section carried an implementation limit: instances whose slot signatures hold
non-primitive or function-typed values could not be interned, and generic interface defaults had
no lowering. Both fell with 2.17 and 3.0 — the conformance suite runs interface values over
struct-typed, function-typed and default-method slots — and the limit is recorded here only so a
reader of old modules knows it existed.)*

## 5.4 Resolution order

Member resolution on a concrete type is fixed at compile time, in this order: own member, then
visible extension method, then a default method of a conformed interface's chain. Two defaults
for one name from UNRELATED interfaces are an ambiguity error (`LYR-SEM0043`) asking for an
explicit override; the same interface reached twice through a chain is one conformance, not
two. The chosen target stands in the compiled module — a vtable row holds function indices, and
the runtime searches nothing.

A row is built per interface INSTANCE (§5.1) and holds the implementation that satisfied THAT
conformance: the one whose signature matched, not the first member of the name. Since 3.0.1, and
the difference is visible only where one type satisfies two conformances with two overloads of a
name declared on the type ITSELF — where the two live apart, one an own member and one in an
extend block, a lookup by name lands on the right one by accident.

## 5.5 Extend blocks and the orphan rule

`extend T { … }` adds methods to any visible type, builtins included; such method-only blocks
are unrestricted. `extend T :: [I] { … }` additionally declares conformance and is
**orphan-checked**: the extending module must declare `T` or one of the `I` itself
(`LYR-SEM0041`). The rule looks at the interface, not its type arguments.

Extension methods are visible where the declaring module is imported (§4.2). A static extension
method belongs to the type; calling it through an instance is an error since 2.0
(`LYR-SEM0074` — a warning through 1.x, the one severity change of the major, §12.1).

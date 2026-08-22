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

A type conforms to a generic interface at specific arguments (`S :: [Eq<S>]`) and can conform
to one interface only once: a second conformance at different arguments fails the signature
match — one method cannot have two signatures. *This is why heterogeneous operator arithmetic
does not exist (chapter 6).*

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

## 5.3 Interface values

A value whose static type is an interface is a **fat pointer**: a reference plus its method
table. Constructing one is the assignment of a CONCRETE conforming value to an interface-typed
location; scalars cannot be interface values (no reference), and structs, classes and enums
can. Calls through an interface value are the language's **only dynamic dispatch**.

An interface value answers every member of its interface's chain. It does **not** convert to
another interface type — the parent included: implication holds for the implementing type, not
for fat pointers. Take the concrete value through the parent where a parent-typed value is
needed.

*Implementation limit (diagnosed, `LYR-IR0001`):* instances of generic interfaces whose method
signatures carry non-primitive or function-typed slots cannot yet be interned as values, and
generic default methods have no lowering; both are compile-time refusals, never silent.

## 5.4 Resolution order

Member resolution on a concrete type is fixed at compile time, in this order: own member, then
visible extension method, then a default method of a conformed interface's chain. Two defaults
for one name from UNRELATED interfaces are an ambiguity error (`LYR-SEM0043`) asking for an
explicit override; the same interface reached twice through a chain is one conformance, not
two. The chosen target stands in the compiled module — a vtable row holds function indices, and
the runtime searches nothing.

## 5.5 Extend blocks and the orphan rule

`extend T { … }` adds methods to any visible type, builtins included; such method-only blocks
are unrestricted. `extend T :: [I] { … }` additionally declares conformance and is
**orphan-checked**: the extending module must declare `T` or one of the `I` itself
(`LYR-SEM0041`). The rule looks at the interface, not its type arguments.

Extension methods are visible where the declaring module is imported (§4.2). A static extension
method belongs to the type; calling it through an instance is an error since 2.0
(`LYR-SEM0074` — a warning through 1.x, the one severity change of the major, §12.1).

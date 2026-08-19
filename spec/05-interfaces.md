# 5. Interfaces and conformance

An interface declares instance methods — abstract (no body) or **default** (with body). Members
carry no `static`: dispatch goes through a method table, and a static member has no receiver.
An interface with no methods anywhere in its chain is an error at compilation: there is nothing
to dispatch on.

## 5.1 Declaring conformance

A struct, class or enum declares conformance in its interface list (`struct S :: [I, J]`), or a
module adds it through an extend block (`extend T :: [I] { … }`). Conformance requires one
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

An interface may declare **one parent**: `interface Labeled :: [Named]`. Conforming to the
child implies conforming to the whole transitive chain — abstract members of the chain must be
implemented, default methods of the chain are inherited, a parent constraint is satisfied by
the child, and throwability (`Throwable` in the chain) carries through.

The chain rules (`LYR-SEM0078`): at most one parent — several requirements side by side are
what constraints are for (`<T :: [A, B]>`); only interfaces in the list; no cycles. A member
name may occur once per chain (`LYR-SEM0079`): redeclaring an inherited member is refused
rather than given override semantics, so the same call can never dispatch two ways.

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
method belongs to the type; calling it through an instance warns as deprecated
(`LYR-SEM0074`) and becomes an error at 2.0.

# 3. Types

**Base.** Lyric 5.0 [§3](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/03-types.md) applies, with the deviations below.

**Status.** The core (S2), the optionals, `var x = null`, tuples, enums with payloads, function
values, generics and `with` (S3) written; the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

## Written (S2, the core)

1. **Scalars.** `int` is 64 bits, `float` 64 bits; `bool` and `char` are Lyric 5's. A width type
   of Lyric 5 — `int8` … `int64`, `uint`, `uint8` … `uint64`, `float32`, `float64` — is refused
   where it is named (`LYS-SEM0900`) ([03 K3](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
2. **Widening.** An `int` value where a `float` is taken — a binding, an argument, a field, a
   return, a branch of an `if` beside a `float` one — is widened; nothing narrows on its own
   (`LYS-SEM0001`) ([03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
3. **Structs and classes.** A struct's fields are never written: an assignment to one is refused
   (`LYS-SEM0019`), and so is `var` on one (`LYS-SEM0901`). A class is the mutable reference: its
   `var` fields are written by any code that holds it, its methods without `mut fn` (§7).
4. **Omitted return types** (Kotlin's rule, [09 Ret](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)): `fn f(…) = e`
   has the type of `e`; a block body without a written type is `void`. A function whose type
   depends on itself through its own body is refused until the type is written (`LYS-SEM0010`).
5. A code means what Lyric 5's `LYR-SEM` code of the same number means; Lyric-Script's own
   codes start at 0900 (§16). `LYS-NYI0001` names a form a later milestone of the
   plan builds; it leaves the toolchain before 1.0.

## Written (S3)

6. **Optionals.** Lyric 5 §3.1–3.3 apply as written: `?T` and `??T`, `null`, `!` (on null the
   panic `LYS-RT0004`), `??`, `?.`, `??=`, `== null`, narrowing after a test and after a branch
   that never comes out, `if let`, `while let`. The codes are Lyric 5's: a null operator on a
   value that is never null is `LYS-SEM0005`, `== null` there `LYS-SEM0059`, an assignment
   through `?.` `LYS-SEM0019`.
7. **Narrowing ends at a write** (Lyric 5 §3.2). An assignment to a narrowed binding ends its
   narrowing; a loop that writes it has it narrowed in none of its turns. A module-level `var` is
   never narrowed — a script's top-level bindings are the module's (§7) — and a module-level
   `let` is narrowed like a local.
8. **`var x = null`** without a written type takes the type of the first use in its function
   — the script's code counting as one — that fixes one: an assignment or a `??=` of a value of
   type `T` (or `?T`), or the binding standing where a type `?T` is taken (an argument, a
   return, a typed binding, a field). `x` is then a `?T` from its declaration on, and every use
   is checked as such: uses before the fixing one in the source are allowed where they fix
   nothing (`x == null`) and checked against `?T`. Where nothing in the function fixes the type,
   the declaration is refused with the type to write (`LYS-SEM0010`); `let x = null` is refused
   so too, as in Lyric 5. Lyric 5 infers no binding from a later use ([03 Leer](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
   `var xs = []` and `let xs = []` take the same way (S7b2b): the first use that fixes a list
   type — a push of a `T`, an assignment of a `T[]`, the binding standing where a `T[]` is
   taken — makes it a `T[]`; nothing fixing it is `LYS-SEM0010`. `[:]` follows with the maps
   (S7d).
9. **Tuples.** Lyric 5 §6 rules 1–5 apply: `(A, B)` from two elements (`(1,)` is refused,
   `LYS-PAR0010`); labels `(x: A, y: B)`, no part of the type and seen through the type they
   were written on; `t.0` and `t.x` (`LYS-SEM0012` for an element the tuple lacks); elements
   never written (`LYS-SEM0019`); `let (a, b) = t` and `var (a, b) = t`, nested and with `_`
   (`LYS-SEM0058` where the pattern does not fit, `LYS-SEM0097` for a name twice); a literal
   takes the types an expected tuple gives its elements, and an element that gives no type of
   its own where none is expected is refused (`LYS-SEM0010`). Rule 6 — equality, hashing,
   display — comes with the synthesis (S3h), `for ((a, b) in …)` with the collections (S7).
10. **Enums with payloads.** Lyric 5 §4.1 rules 1–2 and §4.2 apply: tuple variants
   `Num(int)` and struct variants `Rect { w: int, h: int }` beside unit ones, built as
   `Shape.Num(3)`, `Shape.Rect { w = 1, h = 2 }` and `Shape.Empty`, a payload read by a pattern
   only; `.Red`, `.Num(3)` and `.Rect { … }` where the position expects the enum, else refused
   (`LYS-SEM0113`). Unlike Lyric 5 (§4.1 rules 3–4) an enum with a payload is a **reference** to
   an immutable value, as a struct is (rule 3): it holds itself without a box —
   `enum Tree { Leaf(int), Node(Tree, Tree) }`.
11. **Function values.** Lyric 5 §8.1–§8.4 and §8.6 apply, without `inline fn` (§8.5) and,
   until the errors come (S4), without `throws` in a function type: `fn(A, B) -> R`; lambdas in
   the three forms — `(n: int): int => n + 1`, `x => x * 3`, a trailing block with `it` or its
   parameters named before `=>` — their parameters' types written or from the position
   (`LYS-SEM0045`), a `return` in one whose result nothing gives refused (`LYS-SEM0010`); a free
   or static function named without a call, and `obj.method` bound to `obj`; a call through any
   value of a function type, a field's included (`LYS-SEM0013` on what is none); captures — a
   `let` copied, a `var` in a box both sides share, fresh in each pass of a loop (02 C1),
   `this` copied; a local `fn` that calls itself. Two function values are not compared
   (`LYS-SEM0059`). A brace after a name that is no type's opens a trailing block (§2 D4).
12. **Generics.** Lyric 5 §9.1 rules 1–3 and 5 and §9.2 rules 1–4 apply to functions, structs,
   classes and enums: `fn f<T :: [C]>(…)`, `struct Pair<A, B> { … }`; a method of a generic
   type, of every list (`extend<T> T[]`) or of an interface may have type parameters of its own,
   `fn map<U>(f: fn(T) -> U): Box<U>` — the receiver binds its owner's, a call's arguments the
   method's (S7c4c1); a generic type may be named with its arguments before its declaration,
   `fn f(b: Box<int>)` above `struct Box<T>` (S7c4c3b); a type parameter may carry a **default**,
   `interface Add<Rhs = Self>`, `struct Pair<A, B = A>` (§9.1 rule 5; S7c5c1): a use that writes
   fewer arguments — of a type, of an interface, at a call — takes the trailing defaults, read
   where the generic is declared, `Self` the conforming type in a conformance and the parameter in
   a constraint, so `V :: [Add]` is `V :: [Add<V>]` (`LYS-SEM0026` where one without a default is
   left out); `Coroutine<Y>` is `Coroutine<Y, void>` so (10); an extend block's parameters take
   none, its target binds them (`LYS-SEM0026`); a generic is checked once,
   a value of `T` has its constraints' members and no others (`LYS-SEM0012`); the arguments of a
   call bind the type parameters at any depth, a lambda's after the others, what they leave open
   the type the call's position expects, never overriding them (§9.2 rule 2; S7c4c2): `let xs:
   int[] = empty()`; what nothing binds is refused (`LYS-SEM0060`), as is an argument its
   constraints do not admit
   (`LYS-SEM0028`) and a wrong count (`LYS-SEM0026`). An initializer of a generic type binds its
   arguments from its fields' values or takes the instance the position expects; a unit variant
   of a generic enum takes it from the position. Type arguments may be written at a call,
   `none<int>()` (§9.2 rule 4), and at a method, `it.collect<int[]>()` — its own, after those its
   receiver binds, as many as it declares (`LYS-SEM0026`; S7c4c2); the placeholder `_` among
   them comes with S7c6. A `<` after a name or a member opens them where its matching `>`
   is followed by what no comparison goes on with — `(`, a closer, `,`, a line end, `.`, `==`,
   `!=`. A generic function is a value at its type arguments, written, `id<int>`, or bound by
   the position's function type, `let g: fn(string) -> string = id` (`LYS-SEM0060` where
   nothing gives them). `Self`, static and associated members are 05's (rules 10–11).
   Unlike Lyric 5 (§9.1 rule 4), an instance is not compiled per argument list: the types whose
   values are objects of the VM share one copy, whose constraint calls go through the value's
   table; every other type has a copy of its own (11 Gen). The arguments are not lost to the
   sharing: what a shared copy builds is of the exact type its arguments make — `wrap(Foo { })`
   of `fn wrap<T>(x: T): Box<T>` is a `Box<Foo>` —, and `x is T` on an interface value tests the
   argument, as in Lyric 5's copy for it — in a lambda of the copy too.
13. **`with`.** Lyric 5 §2.5 applies as written: `p with { x = 3, pos.y = 4 }` is a copy of
   the struct `p` with the named fields replaced, its values left to right over the old `p`, after
   `p` itself; a path reaches into the structs `p` holds; on a class, a tuple or an enum refused
   (`LYS-SEM0116`), a field twice (`LYS-SEM0070`) or unknown (`LYS-SEM0015`) too; a postfix, and
   as a statement a value thrown away (`LYS-SEM0022`). A struct is shared and never changed
   (rule 3), so the copy is a new object, and so is each struct a path reaches; a path after its
   field was replaced whole changes the new value, as Lyric 5's stores into the copy do.
14. **Literal protocols** ([03 Lit](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)): the prelude declares `FromIntLiteral`,
   `FromFloatLiteral`, `FromStringLiteral`, `FromBoolLiteral` and `FromNullLiteral`, each with a
   static member named for its kind — `static fn fromIntLiteral(v: int): Self`, …,
   `static fn fromNullLiteral(): Self` —, since one type may take several and functions are told
   apart by their count (Lyric 5 §8.1.2). A literal where its place's type conforms — a binding's,
   a parameter's, a field's, a return's, an optional's value type, a type parameter's — is built
   by that type's member: `let m: Money = 5` is `Money.fromIntLiteral(5)`. Only a literal is: a
   value of a variable is never converted (`LYS-SEM0001`), and `null` where an optional is taken
   stays the optional's `null`. `FromArrayLiteral<T>` (S7c2; Lyric 5 10 K4, its member named by
   this rule's kind, `static fn fromArrayLiteral(items: T[]): Self`): a list literal where its
   place's type conforms is a list of `T`, its elements checked against `T`, given to that member
   — `let b: Bag = [1, 2]`, also through a type parameter `B :: [FromArrayLiteral<int>]`.
   `FromMapLiteral` comes with the maps (S7d).
15. *Informative.* The VM holds a `?T` of a reference type as the reference, `null` as none; any
   other `?T` as the slots of `T` and one presence slot after them; a tuple as its elements'
   slots in order, inline; an enum without payloads as an `int`, one with payloads as an object
   of a VM type per variant whose first scalar is the variant's number; a function value as an
   object whose first scalar names its function and whose fields hold its captures, called by
   `call.v`
   ([11 V2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)).
   Every type has a descriptor, a value of the VM that carries its template and its arguments'
   descriptors. A shared copy gets the descriptors of its arguments as hidden parameters — a
   method of a generic type reads them from its receiver's, since a call through an interface
   value does not know them —, and a type it builds is interned at run time, so that two
   descriptors of one type are one (`load.t`, `inst.t`, `desc.of`, `new.d`, `is.d`).

## Written (S7, the core collections)

16. **Lists** ([03 S](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)). `T[]` is the one sequence type, a list that grows;
   `List<T>` names the same type. `[a, b, c]` is a list of the type its place gives, else of its
   elements' type — an `int` among `float`s is a `float` ([03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)) —, and
   every element must fit it (`LYS-SEM0001`); `[]` takes its type from its place. A list is a
   reference: `let xs = [1]` binds the list for good, and `xs.push(2)` grows it. `length()` is
   its number of elements, `push(v)` appends `v`, `pop()` takes the last element off and gives
   it, `null` where the list is empty. A list's text is its Debug form, `[1, 2, 3]`, each element
   in its own (`["a", "b"]`). The other methods are Lyric 5's `List` and slice methods without
   the views (Lyric 5 §10; [12](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)): `isEmpty()`, `get(i)` and `first()`, `last()` (`null`
   outside), `pushAll(xs)`, `insert(i, v)` (a panic, `LYS-RT0003`, outside `0..=length()`),
   `removeAt(i)`, `removeWhere(p)` (how many went; where `p` throws, the rest stays in order),
   `clear()`, `truncate(n)` (a negative `n` panics), `swap(i, j)`, `reverse()`, `reversed()`,
   `fill(v)`; and where the elements compare — `==` is defined on them ([03 Eq](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)) —
   `contains(x)`, `indexOf(x)`, `remove(x)`, `dedup()`, else they are not there
   (`LYS-SEM0134`). `xs + ys` is a new list of both, `xs * n` one of `n` times the elements (a
   negative `n` panics); `x in xs` and `x !in xs` ask `contains`; `xs == ys` compares the lengths,
   then the elements in order (`LYS-SEM0059` where they do not compare). The comparing methods
   are the prelude's block `extend<T :: [Equatable]> T[]`, so over a type parameter `T ::
   [Equatable]` they are there too ([05](05-interfaces.md) rule 8; S7c5a). An empty
   literal no place gives a type comes with S7b2b; sorting with S7c. Every list is an
   `Iterable` (S7c4a): `xs.iter()` gives an iterator over it, which panics as the loop does
   after a change of the list's length (`LYS-RT0016`). A list is an interface
   value (S7c3) — an `Any`, or of an interface `extend<T> T[] :: [I]` gives it — in a box of its
   type's own, so `x is int[]` tells it and `{x}` prints its Debug form; a list of a type
   parameter is one too, in the box of its copy's element — a shared copy makes its descriptor
   where it runs —, and `x is T[]` tests it (S7c4c3b). Every list is a `FromIterator` of its
   element (S7c4c2): `let xs: int[] = it.collect()` ([07](07-statements.md) rule 7).
17. *Informative.* The VM holds a list as one object with the scalar and the reference slots of
   its elements apart: a list of `int` holds its ints unboxed, a list of tuples their slots in
   order (`list.new`, `list.push`, `list.get.*`, `list.set.*`, `list.len`, `list.pop`).

## Deviations (skeleton, written with later milestones)

- Scalars `int` (64-bit), `float` (64-bit), `bool`, `char`; no width family; `Bytes` and `BigInt` in `std`; `int` widens to `float` ([02 T1](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03 Mix](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- `struct` values are always immutable (`with`), `class` is the mutable reference; recursive structs need no `Box`; no `&T` ([02 T7](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- One sequence type `T[]` that grows (`List<T>` an alias), copying slices; no `Slice`; `StringView` an alias of `string` ([03 S, Str](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md)).
- No unions; optionals as in Lyric 5; literal protocols for every literal kind; empty literals typed by their first use in the function; Kotlin's rule for omitted return types ([02 T4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [03](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [09 Ret](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).
- Structs, enums and tuples are `Equatable`/`Hashable` without asking when their fields are; `{x}` falls back to `Debug`; `float` is `TotalOrder`; `Map`/`Set` iterate in insertion order ([03 Eq](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/03-werte-und-typen.md), [05 Fl](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/05-abstraktion-und-fehler.md), [01 S8](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).

**Conformance.** `conformance/cases/03-types/` (`since: 1.0.0`).

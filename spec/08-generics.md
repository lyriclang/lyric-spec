# 8. Generics

## 8.1 The model: monomorphization

A generic declaration is a template. Every use at a distinct tuple of type arguments produces
its own type or function, with its own layout and its own compiled body — `Box<int>` and
`Box<string>` share nothing at runtime. This is the model, not an optimization: a Lyric value
carries no type tag, so nothing generic can exist at runtime.

Consequences the language commits to:

- constrained calls are DIRECT calls after monomorphization — a `T :: [Display]` costs nothing
  at the call site;
- a generic function or type cannot cross a runtime boundary un-instantiated: a generic
  function is not a function value (`fn` values are monomorphic — using one as a value is a
  type error, since its unsubstituted signature fits no function type), and attributes sit on
  generic declarations only in the one row-less case (`@Deprecated`);
- instantiation is demand-driven from the roots; unreachable instantiations do not exist in
  the module;
- every instantiation chain must be FINITE. Polymorphic recursion — a function reaching itself
  at a larger type, `deeper(Box { v = x })` inside `deeper<T>(x: T)` — is refused at compile
  time, in whichever form it is written: the inferred construction has no known instance at
  the call (`LYR-SEM0026` — field values never drive construction inference, §8.2), and the
  explicit `Box<T> { v = x }` leaves an instantiation open that no finite set of instances
  closes, which the lowering refuses (`LYR-IR0001`). The member-shaped twin — a non-generic
  interface member whose result type demands an unbounded instance chain — is §5.2a's caution,
  refused the same way.

**Generics and overloading are two answers to one question**, and since 3.0 the language has
both. They are not interchangeable: a generic function is ONE function that serves every type
satisfying its constraints, and an overload set is SEVERAL functions that happen to share a name.
Where both could apply, the concrete parameter wins (§4.3a) — a function written for this type
says more about a call than one written for every type.

## 8.2 Constraints

`<T :: [I, J<T>]>` — a type parameter carries interface constraints. Inside the declaration,
`T` has exactly the union of the constraint interfaces' chains as its member surface
(`LYR-SEM0027` otherwise). At the call site every argument must satisfy every constraint
(§5.1, §5.2 — a child interface constraint is satisfied through its chain); the checker
resolves constraints against the FULL argument mapping, so `<K, V :: [Map<K, V>]>` works.

A generic CONSTRUCTION infers its type arguments by its own rule, by decision: they come from
written arguments (`Box<Meters> { v = m }`) or from the expected type of the position
(`let b: Box<int> = Box { v = 5 };`), never from the field values — a contextless
`Box { v = 5 }` is `LYR-SEM0026`, not an inference. An enum variant follows the construction
rule: `let o: Opt<int> = Opt.Some(7);` names its instance on the left.

## 8.3 Inference at a call

A generic function's type arguments are inferred from its value arguments. The rules, in the
order they apply:

1. **What is written wins.** Explicit type arguments (`total<int>(…)`) bind their parameters
   before any argument is looked at; the count must match the declaration (`LYR-SEM0026`), and
   the written arguments must satisfy their constraints (`LYR-SEM0028`) — the explicit form is
   not a way around them. Inference only fills what writing left open, so `id<int>("x")` is
   the ordinary assignment error at the argument, never a silent `id<string>`.

2. **Non-lambda arguments are typed first, eagerly.** An argument standing at a CONCRETE
   parameter is typed with that parameter as its context, so a literal adapts (§3.1) and
   `f(Opt.Some(5))` names its instance. At a parameter that mentions a type parameter there is
   no context: nothing may fix what this very argument is supposed to determine.

3. **Binding is structural.** A parameter type is run against its argument type by shape,
   descending into parts: a bare `T` binds the argument type; `T[]` against `int[]` binds the
   element, likewise `?T`, a tuple of the same arity, `fn(T) -> U` against a function type, an
   instance of the same generic declaration argument by argument, and `Coroutine<T>` against a
   coroutine. The FIRST binding of a parameter stands; a later argument that contradicts it
   fails as the ordinary assignment error AT that argument — `pair(1, "x")` against
   `pair<T>(a: T, b: T)` reports the `"x"` — which is deliberate: the mismatch is reported
   where the mismatching value stands, not as a sentence about inference.

4. **A conformance may carry the binding** where shapes cannot. At a parameter whose type is
   an instance of a generic INTERFACE (`fn find<T>(it: Iterator<T>)`), an argument with no
   structural similarity binds through its declared conformance to that interface — the
   connection stands in the argument's declaration, not in its shape. Since 3.6.0, an argument
   type that conforms to that interface SEVERAL times (§5.1) does not choose: the call is
   refused (`LYR-SEM0092`), and writing the type argument settles it, by rule 1. *(Through 3.5
   the first conformance in declaration order won, silently — the same call compiled or failed
   depending on the order of a `::` list, which is behavior nothing should have depended on.)*

5. **Lambda arguments are typed last**, with the substituted parameter type as their context —
   which is what lets a lambda's parameters go unannotated — and their actual types bind the
   parameters still open: the classic `U` bound from a lambda's return.

6. **What remains unbound is refused** (`LYR-SEM0060`): write it explicitly, `empty<int>()`.
   The expected type of the CALL's position binds nothing for a function — a no-argument
   factory is not callable bare, however annotated the binding it stands in. Construction is
   the deliberate exception, §8.2: a struct initializer or enum variant does read the expected
   type, because a construction names what it builds.

7. **Constraints are checked against the full inferred mapping** (`LYR-SEM0028`), after all
   binding is done.

## 8.4 Generic statics and instances

A static member of a generic type is called with the type's arguments written
(`List<int>.empty()`; `LYR-SEM0063` otherwise) and substitutes the caller's own type parameters
where they appear. Methods of a generic type belong to the INSTANCE: `Box<int>.get` and
`Box<string>.get` are two functions.

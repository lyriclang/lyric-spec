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
  function is not a function value (`fn` values are monomorphic), and attributes sit on
  generic declarations only in the one row-less case (`@Deprecated`);
- instantiation is demand-driven from the roots; unreachable instantiations do not exist in
  the module;
- every instantiation chain must be FINITE: polymorphic recursion — a function reaching itself
  at a larger type, `deeper(Box { v = x })` inside `deeper<T>(x: T)` — is refused at the call,
  because monomorphizing it would not terminate.

## 8.2 Constraints

`<T :: [I, J<T>]>` — a type parameter carries interface constraints. Inside the declaration,
`T` has exactly the union of the constraint interfaces' chains as its member surface
(`LYR-SEM0027` otherwise). At the call site every argument must satisfy every constraint
(§5.1, §5.2 — a child interface constraint is satisfied through its chain); the checker
resolves constraints against the FULL argument mapping, so `<K, V :: [Map<K, V>]>` works.

Type arguments are inferred from value arguments in two phases — eagerly typed arguments bind
first, lambda returns bind what remains — and can always be written explicitly
(`total<int>(…)`). A generic CONSTRUCTION infers differently, by decision: its type arguments
come from written arguments (`Box<Meters> { v = m }`) or from the expected type of the
position, never from the field values — a contextless `Box { v = 5 }` is `LYR-SEM0026`, not
an inference.

## 8.3 Generic statics and instances

A static member of a generic type is called with the type's arguments written
(`List<int>.empty()`; `LYR-SEM0063` otherwise) and substitutes the caller's own type parameters
where they appear. Methods of a generic type belong to the INSTANCE: `Box<int>.get` and
`Box<string>.get` are two functions.

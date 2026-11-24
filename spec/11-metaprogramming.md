# 11. Metaprogramming and reflection

**Base.** Lyric 5.0 [§11](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/11-metaprogramming.md) applies, with the deviations below.

**Status.** The attributes' syntax and the compiler's closed list written (S8f1); data attributes and
reflection come with S10, the list's other members with S11 — until then the design documents decide.

## Written (S8f1, attributes)

1. **Attributes** ([09 At](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)). `@Name` or `@Name(args)` stands before a function, a
   type, an enum or an interface, and in a body before a method (S8f3a), on its own line or before
   the declaration on the same, as many as it has; before anything else — a statement, an `import`,
   an `extend`, a field — or at the end of a file it is `LYS-PAR0042`. The compiler knows a closed list; a name not on it is `LYS-SEM0011`. An
   argument is a compile-time value — a literal, a string without holes, a variant without a
   payload — or `LYS-SEM0066`; the same attribute twice on one declaration is `LYS-SEM0068`. The
   list's first member is `@Requires`, which belongs to a module of the host (chapter 13) and
   elsewhere is `LYS-SEM0065`.

## Deviations

- No `comptime`, no macros, no `inline fn` ([02 W](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md)).
- Read-only reflection at run time; function values as `Any`; data attributes readable at run time; the closed compiler-attribute list without `@When`, `@Export` and the inline hints ([09 Rf, At](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/09-syntax-und-reflexion.md)).

**Conformance.** `conformance/cases/11-metaprogramming/` (`since: 1.0.0`).

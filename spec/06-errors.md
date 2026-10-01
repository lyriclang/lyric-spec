# 6. Errors

A function that can fail says so in its signature, a call of it is marked where it stands, and
what it throws is caught or passed on by a function that says so in turn — two channels, the
value and the error, each in plain sight
([05 E1–E12](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/05-fehler.md),
[01 L5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md),
[08 D9, D18, Y4, Y5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)).

## Scope

What is thrown, the `throws` set, the `try` mark and what covers a thrown type. Written with M5
S1a; the chapter grows with the milestone's slices — throwing and propagating at run time and
`main`'s report (S1b), `catch` with its clauses, `try?` and `try!` (S2), `defer` on the error
path and `using` (S3), panics, `never` and the thrown set of a function type (S4). What is not
written here yet is decided in the design documents, not here.

**Conformance.** `conformance/cases/06-errors/`.

## 1. What is thrown

1. **`Error`** of `std.core` is the root of everything thrown, caught and declared:
   `interface Error { fn message(): string; fn cause(): ?Error { return null; } }` (05 E6 O1).
   `cause` names the error this one wraps; the wrapping is the type's own field (O2).
2. A value is **throwable** when its type conforms to `Error` (E3): a struct, a class or an enum
   that conforms, an interface value of `Error` or of an interface extending it, a type
   parameter constrained to it. An enum is the natural form —
   `enum ParseError :: [Error] { Empty, BadDigit(char, int); … }`. Anything else — a number, a
   string, an array, an optional — is not (`LYR-SEM0030`).
3. `throw e` throws `e`; it is a statement, or an expression of type `never` wherever an
   expression may stand (`x ?? throw NotFound { }`). `e` is throwable (`LYR-SEM0030`).

## 2. The `throws` set

1. A function that may throw declares it after its return type: **`throws E`** for one type,
   **`throws [A, B]`** for several — a **set**, in brackets from two on like every list
   ([08 D5/D6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)); two
   without the brackets are refused (`LYR-PAR0049`). The order means nothing; a type named
   twice is refused (`LYR-SEM0137`). Every element is throwable (`LYR-SEM0030`).
2. The bare **`throws`** is `throws Error`: anything may be thrown, and the caller learns what by
   testing the value's type. The list is the form to prefer.
3. The set is **declared, never inferred**, for a named function (K3). A function without a
   clause throws nothing.
4. An implementation of an interface member throws **at most** what the member declares: every
   type of its set is covered by the member's ([§3](#3-the-try-mark-and-coverage) rule 4, K6) —
   `LYR-SEM0042` otherwise.
5. `fn main()` may declare `throws` ([08 D18](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)),
   like any function; its return type is `int` or `void`, with or without `args: string[]`
   (`LYR-SEM0021`).
6. *(Informative.)* A function value of a throwing function and a lambda that throws wait for
   the thrown set of a function type (T17); until then the former is refused (`LYR-SEM0037`) and
   a lambda's body catches what it calls.

## 3. The `try` mark and coverage

1. Every call of a throwing function is **marked**: it stands under **`try`** — the prefix
   `try e`, or the body of a `try { … }` block — of its own function (`LYR-SEM0138`). A
   refactoring that makes a function throw shows at every caller instead of passing through
   unseen (E1). A lambda's body is a function of its own: a `try` around the lambda does not mark
   what its body calls.
2. `try` **covers everything to its right**: `try a + b` is `try (a + b)` and marks every call in
   it ([08 Y4](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md)). It
   therefore stands at the **start** of the expression it covers — a binding's value, an
   argument, a `return`, the right of an `=` — and to the right of another operator it is
   refused (`LYR-PAR0050`): `1 + try f()` is written `try 1 + f()`. The value and the type are
   the expression's. A `try` under which nothing throws is warned about (`LYR-SEM0139`), as is a
   `try` block whose body throws nothing.
3. Every type a site may throw — a marked call, or a `throw` — is **covered** (K8): by a `catch`
   clause of a `try` block around the site (written with S2), or by the `throws` set of the
   function the site stands in (`LYR-SEM0034`). A global's initializer and a default cover
   nothing.
4. An element **covers** a thrown type when it **is** that type — on the instance: `Box<int>`
   does not cover `Box<string>` (K5) — or when it is an interface the type conforms to. `Error`
   covers everything thrown.
5. A call throws its function's set **in the instance's terms**: a method of `Box<int>` declared
   `throws Wrong<T>` throws `Wrong<int>`.

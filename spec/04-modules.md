# 4. Modules, names, and capabilities

## 4.1 Modules and headers

A module is one source file. The header `module a.b.c;` is optional: in an entry file the module
name comes from the file name; in a file reached through an `import`, the name is the imported
path, and a header disagreeing with it is an error. Two modules claiming the same name are an
error with a note at the first claim (`LYR-RES0007`).

Module resolution maps a dotted path to a file below a **root**: the project root
(`lyric.json`), the standard-library root, or a host-declared native root. A cycle in the import
graph is an error (`LYR-RES0005`).

## 4.2 Imports and visibility

Only `pub` declarations cross a module boundary. Three import forms exist:

- `import a.b { x, y };` — binds the selected names;
- `import a.b;` — binds the module's last segment as a namespace (`b.x`). If that segment
  shadows a builtin type name, the import warns (`LYR-SEM0077`) and using the shadowed name as
  a type is an error naming the trap;
- `import a.b as n;` — binds `n` as the namespace.

Importing a module — under any form — also makes its **extension methods** visible (§5.5): the
methods come with the module, not with a name. An import counts as used when one of its names is
referenced OR one of its extension methods resolves in the file; otherwise it warns
(`LYR-SEM0072`). `import std.string as strings;` is the idiom for a file that wants only the
methods.

## 4.3 Declaration order and globals

Declarations within a module are order-independent (two-pass resolution), with one exception:
module-level `let` initializers run in a fixed order, and an initializer reading a global that
comes later is an error (`LYR-SEM0057`). There is no module-level `var`.

The order is the DEPENDENCY order across modules and the source order within one: a module's
globals are initialized after those of every module it imports, transitively, and then top to
bottom. An initializer may therefore read what its own module declared above it, and anything from
a module it imports. **Since 2.8** — before it the order across modules was the one the entry file
happened to discover them in, which made a third module decide whether a second one compiled.

An import cycle has no such order and is refused for its own reasons (`LYR-RES0005`), so the
question does not arise. Which module is compiled as the entry does not enter into it: a file that
compiles as part of a program compiles on its own.

**A global is immutable to the PROGRAM, not to a host.** An implementation offering the embedding
API may let its host read and write the slots of a loaded module from outside — since 3.2 the
reference implementation does, and a debugger's Globals scope is what it is for. Nothing checks
the type on the way in: a slot is a bit pattern, the program reads it as whatever its instructions
expect, and the module's own table says what stands where (§13, Globals).

## 4.3a Overloading

**Since 3.0**, several functions may share one name, and are told apart by their PARAMETERS. This
is the language's second answer to "one name, several types" — generics with constraints being the
first — and it was admitted deliberately, which is why its rules are written out here rather than
left to the implementation.

**What may overload.** Free functions, methods of a struct, class or enum — `static` ones
included, where the call names the TYPE rather than standing on a value of it (`Id.of(7)` beside
`Id.of("seven")`) — and extension methods. Not interface members: a method table holds one
function per slot and finds it by name, so two of a name would need two slots and every
implementing type would owe both (`LYR-SEM0088`). Only functions share names at all — a function
beside a type of the same name is the ordinary collision (`LYR-RES0001`).

**What separates them.** The parameter list, and nothing else. Two with the same list are a
redeclaration however their results differ (`LYR-SEM0085`): a call site cannot choose by what it
gets back. The list means the TYPES — a default and a `params` tail are call-site transformations
(§7.1) and separate nothing, so `f(xs: int[])` beside `f(params xs: int[])` is that same
redeclaration. Overloading is per SCOPE — an inner declaration hides an outer one whole, as every
declaration does — and a selective import brings the whole set, because importing a name imports
what it means.

**How a call chooses.** By its arguments alone. A candidate takes part when it can accept the
argument COUNT, counting defaults and a `params` tail; it is then rejected unless every argument
either has the parameter's type exactly or is assignable to it. Among those that remain, the one
that needs least wins, in this order:

1. fewest arguments that had to convert (an exact type beats a literal that adapts);
2. fewest parameters that are TYPE PARAMETERS (a function written for this type beats one written
   for every type);
3. the one that needs no default arguments;
4. the one that is not variadic;
5. the type's own member, over an extension — the rule that predates overloading, and last, so it
   decides nothing a parameter could decide.

Nothing left is `LYR-SEM0087`; two that tie on all five are `LYR-SEM0086`. Both name every
candidate: the reader has to be able to see what the compiler saw.

**An argument that does not type at all is reported for itself**, and the call reports nothing
on top of it. Choosing means typing the arguments before a candidate is known, so a mismatch
against a candidate that loses is not reported — but a broken argument is not a mismatch, and
`LYR-SEM0087` naming `<error>` states a consequence while hiding its cause. Since 3.0.1 — the
poison rule the rest of the checker follows, arrived at the one place that had escaped it.

**Extensions of one name are one set.** Several visible extension methods offering one member of
a type are candidates together, chosen by the arguments like any others. What remains ambiguous
is two of them offering that member with the SAME parameters (`LYR-SEM0044`) — nothing at a call
site could tell those apart. *(Until 3.0.1 the shared NAME was the ambiguity, which was right
before overloading and refused an overloaded extension after it.)*

A **lambda argument takes no part** in the choice. It has no type until a parameter gives it one,
so letting it choose would be circular; the other arguments separate the candidates, or the call is
ambiguous.

**As a value.** A name that means several functions, standing where a value is wanted rather than
in callee position, is chosen by the type it is wanted AS: a parameter of type `fn(int) -> string`
picks the overload of that shape. With no such type, or none of that shape, the reference is
refused (`LYR-SEM0089`).

**In the compiled module.** Function names are unique in a `.lyrbc` — the verifier refuses
duplicates — so overloads carry their parameters in the name: `main.show(int)` beside
`main.show(string)`. A name declared once is unchanged, so a program without overloads compiles to
the bytes it always did. A host calling by name (§11) matches on the argument COUNT, since it has
values rather than declared types; two of one count are an ambiguity it settles by passing the full
name.

## 4.4 The standard library's special edges

A small set of functions is bound by the compiler without an import: `panic`, `coroutineEnded`
and — since 2.2.0, behind `co.next()` — `coroutineIsDone` from `std.core`; the
f-string/operator helpers of `std.string` (`concat` behind `+` on strings, `repeat` behind
`*`, the `fromXxx` converters behind interpolation); and the char-array native of `std.string`
behind `for (c in s)` (the private `rawToChars` since 2.0). Everything else in the standard
library is ordinary Lyric reached through ordinary imports. `std.core` imports nothing — it is
the library's root.

`coroutineIsDone` is declared per coroutine signature, so its name may stand in a module's
import table with several signatures — the entries bind independently, and every consumer of
the import table is positional. It takes the coroutine value and answers whether the body has
run to its end.

## 4.5 Capabilities

A module may be **gated**: importing it (or any submodule) records a capability bit in the
compiled module, and a runtime refuses to load the module unless the bit is granted. The bits
and their values are part of the bytecode contract and never change meaning:

| Bit | Gate | Modules |
|---|---|---|
| 0 | `fileAccess` | `std.io.file` |
| 1 | `networkAccess` | `std.io.net` |
| 2 | `osAccess` | `std.os`, `std.time`, `std.task` |
| 3 | `hostAccess` | `std.dotnet` |
| 4 | `processAccess` | `std.process` (4.0) |

Standalone execution grants everything; an embedding host decides. Console I/O and everything
computational require nothing. `std.time` and `std.task` deliberately ride `osAccess`: reading
the clock — or blocking a thread on it — is a question to the environment, and a new bit would
be a contract change for every older runtime. Child processes are a NEW power rather than a
refinement of an old one, which is why `std.process` (4.0) carries its own bit: a host that
grants the environment questions of `osAccess` has not thereby agreed to arbitrary programs
being started.

The recorded bits are a verified BOUND, not a request: a runtime refuses a module whose bits the
host does not grant, and refuses to bind a gated native inside a module whose bits do not cover
it (`LYR-CAP0001` either way; §13). A compiler records the bits its imports imply, so the second
refusal is reachable only from hand-built bytes — the case the capability model exists for.

## 4.6 Reachability *(informative)*

A program is pruned from its entry point: what `main` does not reach — directly or through
vtable rows and attribute-bearing declarations — is not in the compiled module. The canonical
`@Deprecated` attribute roots nothing.

**Since 2.0** (decided 2026-08-19): a module compiled WITHOUT an entry point — a library —
takes the `pub` functions of its compiled modules as reachability roots, so a library's
surface decides its contents. The standard library's own `pub` declarations do not root — they
are content like everything else. It waited for 2.0 because it is observable: an embedding
host calling a function the surface does not reach finds it missing.

## 4.7 Attributes

An attribute is a plain `struct` that declares one of the marker conformances of `std.core` —
`OnModule`, `OnType`, `OnFunction` — and is written `@Name { field = literal }` before the
declaration it applies to, or before the module header. Each marker permits the corresponding
placement and nothing else; the grammar additionally limits placement to a function, a struct,
a class, an enum, or the module header (`LYR-PAR0038`, `LYR-PAR0042`).

An applied attribute becomes **one metadata row** in the compiled module, and everything about
it follows from that:

- Arguments are values at compile time — a number, a string, a char or a bool; **since 2.4** a
  name bound to one: an identifier or a module-qualified path denoting a `let` (module level or
  `static`, in any module) whose initializer is itself such a value, transitively; and **since
  2.10** a unit variant of an enum (`Stage.Physics`), which is what lets a vocabulary be checked
  by the type system rather than spelled as a string. A variant WITH a payload is not one: a row
  holds one value per field, and a payload is values of its own. Nothing is COMPUTED on the way —
  `let n = 1 + 2;` is not a value, because the language folds nothing anywhere — and every field
  of the attribute struct must end with a value, written at the site or as a default of the same
  kind (`LYR-SEM0066`, `LYR-SEM0069`). **Since 3.9.1** the FIELDS themselves are held to the
  same standard, at the use: a row holds a number, a string, a char, a bool or a variant tag,
  so a field of any other type — an optional, an array, a struct — refuses the use
  (`LYR-SEM0096`). Before that rule the sema accepted `n: ?int` with `n = 3` — the literal
  adapts — and the bytecode writer, which has no encoding for it, took the compiler down.
- **Since 3.9** an attribute may take its one value POSITIONALLY: `@On(Event.Damage)`. The
  parenthesized form carries exactly one value, under the same value rules as a written field,
  and it fills the attribute's FIRST field; every other field must end with a value through its
  default, as if unwritten. The form is a conformance, not a courtesy: it is admitted only for
  an attribute struct that declares `std.core.WithArg<T>` — directly or through an interface
  parent, as any conformance may be reached (`LYR-SEM0094` otherwise) — and `T` must be exactly
  the first field's type, checked where the conformance is written, the entry that reaches it
  (`LYR-SEM0095`) — a mismatch lands with the SDK author, not at use sites. The braces form
  stays available to every attribute; one use writes one form or the other, and the grammar
  admits no mix. The row a positional use produces is indistinguishable from the row of its
  braces twin.
- **Since 3.9** several attributes may stand as one GROUP:
  `@[Component, System { order = 10 }, On(Event.Damage)]` — the same list the stacked spelling
  declares, row for row in written order and under the same rules; the one-per-attribute rule
  counts across both spellings. A group holds at least one entry, and the entries carry no `@`
  of their own.
- The same attribute may sit on a declaration once, and set each field once (`LYR-SEM0068`).
- A generic type cannot be an attribute, and an attribute cannot sit on a generic
  declaration — one row cannot stand for every instance (`LYR-SEM0065`, `LYR-SEM0067`). The
  single row-less exception is the canonical `@Deprecated`, which emits no row and only
  drives diagnostics (`LYR-SEM0076`), and may therefore sit on generics.
- **Since 2.1** the same row-less exception extends to MEMBERS: `@Deprecated` — and only it —
  may sit on a method, a field or a `static let` of a struct, class or enum, and on an extend
  method; every other attribute there is `LYR-SEM0065`, because the module format has no
  member rows. **Since 2.15 an INTERFACE member carries it too**, under the same restriction,
  and with the conformance question answered: a use that resolves to the interface's member
  warns, and an IMPLEMENTATION does not. An implementation is not a use, and a conforming type
  must implement what the interface requires — a warning there could not be acted on without
  breaking conformance. (An attribute on the interface DECLARATION itself is still
  `LYR-PAR0042`.)
- An attribute-bearing declaration is a reachability root (§4.6): the row is how an embedding
  host discovers it (§11). `@Deprecated`, having no row, roots nothing.
- **Since 2.13** `@Deprecated` carries a second field, `until`, naming the version that REMOVES
  the declaration — and the compiler enforces it: building with a toolchain that has reached that
  version is `LYR-SEM0081`, as is a version it cannot read. `until = "3.5"` fails at 3.5, not one
  release later; the named version is the one doing the removing. The check sits at the
  DECLARATION rather than at a use, so a form kept past its date is refused whether or not
  anything still calls it. An empty `until` is the ordinary policy: warn now, remove at the next
  major.

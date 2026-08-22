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
| 1 | `networkAccess` | `std.io.net` (reserved) |
| 2 | `osAccess` | `std.os`, `std.time` |
| 3 | `hostAccess` | `std.dotnet` |

Standalone execution grants everything; an embedding host decides. Console I/O and everything
computational require nothing. `std.time` deliberately rides `osAccess`: reading the clock is a
question to the environment, and a new bit would be a contract change for every older runtime.

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
  kind (`LYR-SEM0066`, `LYR-SEM0069`).
- The same attribute may sit on a declaration once, and set each field once (`LYR-SEM0068`).
- A generic type cannot be an attribute, and an attribute cannot sit on a generic
  declaration — one row cannot stand for every instance (`LYR-SEM0065`, `LYR-SEM0067`). The
  single row-less exception is the canonical `@Deprecated`, which emits no row and only
  drives diagnostics (`LYR-SEM0076`), and may therefore sit on generics.
- **Since 2.1** the same row-less exception extends to MEMBERS: `@Deprecated` — and only it —
  may sit on a method, a field or a `static let` of a struct, class or enum, and on an extend
  method; every other attribute there is `LYR-SEM0065`, because the module format has no
  member rows. Interface members carry no attributes at all (`LYR-PAR0042`): deprecating an
  abstract member would raise conformance questions nobody has answered.
- An attribute-bearing declaration is a reachability root (§4.6): the row is how an embedding
  host discovers it (§11). `@Deprecated`, having no row, roots nothing.
- **Since 2.13** `@Deprecated` carries a second field, `until`, naming the version that REMOVES
  the declaration — and the compiler enforces it: building with a toolchain that has reached that
  version is `LYR-SEM0081`, as is a version it cannot read. `until = "3.5"` fails at 3.5, not one
  release later; the named version is the one doing the removing. The check sits at the
  DECLARATION rather than at a use, so a form kept past its date is refused whether or not
  anything still calls it. An empty `until` is the ordinary policy: warn now, remove at the next
  major.

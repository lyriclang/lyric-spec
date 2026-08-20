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
module-level `let` initializers run in declaration order, first by module then by source order,
and an initializer reading a later global is an error. There is no module-level `var`.

## 4.4 The standard library's special edges

A small set of functions is bound by the compiler without an import: `panic` and
`coroutineEnded` from `std.core`; the f-string/operator helpers of `std.string` (`concat`
behind `+` on strings, `repeat` behind `*`, the `fromXxx` converters behind interpolation);
and the char-array native of `std.string` behind `for (c in s)` (the private `rawToChars`
since 2.0). Everything else in the standard library is ordinary Lyric reached through
ordinary imports. `std.core` imports nothing — it is the library's root.

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

- Arguments are literals only — a number, a string, a char or a bool; every field of the
  attribute struct must end with a value, written at the site or as a literal default
  (`LYR-SEM0066`, `LYR-SEM0069`).
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

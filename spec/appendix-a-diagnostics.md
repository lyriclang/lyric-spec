# Appendix A. The diagnostic catalogue

This is the catalogue §12.2 promises: every code the reference toolchain can emit, with its
severity and its cause, verified against the emission sites of the reference implementation.
The **code and severity are contract**; the message wording is quality of implementation
(§12.1 rule 3). A cause is written here as the *condition* that produces the code, not as the
exact message text.

Severities: **E** error (compilation or load rejected), **W** warning, **H** hint. Runtime
panics (`VM`) carry no severity — they abort the program with exit code **101**. Codes marked
**E²** are errors from 2.0 and were warnings before (the one severity change of the major;
§12.1 rule 1 note).

## A.1 LEX — lexical errors

All lexical diagnostics are errors: a token that cannot be formed poisons everything after it.

| Code | S | Cause |
|---|---|---|
| LYR-LEX0001 | E | A character that starts no token (reported as the character, or as `U+NNNN` for a control character). |
| LYR-LEX0002 | E | Unterminated block comment — block comments nest, and a nested one left open counts (§1.2). |
| LYR-LEX0003 | E | Malformed numeric literal: a digit outside the base after `0x`/`0o`/`0b`, or a malformed decimal form. |
| LYR-LEX0004 | E | Empty integer literal after a base prefix (`0x` with no digits). |
| LYR-LEX0005 | E | The separator `_` directly after a base prefix (`0x_1`). |
| LYR-LEX0006 | E | Exponent part is not a decimal number (`1e`, `1e+`). |
| LYR-LEX0007 | E | Malformed escape sequence: unknown escape, `\x` without exactly two hex digits, `\u` without braces, empty `\u{}`, unterminated `\u{`, a value beyond `0x10FFFF`, or one in the surrogate range `0xD800..0xDFFF` — the escape names a Unicode scalar (§1). |
| LYR-LEX0008 | E | A character literal holding more or fewer than one character. |
| LYR-LEX0009 | E | Unterminated string literal — strings do not span lines (§1.6). |
| LYR-LEX0010 | E | Unterminated character literal. |
| LYR-LEX0011 | E | Unterminated f-string — including one broken open by a line end inside an interpolation. |
| LYR-LEX0012 | E | `@` not followed by an identifier — `@ident` is one token (§1.1). |

## A.2 PAR — parse errors

All parse diagnostics are errors. The parser recovers and keeps reading, so one source error
may surface several codes; conformance cases pin the first.

| Code | S | Cause |
|---|---|---|
| LYR-PAR0001 | E | A complete expression, pattern or statement is followed by a token that cannot continue it. |
| LYR-PAR0002 | E | An expression was required and the current token starts none. |
| LYR-PAR0003 | E | `.` or `?.` not followed by a member name. |
| LYR-PAR0004 | E | A `]` is missing: index, array type, constraint list or interface list left open. |
| LYR-PAR0005 | E | A range operator chained (`a..b..c`) — ranges do not chain. |
| LYR-PAR0006 | E | Unknown numeric literal suffix. |
| LYR-PAR0007 | E | Numeric literal too large for every type it could name. |
| LYR-PAR0008 | E | A `(` or `)` the construct requires is missing (call, grouping, function type, parameter list). |
| LYR-PAR0009 | E | A `<` or `>` of a type-argument or type-parameter list is missing. |
| LYR-PAR0010 | E | A tuple literal or tuple type with fewer than two elements. |
| LYR-PAR0011 | E | A type was required and the current token starts none. |
| LYR-PAR0012 | E | `=>` missing in a lambda. |
| LYR-PAR0013 | E | Lambda parameter name missing. |
| LYR-PAR0014 | E | `}` missing to close an f-string interpolation. |
| LYR-PAR0015 | E | `->` missing in a function type. |
| LYR-PAR0016 | E | A function body must open with `{` or end with `;`; also a missing statement `;`. |
| LYR-PAR0017 | E | `{` missing to open a body (type, enum, interface, extend, match, block). |
| LYR-PAR0018 | E | `}` missing to close a body (type, enum, interface, extend, match, block, import list, struct initializer, attribute arguments). |
| LYR-PAR0019 | E | `(` missing after a keyword that requires one: `if`, `while`, `for`, `match`, `catch`. |
| LYR-PAR0020 | E | A malformed binding: name missing (binding, loop variable, catch binding), destructuring outside a local `let`/`var`, a destructuring binding without a tuple pattern, or one without an initializer. |
| LYR-PAR0021 | E | `in` missing in a for-loop. |
| LYR-PAR0022 | E | `while` missing after a do-block. |
| LYR-PAR0023 | E | `try` without a single `catch` clause (the syntactic form; the semantic twin is LYR-SEM0036). |
| LYR-PAR0025 | E | A declaration was required and the current token starts none. |
| LYR-PAR0026 | E | An identifier was required: function, type, field, variant, parameter, interface, alias, attribute or import name, or a module-path segment. |
| LYR-PAR0027 | E | A global binding with `var` — globals are immutable, `let` only (§4.3). |
| LYR-PAR0028 | E | `=` missing in a type alias. |
| LYR-PAR0029 | E | `,` missing between members. |
| LYR-PAR0030 | E | `[` missing after `::` — conformances and constraints stand in brackets. |
| LYR-PAR0031 | E | `:` missing after a parameter or field name. |
| LYR-PAR0032 | E | `fn` was required (member position) and is missing. |
| LYR-PAR0033 | E | A pattern was required and the current token starts none. |
| LYR-PAR0034 | E | `=>` missing in a match arm. |
| LYR-PAR0035 | E | `,` missing after a match arm. |
| LYR-PAR0036 | E | An if-expression without an `else` branch — as an expression it must produce a value on both paths. |
| LYR-PAR0037 | E | `=` missing in a struct initializer or attribute arguments (`:` is only for types). |
| LYR-PAR0038 | E | An attribute on a parameter — only a function, a struct, a class, an enum or the module header carries one. |
| LYR-PAR0040 | E | `static let` outside a struct or class body. |
| LYR-PAR0041 | E | A `static` interface member — interface members dispatch on a receiver. |
| LYR-PAR0042 | E | An attribute not followed by a declaration it may apply to, or sitting on a declaration kind that carries none (since 2.1 members carry one; interface members still do not). |
| LYR-PAR0043 | E | An array type written with a length (`int[3]`, since 3.4.1). Array types carry none; the value is built with `[x] * n`. |

## A.3 RES — module and name resolution

| Code | S | Cause |
|---|---|---|
| LYR-RES0001 | E | A name declared twice in the same scope: module, type body or extend block. Carries a note pointing at the previous declaration. |
| LYR-RES0002 | E | A type name that resolves to nothing. |
| LYR-RES0003 | E | An imported module that cannot be found. |
| LYR-RES0004 | E | An imported name the target module does not export — missing entirely, or present but not `pub`. |
| LYR-RES0005 | E | An import cycle between modules. |
| LYR-RES0006 | E | A file loaded under one module path declaring a different `module` header. |
| LYR-RES0007 | E | The same module path declared by more than one file. |

## A.4 SEM — type checking, flow analysis, warnings and hints

### Errors

| Code | S | Cause |
|---|---|---|
| LYR-SEM0001 | E | Assignability violated: a value of one type where another is required, including `return;` in a non-void function. |
| LYR-SEM0002 | E | Unknown identifier. May carry a did-you-mean note. |
| LYR-SEM0003 | E | An operator not defined for its operand type(s): missing `Ordered`/operator-interface conformance, mismatched range bounds, or a compound assignment through an operator interface on a field or element target (§6.5). |
| LYR-SEM0004 | E | A condition that is not `bool`. |
| LYR-SEM0005 | E | Force-unwrap `!` on a non-optional. |
| LYR-SEM0006 | E | No conversion path: `as` without an `Into` conformance, or an opaque type in an f-string (§3.5). |
| LYR-SEM0007 | E | Not indexable / not iterable: index not an integer, a type without `Indexable<T>`, a `for` over a type without `Iterable<T>`/`Iterator<T>`, or an index on `string` (refused by design — codepoint positions cost O(n)). |
| LYR-SEM0008 | E | `this` outside a method. |
| LYR-SEM0009 | E | Array elements that do not share one type. |
| LYR-SEM0010 | E | A binding with neither a type nor an initializer. |
| LYR-SEM0011 | E | Unknown or unusable type name: unresolved, a module used as a type, or a non-type symbol in type position. |
| LYR-SEM0012 | E | A member that does not exist on the type, static member missing, or a module member that does not exist. May carry a did-you-mean note. |
| LYR-SEM0013 | E | A call on something that is not callable. |
| LYR-SEM0014 | E | Argument count does not match the parameter list (respecting defaults and `params`). |
| LYR-SEM0015 | E | A field that does not exist on the struct, class or variant. |
| LYR-SEM0016 | E | Branches of one construct produce incompatible types (if-expression, match arms). |
| LYR-SEM0017 | E | Not all paths of a non-void function return a value. |
| LYR-SEM0018 | E | Use of a possibly unassigned variable (§7.7 definite assignment). |
| LYR-SEM0019 | E | Assignment to something that is not a mutable lvalue. |
| LYR-SEM0020 | E | A declared conformance without an implementation of one of the interface's methods. |
| LYR-SEM0021 | E | `main` with the wrong signature, or declared twice. |
| LYR-SEM0022 | E | An expression statement with no effect — only calls, assignments and `resume` stand alone. |
| LYR-SEM0023 | E | `mut` on a free function — it belongs to methods. |
| LYR-SEM0024 | E | `params` not last, or not an array type. |
| LYR-SEM0025 | E | A required parameter after a default parameter. |
| LYR-SEM0026 | E | Type-argument count does not match the declaration (function, type, enum). |
| LYR-SEM0027 | E | A member on a type parameter that no constraint provides. |
| LYR-SEM0028 | E | A type argument that does not satisfy its constraint. |
| LYR-SEM0029 | E | A pattern that cannot match the scrutinee: `null` against non-optional, literal or range of the wrong type, tuple arity mismatch, a path that is not the matched enum. |
| LYR-SEM0030 | E | Throwing, declaring or catching a type that does not implement `Throwable` (§9.1). |
| LYR-SEM0031 | E | An enum variant used against its shape: payload not destructured, wrong payload form (tuple vs struct), wrong arity, unknown variant, payload constructed wrongly. |
| LYR-SEM0032 | E | Or-pattern alternatives that bind different variables, or one variable at different types. |
| LYR-SEM0033 | E | A block arm of a match expression that can fall out — blocks have no value; every path must return or throw. |
| LYR-SEM0034 | E | A call that may throw with nothing handling it — no `throws` on the enclosing function, no try/catch around it (§9.2). |
| LYR-SEM0035 | E | A catch-all clause that is not the last catch. |
| LYR-SEM0036 | E | `try` without a `catch` — `finally` does not exist, `defer` is the mechanism. |
| LYR-SEM0037 | E | A `throws` function used as a value — function types carry no throws information (§9.2). |
| LYR-SEM0038 | E | `yield` outside a coroutine, or a bare `yield;` where the coroutine yields a value (§10). |
| LYR-SEM0039 | E | A coroutine returning a value — it ends with a bare `return;`. |
| LYR-SEM0040 | E | `resume` on something that is not a `Coroutine<T>`. |
| LYR-SEM0041 | E | Orphan extension: neither the target type nor any implemented interface is declared in this module (§5.5). |
| LYR-SEM0042 | E | An implementation whose signature does not match the interface's declaration. |
| LYR-SEM0043 | E | A default method provided by more than one conformed interface — override it explicitly. |
| LYR-SEM0044 | E | A member provided by more than one visible extension with the SAME parameters (since 3.0.1). Several of a name are an overload set since 3.0, and the call site chooses; two of one signature leave nothing to choose by. Before 3.0.1 the shared name alone was the cause. |
| LYR-SEM0045 | E | A lambda parameter without a type annotation where no context type supplies one. |
| LYR-SEM0046 | E | A non-void block lambda that can fall out without returning or throwing. |
| LYR-SEM0047 | E | An extend target that is not a plain named type (no generic, array, tuple or function targets). |
| LYR-SEM0050 | E | A non-exhaustive match. Guarded arms do not count toward exhaustiveness (§7.6). |
| LYR-SEM0051 | E | A bodyless function outside the standard library — only stdlib modules declare natives. |
| LYR-SEM0052 | E | A non-value symbol (type, module, interface) used as a value — or (since 3.6.0) a GENERIC function: fn values are monomorphic (§8.1), so an unsubstituted signature fits no function type. Callee position is not a value use. |
| LYR-SEM0053 | E | An attribute name used as an expression. |
| LYR-SEM0054 | E | `static` combined with `mut` — a static member has no receiver. |
| LYR-SEM0055 | E | Static/instance confusion: an instance method or field read from the type, or a static member called on an instance (the deliberate exception: LYR-SEM0074). |
| LYR-SEM0056 | E | A struct containing itself — infinite size; the recursive part needs a `class`. |
| LYR-SEM0057 | E | A global constant reading one that is initialized later — dependency order across modules, source order within one (§4.3). |
| LYR-SEM0058 | E | Destructuring something that is not a tuple, or with the wrong arity. |
| LYR-SEM0059 | E | `==`/`!=` not defined: an optional compared against a non-`null` value, or a type without `Equatable`. |
| LYR-SEM0060 | E | A type argument no call argument determines — write it explicitly. |
| LYR-SEM0061 | E | Constructing a host type from a script — only the host creates one (§11). |
| LYR-SEM0062 | E | `?.` calling a function-typed field — a call through `?.` works on methods; read the value first. |
| LYR-SEM0063 | E | A static member on a generic type without its type arguments written. |
| LYR-SEM0064 | E | A type alias that expands to itself. |
| LYR-SEM0065 | E | Not an attribute here: the type does not declare the marker for the target kind, is generic, is no struct at all — or sits on a MEMBER while not being `@Deprecated`, the one member attribute (§4.7). |
| LYR-SEM0066 | E | An attribute argument that is not a value at compile time — not a literal, not a unit enum variant, and not a name denoting a `let` bound to one (§4.7). |
| LYR-SEM0067 | E | An attribute on a generic declaration — one metadata row cannot stand for every instance. |
| LYR-SEM0068 | E | The same attribute twice on a declaration, or the same field set twice. |
| LYR-SEM0069 | E | An attribute leaving a field without a compile-time value. |
| LYR-SEM0070 | E | A duplicate field in a struct or variant initializer. |
| LYR-SEM0074 | E² | The instance form of a static extension. A warning through 1.x with the message announcing this change; an error from 2.0. |
| LYR-SEM0078 | E | An interface list that cannot mean what it says: an entry that is not an interface — in a parent list, or (since 2.15) in the conformance list of a type or an `extend` — a circular parent chain, or (since 3.6.0) an entry repeating an earlier entry of the same list at the same arguments (§5.1; reached twice through a chain or across declarations stays one conformance and is not refused). |
| LYR-SEM0079 | E | An inherited member name that is ambiguous: an interface redeclaring a member of an ancestor, or (since 2.16) two parents contributing one name from different declarations. A diamond is not ambiguous. |
| LYR-SEM0080 | E | `next()` on a `Coroutine<?T>` (since 2.2.0): a `null` result would mean both "yielded null" and "done" (§10). |
| LYR-SEM0081 | E | A `@Deprecated` whose `until` names a version the toolchain has reached, or one it cannot read (since 2.13.0). The promise is checked at the DECLARATION, so it fires whether or not anything uses it. |
| LYR-SEM0082 | E | A generic interface member that cannot work: one without a body, or a type overriding one (since 2.17). Such a member has no slot — it is monomorphized — so it must bring its own implementation and must be the only one. |
| LYR-SEM0083 | E | An arithmetic operator whose receiver conforms twice with the same right-hand type, disagreeing on what to call (since 3.0). Several conformances are allowed and are selected by the operand; two that take the same operand leave nothing to select by. Reported where the operator is used. |
| LYR-SEM0085 | E | Two functions of one name with the SAME parameter list (since 3.0). Overloads are told apart by what they take; a call site cannot choose by what it gets back. |
| LYR-SEM0086 | E | A call whose overloads tie on every rule of §4.3a (since 3.0). Names every candidate that tied. |
| LYR-SEM0087 | E | A call no overload of the name accepts (since 3.0). Names every candidate and what it takes. |
| LYR-SEM0088 | E | An overloaded INTERFACE member (since 3.0). A method table holds one function per slot and finds it by name. |
| LYR-SEM0089 | E | A name meaning several functions used as a VALUE, with no type to pick by or none of that shape (since 3.0). |
| LYR-SEM0084 | E | A `throws` suffix on a type that is not a coroutine (since 3.0). Every other value runs at its call, and the callee's own clause says there what it throws. |
| LYR-SEM0090 | E | A range outside a loop head (since 3.3). `a..b` is a loop head, not a value: there is no range type, so binding, storing or passing one is refused where it is written (§2, §7.2). |
| LYR-SEM0091 | E | `for-in` over an array of optionals, or over an iterator of optionals (since 3.3). `next()` answers `?T` and spends `null` on the end, so an optional element would need `??T`, and `?` does not nest (§3, §7.2). |
| LYR-SEM0092 | E | A call whose type-argument inference must bind through a conformance while the argument type conforms to that interface more than once (since 3.6.0). No conformance is chosen — the order of a `::` list must never decide a call — and writing the type argument settles it (§8.3). |

### Warnings and hints

| Code | S | Cause |
|---|---|---|
| LYR-SEM0071 | W | An unused local binding. Shorthand field-pattern bindings are exempt by design. |
| LYR-SEM0072 | W | An unused import. An import whose extensions are used counts as used (§4.2). |
| LYR-SEM0073 | W | An unreachable statement. |
| LYR-SEM0075 | H | A `var` never reassigned — `let` would do. Conservative: any by-reference touch counts as a mutation. |
| LYR-SEM0076 | W | Use of a declaration or module marked `@Deprecated`. |
| LYR-SEM0077 | W | An import shadowing a builtin type name. |

## A.5 IR — lowering limits

| Code | S | Cause |
|---|---|---|
| LYR-IR0001 | E | Valid Lyric this implementation cannot lower. Deliberately the ONE code of the area: the set of constructs behind it may shrink release by release without retiring numbers. In the reference toolchain it currently covers `&&=`/`||=` and a `catch` naming a specific interface (the documented limits of §6, §9), and it is where the refusal every implementation must make surfaces there: a monomorphization that cannot terminate, in both shapes (§8.1 polymorphic recursion written with an open instance; §5.2a a member demanding an unbounded instance chain). Two former entries left the list: generic interface defaults lower since 2.17, and a generic function used as a value is refused by the type checker (§8.1), not here. |

## A.6 CLI — driver and project handling

| Code | S | Cause |
|---|---|---|
| LYR-CLI0001 | E | A given file could not be read. |
| LYR-CLI0002 | E | A command invoked without its required argument. |
| LYR-CLI0003 | E | Unknown command or option. |
| LYR-CLI0004 | E | A file of the wrong kind for the command (`lyrvm run` on a `.lyr`). |
| LYR-CLI0005 | E | The runtime named by `--vm` or `LYRIC_VM` does not exist. |
| LYR-CLI0006 | E | The external runtime could not be started. |
| LYR-CLI0008 | E | The output file could not be written — or would not be: a pack the implementation declines to produce because the result could not start. A stub it cannot edit, or (since 3.1) a macOS program on a host that carries no signer, an unsigned Mach-O being killed at launch. |
| LYR-CLI0009 | E | A function named by `--function` is not in the module. |
| LYR-CLI0010 | E | A `lyric.json` was found and could not be understood — carrying on would compile against a module root the file was trying to change. |
| LYR-CLI0011 | E | No `build.lyr` in the directory a build was pointed at. |
| LYR-CLI0012 | E | The build script ran and did not finish its job: panicked, no `build` function, or nothing declared to compile. |
| LYR-CLI0013 | E | A pack stub started directly — the executable carries no program. |
| LYR-CLI0014 | E | A pack footer that does not hold together — a truncated download looks like this. |
| LYR-CLI0015 | E | No stub to pack into — the resolution ladder ended empty-handed. |
| LYR-CLI0016 | E | Warnings under `--deny-warnings`. The warnings keep their severity; this error carries the policy into the exit code. |
| LYR-CLI0017 | W | A tolerable but suspect `lyric.json`, such as an unknown key — tolerated so a newer file still loads, warned so a typo is not silent. |

## A.7 BC — bytecode loading

A loader refuses a damaged or foreign `.lyrbc` before anything runs; every refusal is an
error.

| Code | S | Cause |
|---|---|---|
| LYR-BC0001 | E | The file does not begin with `LYRB`. |
| LYR-BC0002 | E | Unknown major format version. |
| LYR-BC0003 | E | The file ends inside a structure, or a section length does not match its contents. |
| LYR-BC0004 | E | An index out of range: string pool, function, block or local slot. |
| LYR-BC0005 | E | Unknown opcode, type tag or section layout. |
| LYR-BC0006 | E | Stack discipline violated: underflow, depth ≠ 0 at a block boundary, or deeper than the function header announced. |

## A.8 CAP — capability policy

| Code | S | Cause |
|---|---|---|
| LYR-CAP0001 | E | The module requires a capability this host does not grant. Its own area rather than a VM error: it describes host policy, not a broken file — the same module runs elsewhere (§4.5). Also the reverse (since 3.4.1): a module binding a gated native its own bitset does not cover — reachable only from hand-built bytes, and that file IS broken. |
| LYR-CAP0002 | panic | *(since 2.4)* The execution ran out of the instruction budget the host granted it. Host policy for the same reason as `LYR-CAP0001`: the program broke no contract of its own and finishes elsewhere. A panic all the same — a stop the program could catch, or run a `defer` behind, would be one it could sit out. An implementation without the embedding API never emits it. |

## A.9 VM — runtime

`LYR-VM0001` through `LYR-VM0005` refuse a start; the rest are panics — the program aborts
with the code on stderr and exit code **101** (§9.4).

| Code | S | Cause |
|---|---|---|
| LYR-VM0001 | E | No Start section: the module is a library, not a program. |
| LYR-VM0002 | panic | Integer division or remainder by zero. Floating point follows IEEE and is not an error. |
| LYR-VM0003 | panic | An `unreachable` instruction executed — the compiler claimed this point could not be reached. |
| LYR-VM0004 | panic | Call depth exceeded; how unbounded recursion surfaces. The limit is quality of implementation (the reference allows 1024 frames); the code and the panic are the contract. |
| LYR-VM0005 | E | The module requires imports the runtime does not bind. |
| LYR-VM0006 | panic | Array index outside the bounds, or an array length the implementation cannot allocate (since 3.4.1 — it aborted the process before) — runtime values, uncheckable at load time. |
| LYR-VM0007 | panic | Force-unwrap `!` of an optional holding no value. |
| LYR-VM0008 | panic | `enumas` to a variant the value is not. The compiler proves this through `match`; the check remains because a `.lyrbc` may come from elsewhere. |
| LYR-VM0009 | panic | No vtable entry for (concrete type, interface, slot). Reachable only for a module assembled without the loader's checks. |
| LYR-VM0010 | panic | An exception left the entry point uncaught. Reachable from source until 3.0 through the coroutine gap of §10 — a pull whose origin the checker could not follow demanded no handling — and since the throwability moved into the type only for a hand-built module. |
| LYR-VM0011 | panic | `panic(msg)` from the program. Not catchable; the message is the caller's. |
| LYR-VM0012 | panic | A `char` result outside the Unicode range or in the surrogate range — checked where the value is produced. |

## A.10 EMB — the embedding boundary

Reported to the **host** as exceptions of the embedding API, not to the script; a pure
standalone implementation never emits them. For an implementation offering the embedding API
they are contract like every other family.

| Code | S | Cause |
|---|---|---|
| LYR-EMB0001 | E | A type that cannot cross the host boundary. |
| LYR-EMB0002 | E | A host asked a `void` function for a value. |
| LYR-EMB0003 | E | The value's type does not fit what the host asked for (wrong host type, or an unconvertible return). |
| LYR-EMB0004 | E | A numeric value that does not fit the target type. |
| LYR-EMB0005 | E | A host value of the wrong .NET kind for the expected Lyric type (a string where an integer was declared, `null` for a scalar). |
| LYR-EMB0006 | E | A call target that is no function: the attribute sits on a module or type, or the named function does not exist. |
| LYR-EMB0007 | E | Argument count does not match the script function. |
| LYR-EMB0008 | E | Reload of a module compiled from memory — there is no file to reload. |

## A.11 Retired and never-issued numbers

A retired number is never issued again (§12.1 rule 2).

| Number | Fate |
|---|---|
| LYR-PAR0024 | Retired. "match statements are not yet implemented" — a bootstrap placeholder, gone when match landed (pre-1.0). |
| LYR-PAR0039 | Retired. Refused interface parent lists while interfaces had none; replaced by the semantic LYR-SEM0078 when single-parent inheritance landed (1.13). |
| LYR-CLI0007 | Retired pre-1.0 (driver inventory sweep). |
| LYR-SEM0048, LYR-SEM0049 | Never issued — the numbering skipped them. Not free slots. |

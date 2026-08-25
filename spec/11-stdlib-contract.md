# 11. The standard-library contract

The standard library is written in Lyric and versioned with the toolchain; its BEHAVIOR is
specified by its own documentation and test suite (`stdlib-tests/` in the toolchain
repository), not duplicated here. What THIS document fixes is the boundary a second
implementation must honor:

1. **The compiler-bound edges** (§4.4): `std.core.panic`, `std.core.coroutineEnded`,
   `std.core.coroutineIsDone` (since 2.2.0, behind `co.next()`; bound for every coroutine
   signature it is declared with), the `std.string` helpers behind `+`, `*` and interpolation,
   and the char-array native behind `for (c in s)`. An implementation must provide these under
   these names — they are reachable from programs that import nothing.

   Interpolation makes the CONVERSION helpers observable: what `fromFloat` writes is program
   output, so its shape is fixed here rather than left to a library's habits. The result is the
   shortest decimal string that reads back as the same value — plain decimal while the value's
   decimal exponent lies in `-4 .. 16`, scientific outside it, written with a LOWERCASE marker,
   a sign and at least two exponent digits (`1e+21`, `1e-05`). `Infinity`, `-Infinity` and `NaN`
   name the non-finite values, negative zero renders `-0`, and an integral value carries no
   fractional part (`1.0` renders `1`). `fromInt` is plain decimal, `fromBool` is `true` or
   `false`, and none of them has a locale.
2. **The operator and constraint anchors of `std.core`**: `Display`, `Equatable<T>`,
   `Hashable<T>` (whose parent is `Equatable<T>` since 2.0 — a key constraint is
   `K :: [Hashable<K>]` alone), `Ordered<T>`, `Add/Sub/Mul/Div<T>`, `Into<T>`, the attribute
   markers (`OnModule`, `OnType`, `OnFunction`), the positional-argument conformance
   `WithArg<T>` (since 3.9) and `@Deprecated`. Chapter 6's operator rule and the collection
   constraints name them; without them the language loses syntax.
3. **The capability gates** (§4.5) and the native import names the bytecode of a compiled
   standard library carries: binding is symbolic by name (`std.io.file.readBytes`, …), and the
   set a runtime must implement is exactly the set the shipped `stdlib/` declares as bodiless
   functions — with ONE exception: `std.build`'s natives are bound by the build runner, its
   host, the same way an embedding host registers an SDK surface.
4. **The builtin `Throwable`** (§9.1), which is not part of the library at all.

Everything else — which methods `List` has, what `iso()` renders — is library surface: it
evolves under the toolchain's deprecation policy (warn one line, remove at the next major) and
is out of scope for language conformance.

# 11. The standard-library contract

The standard library is written in Lyric and versioned with the toolchain; its BEHAVIOR is
specified by its own documentation and test suite (`stdlib-tests/` in the toolchain
repository), not duplicated here. What THIS document fixes is the boundary a second
implementation must honor:

1. **The compiler-bound edges** (§4.4): `std.core.panic`, `std.core.coroutineEnded`, and the
   `std.string` helpers behind `+`, `*` and interpolation. An implementation must provide
   these under these names — they are reachable from programs that import nothing.
2. **The operator and constraint anchors of `std.core`**: `Display`, `Equatable<T>`,
   `Hashable<T>`, `Ordered<T>`, `Add/Sub/Mul/Div<T>`, `Into<T>`, the attribute markers
   (`OnModule`, `OnType`, `OnFunction`) and `@Deprecated`. Chapter 6's operator rule and the
   collection constraints name them; without them the language loses syntax.
3. **The capability gates** (§4.5) and the native import names the bytecode of a compiled
   standard library carries: binding is symbolic by name (`std.io.file.readBytes`, …), and the
   set a runtime must implement is exactly the set the shipped `stdlib/` declares as bodiless
   functions.
4. **The builtin `Throwable`** (§9.1), which is not part of the library at all.

Everything else — which methods `List` has, what `iso()` renders — is library surface: it
evolves under the toolchain's deprecation policy (warn one line, remove at the next major) and
is out of scope for language conformance.

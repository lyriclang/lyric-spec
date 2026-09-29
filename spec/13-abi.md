# ABI and embedding

> **Skeleton.** Written with milestone **M1/M14** of the Lyric 5 plan, spec-first: each rule lands
> here with its conformance case before or with its implementation. Source of the decisions:
> [01 Runtime](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md), [11 Tooling and interop W4/W5](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/11-werkzeuge-interop.md).

## Scope

The C ABI as the one foreign boundary: the type table, `@Layout(C)`, pointers, callbacks, exports, and the embedding API (`lyr_init`, exports as tasks, `LyrStatus`). Replaces the 4.x bytecode chapter.

# 13. Embedding

**Base.** None — this chapter replaces Lyric 5's chapter 13.

**Status.** The instance, loading and the values at the boundary written (S8a); the budget's
suspension, waiting, the host API, isolation and the C ABI come with the rest of S8 — until then
the design documents decide.

## Written (S8a, the instance)

1. **The instance** ([01 S9, S11](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md); [07 Top](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). A host loads a script into an **instance**: its
   top-level bindings, tasks and timers live from its `init` to its `close`. `init` runs the top
   level once; then `call` runs a function of the script, as the first task of that call, against
   the same bindings. A task the call leaves waiting — detached, or on a timer — stays in the
   instance and goes on in its next call. **After a panic of the script the instance takes calls
   as before**: the call's frames are gone, its bindings are as the panic left them. The budget's
   end leaves the instance suspended, and an `exit` of the script ends it: neither takes a call. A
   call before `init`, a second `init`, or a call on an instance that takes none is the host's
   mistake, not a result.
2. **Loading** ([01 S1, S10](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)). A host's VM loads a script from its **source**, under a name its
   diagnostics carry and its own imports are found by: compiled — or read from the host's cache
   directory, keyed by the source and the toolchain, a script with warnings not kept — and its
   rights checked against those the host gives, as rule 1 of chapter 17 checks them for a run. A
   source with errors, or rights not given, loads no instance; the host gets the diagnostics as
   values, each with its code, message, file, line and column, and the rights with their imports
   — nothing is printed. Bytecode the host compiled itself loads with **`loadTrusted`**: not
   compiled and not checked, its rights checked as a source's; bytecode of another format or
   toolchain does not load.
3. **Values at the boundary** ([01 S11](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md); [11 Emb](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)). A host calls the **public functions of the
   script's top level** that are not generic, by name — not a `private` or `internal` one, not a
   method, not the top level itself. What crosses is `int`, `float`, `bool`, `char`, `string` and
   lists of them, as the host's values: a copy, never a reference into the instance. A function
   whose parameter or result is of another type, an argument of another type, or another count
   of arguments, is the host's mistake. A call ends as one of: its **value**; an **error** that
   left every frame, with its type's name, message, causes and frames; a **panic**, with its
   code, message and frames; **suspended** by the budget; **aborted**; **stale**; or the script's
   **exit** with its code. Which functions a host may call, with their types, travels with the
   bytecode.

## Scope

- Replaces Lyric 5's chapter 13: the C ABI is not a language boundary of Lyric-Script. The Lyric 5 API and the C ABI of the VM, the host API as `.lyrs` declarations, native modules ([00 Z5](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/00-positionierung.md), [11 Emb, Hst](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)).

**Conformance.** `conformance/cases/13-embedding/` (`since: 1.0.0`).

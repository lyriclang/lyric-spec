# 13. Embedding

**Base.** None — this chapter replaces Lyric 5's chapter 13.

**Status.** The instance, loading and the values at the boundary written (S8a), waiting (S8d), the
host's modules (S8f2), their handles (S8f3a), structs and errors (S8f3b); callbacks, isolation and the
C ABI come with the rest of S8 — until then the design documents decide.

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
4. **Waiting** ([07 Wait, N6](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); S8d). A call waits for what its tasks wait for —
   a timer, a native's end, a channel — until it ends: the host's thread is the instance's
   meanwhile. A host that must not stall **starts** a call instead: what is ready runs, then the
   host gets the call's end or *waiting* back, and **steps** it again later, each step running what
   became ready and never waiting. An instance with a started call takes only steps and an abort.
   A started call the budget halts steps on only with a new budget, as a `resume` gives one
   ([§17 rule 2](17-host.md)).
5. **Modules of the host** ([01 S2](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md); [11 Hst](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md); S8f2). A host registers a **module of its own**
   under a name: Lyric-Script source that declares functions **without a body** — no type
   parameters, no `throws`, their parameters and result values of the boundary (rule 3) — and
   nothing else (`LYS-SEM0907`); it is checked when it is registered, its errors the host's. A
   script imports it as **`import host.<name>`**, and calls its functions as its own; a module the
   host did not register is no module (`LYS-RES0003`) — the command line registers none. A function
   asks for a **right** with `@Requires("name")` (`LYS-SEM0908` for a name that is none: lowercase
   letters, digits and `-`, a letter first); an import asks for the rights of what it names, a whole
   module's import for all of its functions', checked as rule 1 of chapter 17 checks a module of the
   standard library's — a right named as a class of it is that class. The host gives each function
   its **implementation** by name; a script that imports a module whose functions lack one does not
   load. What an implementation cannot do, or a value of another type than its function declares,
   is a panic of the script (`LYS-RT0900`); the instance takes calls after it as after any panic.
6. **Handles** (S8f3a; [11 Hst, V3](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)). A module of the host may declare a **class without
   fields**, type parameters, conformances or constants, whose methods — `static` ones too — have no
   body (`LYS-SEM0907` otherwise): a **handle**. Its value is a number the host gave, under the
   class's name; what it stands for the host holds, and the host's implementation of a method takes
   the receiver as its first argument. A handle is a value of the boundary (rule 3) in either
   direction. A script never builds one (`LYS-SEM0909`), and `==` on handles is refused as on any
   class that is neither `Identity` nor `Equatable` (`LYS-SEM0059`): what makes two the same is the
   host's to say. `@Requires` may stand on a method; an import that names the class asks for the
   rights of its methods.
7. **Structs and errors of the host** (S8f3b; [11 Hst](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)). A module of the host may declare a
   **struct** whose fields are values of the boundary, without defaults, type parameters or
   constants (`LYS-SEM0907` otherwise); a script builds and reads it as its own, and it crosses the
   boundary as a copy, its fields in the order it declares them. Its one conformance may be
   `Error`: then it is an **error of the host**, its methods — `message()` among them — the host's
   to implement like a handle's. A function of the host declares what it throws by naming such
   errors in its `throws` (`LYS-SEM0907` for any other set, the bare form among them): that set is
   all it throws. An error the host gives that its function declares is thrown in the script at the
   call, and is caught and reported as any other; one it does not declare, and any other failure,
   is a panic (`LYS-RT0900`).

## Scope

- Replaces Lyric 5's chapter 13: the C ABI is not a language boundary of Lyric-Script. The Lyric 5 API and the C ABI of the VM, the host API as `.lyrs` declarations, native modules ([00 Z5](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/00-positionierung.md), [11 Emb, Hst](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)).

**Conformance.** `conformance/cases/13-embedding/` (`since: 1.0.0`).

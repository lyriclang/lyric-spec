# 4. Modules

**Base.** Lyric 5.0 [§4](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/04-modules.md) applies, with the deviations below.

**Status.** The modules of one root written (S5a): a program of files below the entry's folder,
the three forms of import and `pub import`, `private` on a function, the bindings of an imported
module and the names a module sees. A type named through its module in an initializer, a generic
type through its module, `private` on a type and on a member, the names of `LYS-RES0011`,
`LYS-RES0012` and `LYS-SEM0153` and the trace form with the file come with S5a2; the manifest,
its dependencies and the rights from imports with S5b–S5e — until then the design documents
decide.

## Written (S5a, the modules of one root)

1. **The root** ([07 Path](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); Lyric 5 §2 rule 1). A program is
   its entry script and the modules its imports reach. Without a manifest the entry's folder is
   the root, without a prefix: `import a.b` names the file `a/b.lyrs` below it, and that module's
   path is `a.b`. An import of a module no such file provides is refused (`LYS-RES0003`). A
   folder is a namespace and no module; `a.lyrs` beside `a/` is a module of its own.
2. **A file is one module** (Lyric 5 §2 rule 5). A module several others import is read once,
   and its bindings exist once. Imports form no cycle: one that does is refused, and the error
   names the modules on it (`LYS-RES0005`).
3. **Only the entry runs its statements** ([07 Top](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md); Lyric 5 §1 rules 1–2).
   An imported module's `let`s and `var`s are its **bindings**: they are filled before the
   entry's code runs, a module's before those of every module that imports it, in the order
   they stand within it. Its other statements do not run, and each is warned
   (`LYS-SEM0905`, Script's own: a Lyric 5 module holds no statement).
4. **A declaration is its module's** (Lyric 5 §2 rule 9): two modules may declare one name, and
   the two are two declarations; two types of one name stay two types — a value of one is no
   value of the other, `is` included.
5. **Visibility** ([02 V](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md); Lyric 5 §3 rules 1–3). A declaration
   without a word is seen beyond its file — Script's default; Lyric 5's is `internal` —, as one
   with `pub` or `internal` is; `private` keeps it to its file. A `private` function is named by
   its own module alone: an import of it and a call through its module are refused
   (`LYS-RES0009`).
6. **Imports** (Lyric 5 §4 rules 1–2). An import takes one of three forms: **selective**,
   `import a.b { f, T }`, binds the names it lists, an item **renamed** with `as` under its new
   name alone; **qualified**, `import a.b`, binds the module under its last segment, `b.f()`;
   **aliased**, `import a.b as m`, under another name. There is no import of everything. A name
   the module neither declares nor passes on is refused (`LYS-RES0004`). **`pub import`**
   passes on what it binds: imported from the module that passes it on, or named through it. A
   module sees what it declares, what it imports and the prelude — the entry's names no more
   than another module's (`LYS-SEM0002`).
7. **A name is bound once in a module** (Lyric 5 `LYR-RES0001`). An import of a name the module
   declares itself, or a second import of one name, is refused (`LYS-RES0001`); the
   declaration keeps its name.
8. **An unused import** (Lyric 5 §4 rule 3) is warned, in every form (`LYS-SEM0072`), in the
   order the imports stand; a `pub import` is used by passing its names on. An import refused
   already (rules 5–7) is not also warned.
9. **A diagnostic names its file**: what is wrong in an imported module is reported at that
   module's file, line and column.

## Deviations

- A module's statements are its `main`; only the entry module runs them ([07 Top](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).
- Without a manifest the entry script's folder is the root, without prefix ([07 Path](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).
- Public by default, `private` per file; `pub` and `internal` accepted; the prelude adds `print`, `println`, `eprintln`, `readLine`, `args`, `exit`; global initializers may throw ([02 V](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/02-leitbild.md), [07](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)).

**Conformance.** `conformance/cases/04-modules/` (`since: 1.0.0`), each case a program: a folder
with its entry, `main.lyrs` ([the format](../conformance/README.md)); the forms one by one in the
toolchain's own tests (`tests/modules.lyr`).

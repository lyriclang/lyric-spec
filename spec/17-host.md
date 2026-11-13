# 17. Host, sandbox and reload

**Base.** None — this chapter is Lyric-Script's own.

**Status.** Rights from imports written (S5e); fuel and deadline, suspension and abort written
(S8b); scopes, the allocation budget and ownership come with the rest of S8, reload with S9 —
until then the design documents decide.

## Written (S5e, rights from imports)

1. **Rights** ([01 S1, S4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md); [12 Rechte](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)). A module of the standard
   library that reaches outside the script belongs to a **class of rights** — `file`, `net`,
   `process`, `os` (the environment, signals, the clock, unseeded randomness), `native`; a
   program asks for the classes its imports reach, each with its import, and the module's
   bytecode carries them, so a cached module asks as the compiled one does. They are checked
   when the module is loaded, before anything runs: nothing is given unless the run gives it —
   `--allow file,net` names classes, `-A` gives every one (`LYS-CLI0007` for a word that is no
   class). Where stdin and stderr are a terminal, the run lists what it was not given, each with
   its import, and asks once; else every missing right is reported at once, with its import
   (`LYS-CAP0001`), exit 2. `check` asks for none. A script holds no rights of its own: not in
   its frontmatter, not in a manifest. The standard library's table: `std.fs` asks for `file`;
   `std.net` and `std.http` for `net`; `std.process` for `process`; `std.os`, `std.time` and
   `std.random.system` for `os`; every other module of it for none, `std.random` among them; a module of it
   that imports another asks for nothing by that import (S7h3: `std.process` imports `std.os`)
   ([§12 rule 18](12-stdlib.md)) — a module below a row counts as the row (`std.fs.glob` asks for
   `file`).

## Written (S8b, the budget)

2. **Fuel and deadline** ([01 S5a, S5b](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md); [07 N8](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md)). A host gives each call of an
   instance ([§13 rule 1](13-embedding.md)) a budget: **fuel**, units a backward jump or a call
   spends one of and a heavy native its work ([§12 rules 17, 37](12-stdlib.md)), the same every
   time; a **deadline**, how long the call may take, which is not; either, both, or neither. The
   first to end halts the whole instance — every task of it, wherever it stands: at a backward jump,
   at a call, before a native, or in a wait, which does not outlast the deadline. A halted instance
   takes only a `resume` with a new budget, which goes on where it halted, as if it had not — the
   instruction it stood at runs then —, or an abort. What the fuel had left when it halted comes to
   what the `resume` gives: a native dearer than one grant gets through after some. A deadline does
   not change where the fuel halts.
3. **Abort** ([01 S5b](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)). An abort ends an instance at once, halted or not: its tasks go,
   parked ones too, and no `defer` runs; the files and directories its script left open are closed,
   the child processes it started are killed, its subscriptions to signals end. The instance takes
   nothing after it.

## Scope

- Rights and scopes, the prompt, fuel and deadline, suspension and abort, the allocation budget, determinism from the rights, ownership per instance, hot reload by name and type, the outcomes of a host call ([01](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md), [07 Wait](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md), [11](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)).

**Conformance.** `conformance/cases/17-host/` (`since: 1.0.0`).

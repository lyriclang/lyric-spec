# 17. Host, sandbox and reload

**Base.** None — this chapter is Lyric-Script's own.

**Status.** Rights from imports written (S5e); scopes, fuel and deadline, suspension, the
allocation budget, ownership and reload come with S8 — until then the design documents decide.

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
   `std.random` for `os`; every other module of it for none — a module below a row counts as
   the row (`std.fs.glob` asks for `file`).

## Scope

- Rights and scopes, the prompt, fuel and deadline, suspension and abort, the allocation budget, determinism from the rights, ownership per instance, hot reload by name and type, the outcomes of a host call ([01](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md), [07 Wait](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/07-nebenlaeufigkeit-und-programmstruktur.md), [11](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md)).

**Conformance.** `conformance/cases/17-host/` (`since: 1.0.0`).

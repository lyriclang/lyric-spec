# 14. Command line

**Base.** Lyric 5.0 [§14](https://github.com/lyriclang/lyric-spec/blob/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e/spec/14-cli.md) applies, with the deviations below.

**Status.** `run`, `check`, `clean` written (S2); the rest a skeleton, written with the milestone that builds it — until then the design documents decide.

## Written (S2)

1. **`lyric-script run FILE`** compiles and runs a script; `lyric-script FILE.lyrs` is the same
   ([12 CLI](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)). **`lyric-script check FILE`** compiles it and runs nothing. Both take
   `--json` ([§16](16-diagnostics.md) rule 3); an option a command does not know is refused
   (`LYS-CLI0004`), and so is a second file (`LYS-CLI0002`).
2. **Exit codes**: 0 when the script ran to its end or checked cleanly; 1 when it does not
   compile; 2 for a fault of the command line — an unknown command, option or file; 101 when
   the script panicked, its panic reported with the script's frames.
3. **The bytecode cache** ([11 Fmt](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/11-laufzeit-und-vm.md), [12 Cache](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md)): `run` keeps a
   script's bytecode under the key `sha256(source, toolchain version, bytecode format)` and runs
   a later run of the same source from it; a program of modules is keyed by every file it reads,
   each module's path and text ([04](04-modules.md) rule 1), so a changed module is compiled anew. It lies in the user's cache directory —
   `LYRIC_SCRIPT_CACHE` where it is set, else `$XDG_CACHE_HOME/lyric-script` or
   `~/.cache/lyric-script`, on Windows `%LOCALAPPDATA%\lyric-script\cache` —, under `bytecode/`.
   A file of another toolchain, another source, or one that does not read back is no cache, and
   the script is compiled anew; a script whose compilation warns is not kept, so its warnings
   are said at every run. **`lyric-script clean`** empties it.

## Deviations (skeleton, written with later milestones)

- One binary `lyric-script` with its verbs; the rights prompt, `--allow`, `-A`; `run --watch` ([12](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/12-stdlib-und-werkzeuge.md), [01 S4](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/01-host-sicherheit.md)).

**Conformance.** `conformance/cases/14-cli/` (`since: 1.0.0`).

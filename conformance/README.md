# The conformance suite

Every case is ONE `.lyr` file whose expectations stand in a `//!` header at the top — or, where
a rule is about packages ([04 §2](../spec/04-modules.md), [15](../spec/15-project.md)), ONE
directory holding a package: its `lyric.toml`, its `src/`, and the header at the top of
`src/main.lyr`. A single-file case needs no manifest beside it, and any implementation can build
a runner in an afternoon — the reference runner in `tools/run_conformance.py` is some 200 lines.

## Case format

The header is the leading block of lines starting `//!`. Directives:

```
//! run                      compile and execute; expect exit 0 unless stated
//! exit: 7                  expected process exit code (main's return value)
//! panic: LYR-RT0001        expect a panic carrying this code; exit code is 101
//! stdout:                  expected standard output, byte-exact, LF line ends:
//! | first line
//! | second line
//! stderr:                  the error stream begins with these lines (a debug trace may follow):
//! | error: first
//! |   suppressed: second
//! check                    compile only; expect acceptance in silence
//! error: LYR-SEM0001       compile only; expect rejection with exactly these codes (repeatable)
//! warning: LYR-SEM0076     compilation succeeds and reports this code (repeatable)
//! since: 5.0.0             the case pins behavior of this language version and later; a
//!                          runner given an older --toolchain-version skips it
```

Exactly one of `run` / `check` leads the header. `error:` implies rejection (compile exit 1)
with exactly the listed error codes — every one reported, none besides them, so a cascade behind
the one mistake fails the case; warnings are not compared in a rejected case. `check` without
`error:` expects silence — no diagnostics at all. A `|` line is the text after the bar less one
space, so `|   suppressed: second` keeps the report's two.

## What a case may use

Cases test the LANGUAGE. They may rely on two library edges and the §11 anchors, nothing else
of the standard library:

- `import std.io { println };` — the suite's one output channel;
- in a package case, the package's own modules;
- f-strings and the operators, whose helpers the compiler binds itself;
- the `std.core` names the stdlib contract fixes (§11): `Exception`, the operator and
  constraint interfaces, `@Deprecated` and the attribute markers — including pinning the
  ABSENCE of surface the contract removed. The prelude's names need no import (04 §4); the
  others a case imports from `std.core`;
- the names a language rule itself stands on: `std.task`'s `Cancelled`, which a coroutine's
  yield throws at `close()` (10 §1.9), and `std.core`'s `sequence` (10 §1.12); the tasks and
  waits of 10 §2–§5 — `std.task`'s `spawn`, `Task` with `await`, `isDone`, `status` and
  `cancel`, `TaskStatus`, `PanicInfo`, `TaskScope`, `withTimeout` and `TimedOut`,
  `spawnDetached`, `yieldNow`, `sleep`, `Channel` and `ChannelClosed` (10 §6), `Select` and
  `Timer` (10 §7), `std.sync`'s `Atomic` and `AtomicValue` (10 §8), `Thread` (10 §9), `Mutex`,
  `RwLock`, `LockGuard` and `Once` (10 §10), `Pool` (10 §11), `Signal` and `signals` (10 §12) —
  and the
  `std.time.Duration` a sleep takes, made by its `of…` constructors.

A case that needs more library than that — container behavior, string methods — belongs to
the library's own tests, not here.

## Running

```
python tools/run_conformance.py --lyric5 <compiler executable> [--profile debug|release] [--toolchain-version 5.0.0]
```

The runner builds with `lyric5 build` — a `check` case through the front end only
(`--emit ir`), a `run` case to a native binary in the profile asked for — runs the binary, and
compares. A package case is copied into a directory of its own and built from there without
naming a file, as a user builds a package; its binary is the one named after the package.

A package case holds its dependencies itself:

- a package read from a directory in one of its own — `deps/geo`, named by a relative path. A
  package nested in a case is no case of its own;
- a package read from git as `repos/<name>/<version>/`, a directory per version. The runner makes
  each `repos/<name>` a git repository beside the case's copy: one commit per version, oldest
  first, each tagged `v<version>`, all on the branch `main`. Where a manifest — the case's or a
  version's — says `{repos}`, the runner writes the repositories' place as a `file://` URL:
  `geo = { git = "{repos}/geo", tag = "v1.0.0" }`. Such a case is built with a cache of the
  run's own (`LYRIC_CACHE`, the reference toolchain's), so what it fetches stays out of the
  user's.

Exit codes it relies on (spec-fixed, 14 §1 and 13 §1.4): 0 success, 1 rejected compilation, 101
panic. `--parse-only` reads every header and runs nothing: the suite's own
format check, which is what this repository's CI runs, since no 5.0 toolchain is released yet
— the suite is run against the compiler's working tree by the compiler's own CI
(lyriclang/lyric, job *Conformance gate*), in both profiles.

Cases live under `conformance/cases/<chapter>/`, named after the sentence they pin — a file, or
a package's directory.

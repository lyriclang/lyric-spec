# Conformance suite

Every case is ONE `.lyrs` script under `cases/<chapter>/`, named after the sentence it pins, with
its expectations in a `//!` header — or ONE program of modules, a folder so named that holds the
entry, `main.lyrs`, with the header, and the modules it imports below it
([04](../spec/04-modules.md) rule 1). The format is Lyric 5's (`main`, `conformance/README.md`)
with the differences below; the reference runner is `tools/run_conformance.py`. Every deviation
from Lyric 5 gets a failing and a passing case.

## Case format

```
//! run                      check, then run; expect exit 0 unless stated
//! exit: 7                  expected exit code (exit(n), or main's result)
//! panic: LYS-RT0001        expect a panic carrying this code; exit code is 101
//! stdout:                  expected standard output, byte-exact, LF line ends:
//! | first line
//! | second line
//! stderr:                  the error stream begins with these lines (the frames may follow):
//! | error: first
//! |   caused by: second
//! check                    check only; expect acceptance in silence
//! error: LYS-SEM0001       check only; expect rejection with this code (repeatable)
//! warning: LYS-LEX0901     the check succeeds and reports this code (repeatable)
//! since: 1.0.0             the Lyric-Script version the case pins; required
//! until: 1.2.0             the version from which the case no longer holds
```

One space after a `|` belongs to the format; more are the line's own, so `|   caused by: x`
expects `  caused by: x`.

Exactly one of `run` / `check` leads the header. `error:` implies rejection (exit 1), and a
case's `warning:` lines are then expected beside its errors; `check` without `error:` or
`warning:` expects silence.

The differences from Lyric 5's format:

- A case is a script: its top-level statements run, `main` is not needed, and the prelude's
  `print` and `println` are the output channel — no import.
- Every case carries `since:`, at least `1.0.0`; a case without it is a fault of the suite.
- The header is the leading block of `//!` lines. A case whose first lines are its point — a `#!`
  line, a frontmatter — carries the header as the **trailing** block instead.
- A program of modules is a folder with a `main.lyrs`: the runner checks and runs that file, and
  the folder's other `.lyrs` files, at any depth, are its modules, not cases; they carry no
  header.
- A **package case** is a folder with a `lyric-script.toml`: its header stands in its
  `src/main.lyrs`, and the runner checks and runs it from the folder without naming a file, as a
  user does ([15](../spec/15-project.md) rule 2). It holds its dependencies itself, each in a
  folder of its own below `deps/`, named by a relative path; a package nested in a case is no
  case of its own.
- `exit:` beside `error:` is the exit code of a rejection that is a fault of the environment,
  2 (`LYS-PKG0007`, `LYS-PKG0009`); without it a rejection exits 1.
- A package case's dependency read from git stands as `repos/<name>/<version>/`, a folder per
  version. The runner builds the case from a copy, makes each `repos/<name>` a git repository
  beside it — one commit per version, oldest first, each tagged `v<version>`, on the branch
  `main`, by a fixed author at fixed times — and writes the repositories' place as a `file://`
  URL where a manifest or a lock says `{repos}`: `geo = { git = "{repos}/geo", tag = "v1.0.0" }`.
  Each such case runs with a cache of its own (`LYRIC_SCRIPT_CACHE`). A program case — a folder
  with a `main.lyrs` — that holds `repos/` is built the same way, `{repos}` written in its
  scripts' frontmatter too.
- `env: NAME=value` adds to the environment the case runs in (repeatable); `stderr-has:` a text
  the error stream holds somewhere (repeatable), where the report names paths of the run.
- `option: --offline` passes an option to `check` and `run` (repeatable); `update` runs
  `lyric-script update` in a package case before it is checked. A case's `lyric-script.lock` may
  name the repositories' commits: they are fixed by the fixed author and times.

## What a case may use

The language, `print`/`println`, and what a chapter of the delta names. A case that needs more
of the standard library belongs to the library's own tests.

## Running

```
python3 tools/run_conformance.py --lyric-script <path to lyric-script> [--toolchain-version 1.0.0]
```

The runner checks every case with `lyric-script check` and runs the `run` cases with
`lyric-script run`. The exit codes it relies on: 0 success, 1 rejected or failed, 101 panic.

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

## What a case may use

The language, `print`/`println`, and what a chapter of the delta names. A case that needs more
of the standard library belongs to the library's own tests.

## Running

```
python3 tools/run_conformance.py --lyric-script <path to lyric-script> [--toolchain-version 1.0.0]
```

The runner checks every case with `lyric-script check` and runs the `run` cases with
`lyric-script run`. The exit codes it relies on: 0 success, 1 rejected or failed, 101 panic.

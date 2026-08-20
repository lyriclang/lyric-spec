# The conformance suite

Every case is ONE `.lyr` file whose expectations stand in a `//!` header at the top. A runner
needs no manifest beside the file, and any implementation can build one in an afternoon — the
reference runner in `tools/run_conformance.py` is under 150 lines.

## Case format

The header is the leading block of lines starting `//!`. Directives:

```
//! run                      compile and execute; expect exit 0 unless stated
//! exit: 7                  expected process exit code (main's return value)
//! panic: LYR-VM0002        expect a panic carrying this code; exit code is 101
//! stdout:                  expected standard output, byte-exact, LF line ends:
//! | first line
//! | second line
//! check                    compile only; expect acceptance in silence
//! error: LYR-SEM0001       compile only; expect rejection with this code (repeatable)
//! warning: LYR-SEM0076     compilation succeeds and reports this code (repeatable)
//! since: 2.0.0             the case pins behavior of this language version and later; a
//!                          runner given an older --toolchain-version skips it
```

Exactly one of `run` / `check` leads the header. `error:` implies rejection (compile exit 1);
`check` without `error:` expects silence — no diagnostics at all.

## What a case may use

Cases test the LANGUAGE. They may rely on two library edges and the §11 anchors, nothing else
of the standard library:

- `import std.io.console { println };` — the suite's one output channel;
- f-strings and the operators, whose helpers the compiler binds itself;
- the `std.core` names the stdlib contract fixes (§11): `Exception`, the operator and
  constraint interfaces, `@Deprecated` and the attribute markers — including pinning the
  ABSENCE of surface the contract removed.

A case that needs more library than that — container behavior, string methods — belongs to
the library's own tests, not here.

## Running

```
python tools/run_conformance.py --toolchain <dir with lyrc and lyrvm> [--stdlib <dir>]
```

The runner compiles with `lyrc build`, executes with `lyrvm run`, and compares. Exit codes it
relies on (spec-fixed): 0 success, 1 rejected compilation, 101 panic.

Case files live under `conformance/cases/<chapter>/`, named after the sentence they pin.

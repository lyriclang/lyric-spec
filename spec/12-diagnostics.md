# 12. The diagnostic catalogue

Diagnostic codes are **contract**, not decoration: a conformance case may pin one, tooling
matches on them, and a second implementation must report the same code for the same construct.

## 12.1 The code model

A code is `LYR-<AREA><NNNN>`; the areas partition the pipeline:

| Area | Reports |
|---|---|
| `LEX` | lexical errors |
| `PAR` | parse errors |
| `RES` | module and name resolution |
| `SEM` | type checking, flow, warnings and hints |
| `IR` | valid Lyric this implementation cannot lower — `LYR-IR0001` is deliberately the ONE code of the area |
| `CLI` | driver and project-file handling |
| `VM` | load-time validation and runtime panics |

Three rules make the codes a contract:

1. **Severity belongs to the code.** `LYR-SEM0076` is a warning in every conforming
   implementation; a strict mode changes exit-code policy (the toolchain's `--deny-warnings`
   reports a closing error), never a code's severity.
2. **A retired number is never issued again.** `LYR-PAR0039` (interface parent lists, an error
   until 1.13) and `LYR-CLI0007` stay retired; gaps in the numbering are history, not free
   slots.
3. **The code names the cause, the message may improve.** Conformance pins codes; message
   wording is quality of implementation.

## 12.2 The catalogue

The full machine-readable catalogue — every code with its severity and a one-line cause — is a
2.0 artifact generated from the reference implementation, and will live in this repository
beside the suite. Until then the codes this specification references in chapters 1–10 are the
seed, and every one of them is exercised by at least one conformance case or spec sentence.

## 12.3 Runtime panics

Panics carry codes too (`LYR-VM0002` division by zero, `LYR-VM0007` `!` on empty,
`LYR-VM0010` uncaught exception, …); a conforming runtime reports the code and exits with
**101**. Compilation rejection exits with **1**, success with the program's `main` return
value.

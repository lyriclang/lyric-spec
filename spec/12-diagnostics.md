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
| `BC` | bytecode loading — a damaged or foreign `.lyrbc` refused before anything runs |
| `CAP` | capability policy — the host does not grant what the module requires (§4.5) |
| `VM` | start refusals and runtime panics |
| `EMB` | the embedding boundary, reported to the host (§11); absent from a pure standalone implementation |

Three rules make the codes a contract:

1. **Severity belongs to the code.** `LYR-SEM0076` is a warning in every conforming
   implementation; a strict mode changes exit-code policy (the toolchain's `--deny-warnings`
   reports a closing error), never a code's severity. A severity may change only at a major
   version, as spec change: the single 1.x→2.0 change is `LYR-SEM0074`, warning to error —
   the deprecation clock its message announced.
2. **A retired number is never issued again.** `LYR-PAR0039` (interface parent lists, an error
   until 1.13) and `LYR-CLI0007` stay retired; gaps in the numbering are history, not free
   slots.
3. **The code names the cause, the message may improve.** Conformance pins codes; message
   wording is quality of implementation.

## 12.2 The catalogue

The full catalogue — every code with its severity and a one-line cause, plus the retired
numbers — is **[Appendix A](appendix-a-diagnostics.md)**, curated against the emission sites
of the reference implementation. A code that appears in neither the appendix nor a retirement
row does not exist; adding one is a specification change.

## 12.3 Runtime panics

Panics carry codes too (`LYR-VM0002` division by zero, `LYR-VM0007` `!` on empty,
`LYR-VM0010` uncaught exception, …); a conforming runtime reports the code and exits with
**101**. Compilation rejection exits with **1**, success with the program's `main` return
value.

## 12.4 Implementation limits, and the implementation's own failures

Two things can stop a compile that are not the program's fault, and both owe a diagnostic rather
than a dead process.

**Nesting has a limit, and reaching it is a diagnostic.** A conforming implementation may bound how
deeply expressions and types nest — a recursive descent over an unbounded nesting exhausts a real
stack, whatever the language says — and reports reaching it as `LYR-PAR0045` at the parse and
`LYR-SEM0105` at the check, with the position of the construct that went too deep. **The depth is
not specified and is not part of the contract**: it belongs to a thread's stack, not to Lyric, and
a number here would make a conformance case pass or fail by platform. What IS required is that the
limit be reported and not crashed into. A conforming implementation accepts nesting of at least
**128**, which is far past what a person writes and far below what any stack refuses.

**An implementation that fails internally says so with a code.** `LYR-CLI0020` reports that the
compiler itself is at fault: a state it believes impossible, not a program it cannot accept. It
carries whatever position it has, it asks for a report rather than an edit, and under a
machine-readable output mode it is a diagnostic like any other — an implementation that lets an
internal failure escape as a stack trace destroys that output for the tool reading it.

The distinction from `LYR-IR0001` is the whole point and runs the other way: `IR0001` is valid
Lyric this implementation cannot lower — the program is right and the compiler is limited.
`CLI0020` is the compiler being wrong. Neither may wear the other's code.

## 12.5 Migration warnings

A **migration warning** reports a program that compiles today and will mean something else, or
stop compiling, in a named later version. It is a warning and not an error by decision: the
program is legal under the rules in force, and refusing it would make this document describe a
language nobody has released.

Four questions about the language are open rather than settled, and all four are settled together
with **5.0** rather than one release at a time (maintainer, 2026-09-24). Until then each carries a
warning and NOTHING ELSE CHANGES — the behaviour a program has today is the behaviour it keeps
until the major:

| Code | What it marks | Where |
|---|---|---|
| `LYR-SEM0107` | a second binding of one name in one scope | §7.1 |
| `LYR-SEM0108` | a non-`mut` method writing `this` on a class | §3.4a |
| `LYR-SEM0109` | a field written through an immutable struct binding | §3.4a |
| `LYR-SEM0110` | a `defer` body that can throw | §7.5 |

Three properties distinguish a migration warning from an ordinary one:

- **It does not presume the answer.** Each of the four reports a program whose meaning changes
  WHICHEVER way its question is settled. A warning that fired only under one candidate answer
  would be that answer, taken quietly.
- **It names the version.** "This changes in 5.0" is the content. A warning that merely says
  something is unusual belongs to the ordinary catalogue.
- **It retires WITH its rule.** When 5.0 settles a question, its code is retired (§12.1 rule 2)
  rather than repurposed as the error the new rule reports — the old code meant "this will
  change", and that sentence stops being true.

The four questions are stated where they belong, not here, and each says what is unspecified
rather than describing what one implementation happens to do. A conformance case for a migration
warning pins the WARNING; it cannot pin the outcome, because there is none to pin.

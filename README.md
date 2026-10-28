# The Lyric-Script Specification

**Status: skeleton (S0 of the plan to `lyric-script 1.0.0`).** This branch (`script`) specifies
Lyric-Script as a **delta to Lyric 5.0**: each chapter says which chapter of the Lyric 5
specification applies and lists the deviations, each with its reason in the design
([lyriclang/lyric-script `design/v1/spec/`](https://github.com/lyriclang/lyric-script/blob/main/design/v1/spec/)). Chapter 13 replaces Lyric 5's ABI chapter;
chapter 17 has no Lyric 5 counterpart.

The specification defines the language and the toolchain implements it; a divergence is a
toolchain bug. A rule is written here first — the chapter sentence and its conformance case — and
the toolchain follows (its `spec.pin` names the commit here).

## Base

The Lyric 5 specification at `lyric-spec` `main`
[`38ea610e`](https://github.com/lyriclang/lyric-spec/tree/38ea610e6fcfa76dc7222b442a30c3e44eb4a00e). The base moves to the Lyric 5.0 tag when
it exists (S15 of the plan); a later Lyric 5 edition reaches Lyric-Script only by a decision
written in the design.

## Layout

| Path | Content |
|---|---|
| `spec/01-lexical.md` … `spec/16-diagnostics.md` | the deltas, chapter by chapter after Lyric 5 |
| `spec/13-embedding.md` | replaces Lyric 5's ABI chapter |
| `spec/17-host.md` | rights, budget, reload, determinism, instances — Lyric-Script's own |
| `conformance/` | the conformance suite (`since: 1.0.0`) |

## History

The Lyric 4.x specification that stood on this branch is the tag `script-4.x-final`; the 4.6
toolchain at lyric-script `v4.6-final` checks against it.

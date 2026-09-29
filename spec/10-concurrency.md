# Concurrency

> **Skeleton.** Written with milestone **M6** of the Lyric 5 plan, spec-first: each rule lands
> here with its conformance case before or with its implementation. Source of the decisions:
> [06 Concurrency](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/06-nebenlaeufigkeit.md), [01 Runtime L4/L6](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/01-laufzeit.md).

## Scope

Coroutines and generators, tasks and `TaskScope`, parking, threads with one scheduler each, channels and synchronization, the memory model.

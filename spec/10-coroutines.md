# 10. Coroutines

A function whose return type is `Coroutine<T>` is a coroutine: calling it runs NOTHING and
yields a suspended computation; `resume co` runs the body to its next `yield` and produces that
value, of type `T`. State between two yields — locals, loop positions — survives. There is no
other concurrency in the language: a coroutine is a value you drive, not a thread.

**Since 4.0 a coroutine is STACKFUL**: its frames live on a chain of their own, apart from the
stack of whoever pulls, and a `yield` executed at ANY call depth beneath a running `resume`
suspends the whole chain — `readLine` may wait inside a helper inside a loop, and the pull
sees the value. Which coroutine a `yield` suspends is a runtime fact: the nearest enclosing
running resume of the current chain. §10a states the rules that follow from that.

Rules:

- **through 3.x**: `yield e;` is only legal in a coroutine body (`LYR-SEM0038`). **Since
  4.0** it is legal in every function — see §10a; inside a coroutine BODY the value still
  checks against `T` at compile time (the better error, kept), a bare `yield;` where the
  coroutine yields a value stays `LYR-SEM0038`, and `Coroutine<void>` yields bare;
- a coroutine ends with a bare `return;` — it cannot return a value (`LYR-SEM0039`). Ending
  early this way is exactly the run-through exit: the next pull sees an exhausted coroutine;
- **`resume` on an exhausted coroutine is a panic**, arriving through
  `std.core.coroutineEnded`. `resume` itself has no `null` protocol: a caller either knows how
  many values exist, drives an infinite coroutine and stops itself, or pulls with `next()`;
- **`co.next()` is the safe form of the same pull** (since 2.2.0): it advances the coroutine
  exactly like `resume` and answers `?T` — the value, or `null` once the body has run to its
  end, and `null` on every call after that. Leniency belongs to the call, not the state:
  `resume` on the same exhausted coroutine still panics. Two yield types change the answer's
  form: a `Coroutine<void>` has no value to wrap, so its `next()` answers `bool` — did it
  advance? — and a `Coroutine<?T>` refuses the form (`LYR-SEM0080`), because `null` would mean
  both "yielded null" and "done". `next` is a built-in member, not a method a type declares —
  the same standing as `length` on an array — and it exists only as a call;
- there is deliberately NO query that answers "done" without pulling: whether another value
  comes is decided by the body running, so such a query cannot be answered without advancing —
  the reason no generator API (Python, JavaScript, C#) has one;
- **a coroutine body may `throw`**, and the exception leaves the `resume` or `next()` that was
  running it, in the frame that drove the pull — an enclosing `try` there catches it like any
  other. `next()` is lenient about EXHAUSTION, not about throwing;
- send values (`resume co, v`) do not exist;
- a lambda is never a coroutine — its type is a function type, and calling it runs it. (Since
  4.0 its body may still `yield` while a resume runs, like any function's: §10a);
- at runtime a `Coroutine<T>` IS a function value that remembers where it left off — which is
  why `resume` behaves as a call. Since 2.2.0 it carries one parameter, the lenient flag
  distinguishing the two pull forms; exhaustion is read back through the compiler-bound
  `std.core.coroutineIsDone` (§4.4, §11).

## 10a. The dynamic yield (since 4.0)

`yield` is legal in EVERY function — an ordinary function, an extend method, a lambda. What it
does is decided when it runs, not where it stands, and every failure of that decision is a
PANIC, not a diagnostic — the dynamic half of the rule, and the sentence that makes 4.0 a
language major (`LYR-SEM0038` refused the form statically through 3.x; no program that
compiled before changes meaning):

1. **A yield needs a running resume.** Executed while no resume of the current chain is
   running — in `main`, in a function a host called directly, at a global initializer — it
   panics: a value was produced and nobody is suspended waiting for one.
2. **A yield suspends the NEAREST running resume of its own chain.** Nested coroutines nest
   chains: when coroutine A's body resumes coroutine B, a yield beneath B's resume suspends B
   and arrives at A; A's own yields suspend A and arrive at A's puller. Each pull drives
   exactly one chain one step.
3. **The value's type must BE the chain's element type, or the yield panics.** The compiler
   types the yielded expression as what it is — there is no context to adapt against, because
   which chain the yield meets is a runtime fact — and the meeting is checked where it
   happens: a `yield "x";` reaching a `Coroutine<int>` panics, a bare `yield;` reaching it
   panics, `yield 3;` reaching a `Coroutine<void>` panics. Inside a coroutine BODY the check
   stays static (§10), so the panic is reachable only from the helpers beneath it. *(Weighed
   and refused: a `yields T` clause on helper signatures — it would move this panic to compile
   time, and it would colour every yielding helper the way `async` colours callers, which is
   the disease door C exists to avoid. And an unchecked yield is not available at all: a value
   carries no type tag (§13), the pull site types its result statically, and a wrong value
   admitted here would corrupt the puller, not panic it.)*
4. **A native frame is a yield barrier** — Lua's C-boundary rule. A chain suspends by capturing
   Lyric frames; a native call's frame cannot be captured, so a yield executed beneath one — a
   host callback, a native function calling back into script — panics rather than suspending
   half a chain. A frame compiled by the opt-in JIT is a native frame for this rule.
5. **A running coroutine cannot be resumed.** `resume co` while `co` is suspended mid-resume —
   from its own chain or any other — panics: one chain, one driver.

All five arrive as panics through the same route as `std.core.coroutineEnded` (§4.4): not
catchable, ending the program with a backtrace that shows the chain. The backtrace of a
suspended-at-depth panic names the yield site and every frame down from the resume.

**Defers and the chain.** A `defer` runs when its frame exits — by return, by run-through, or
by an exception unwinding the chain toward the pull. Suspension is not an exit: a chain
abandoned mid-suspension — dropped, collected — runs NOTHING, exactly as a suspended body has
behaved since 1.x. Cleanup that must happen belongs to whoever drives the coroutine to its
end; the garbage collector is not an exit path and does not become one here.

**What stays static.** A coroutine body still ends with a bare `return;` (`LYR-SEM0039`), its
own yields still check against `T` where they stand, and the throwability of a pull stays the
type's (§Throwability of a pull) — a helper that throws beneath the body is a call the body
already had to handle or declare, at any depth.

## Throwability of a pull

Since 3.0 it belongs to the **type**: `Coroutine<int> throws Exception` is a different type from
`Coroutine<int>`, and it stays one through a field, an optional, a parameter and a return.

- A coroutine function's `throws` clause describes the coroutine it returns, not its call:
  `fn gen(): Coroutine<int> throws Exception` produces a `Coroutine<int> throws Exception`. The
  call itself demands nothing, because it runs no body — it builds a suspended frame.
- A **pull** — `resume` or `next()` — of a coroutine whose type throws is a throw site like any
  call to a `throws` function: an enclosing `try` handles it, or the enclosing function declares
  it (`LYR-SEM0034` otherwise). `next()` is lenient about exhaustion, never about throwing.
- Written elsewhere, the throwability is a type suffix (§2): `co: ?Coroutine<int> throws Exception`
  as a field, a parameter, a binding. `throws` without a type means any `Throwable`. The suffix is
  valid on a coroutine type and nowhere else (`LYR-SEM0084`).
- Assignment is one-directional: a coroutine that cannot throw fits where one that may is
  expected, and not the other way round. The refused direction is the one that used to drop the
  demand silently.

*(Before 3.0 the demand was attached to the CALL — the one event that cannot throw — so it
appeared to follow the local variable and vanished at the first indirection, and the exception
left the entry point as `LYR-VM0010`. The three alternatives weighed then and refused: treating
every pull as throwing taxes every ordinary coroutine; refusing a throwing coroutine a field
punishes programs that are already correct; tracking the origin at the pull closes the optional
and not the field. Only the type carries it everywhere.)*

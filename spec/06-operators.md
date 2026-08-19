# 6. Expressions and operators

Precedence and associativity are the table in the grammar (§2.2). This chapter defines what the
operators MEAN, and in particular the one rule behind all operator overloading: **an operator on
a non-primitive type IS an interface method call**, resolved exactly as the written call would
be, recorded at compile time. There is no second dispatch mechanism and no user-defined
operator beyond the interfaces named here.

## 6.1 Arithmetic

`+ - * /` on two operands of the SAME numeric type are the machine operations (§3.2: wrapping;
float per IEEE 754). `%` is numeric-only. Mixed numeric operands do not unify: `int + int32` is
an error, cast first.

On a non-primitive type, `a + b` is `a.add(b)` through `Add<T>` of `std.core`; likewise
`Sub<T>`, `Mul<T>`, `Div<T>`. The interfaces are **homogeneous** — operand and result are the
declaring type — by decision: a type conforms to `Mul` once (§5.1), and without overloading a
second `mul` cannot exist, so a two-parameter form would buy one fixed partner type and
nothing more. Mixed forms (`Vec2 * float`) are named methods.

Two string operators ride the same rule with library backing: `s1 + s2` is
`std.string.concat`, `s * n` is `std.string.repeat`.

## 6.2 Comparison and equality

`< <= > >=` on the same numeric type (and `char`) are machine comparisons; on `string` and on
conforming types they are `Ordered<T>.compare` — derived from ONE method, so the four cannot
disagree. `==`/`!=` on scalars are machine equality; on conforming types they are
`Equatable<T>.equals`. Conformance is required, not the method alone: an `equals` nobody
declared as `Equatable` does not become an operator.

`?T` compares only against `null`; comparing two optionals is an error (`LYR-SEM0059`) —
narrow first. Two values of one opaque alias compare by their underlying (§3.5).

## 6.3 Optionals: `??`, `!`, `?.`

- `a ?? b` — `a` if present, else `b`; `b` evaluates only then. The result is `T` when `b : T`,
  and `?T` when `b` is itself optional.
- `a!` — the value, or a panic (`LYR-VM0007`) that names nothing; `std.option.expect` carries a
  message.
- `a?.m(…)` — the call if present, else `null`; the result is optional.

## 6.4 Casts

`as` per §3.6. A non-numeric, non-opaque cast is the `Into<T>` conversion call, stored at
compile time like every operator.

## 6.5 Compound assignment

`x op= e` on a variable target — a local or a captured variable — is the operator applied and
stored: for interface-backed operators the synthesized call lowers whole. On a **field or
element** target the compound form is an error (`LYR-SEM0003`) telling the writer to spell it
out: the shorthand would evaluate the object or the index twice, and that stays visible in
source.

## 6.6 Interpolated strings

`f"a{x}b{y:N2}"` desugars to concatenation of the literal parts with, per hole: the matching
`std.string.fromXxx` converter for a primitive value, or `std.fmt.formatXxx(value, "spec")`
when a specifier is present. A hole whose type has no converter — a struct, a class, an opaque
alias — is an error; there is no implicit `Display` call in interpolation.

## 6.7 Blocks, `if`, `match` as expressions

`if (c) a else b` and `match` in value position unify their arm types: equal types, or one arm
`null` widening the result to the optional. Disagreeing arms are one error (`LYR-SEM0016`).
Block lambdas infer their return type from their `return` statements under the same
unification (chapter 7).

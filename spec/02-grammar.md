# Grammar

The syntax of Lyric 5 as one EBNF: what a file may hold, token by token. Source of the decisions:
[08 Syntax](https://github.com/lyriclang/lyric/blob/main/design/v5/spec/08-syntax.md).

## Scope

The canonical EBNF of Lyric 5 and the rules around it: the notation, the declarations, types,
statements, expressions and patterns, the choices the parser makes where the grammar leaves two
readings, and how the grammar is checked against the suite.

## 1. Notation and reading

1. The grammar is EBNF. `Rule = … .` defines a rule; `'x'` is a terminal; `A B` is a sequence,
   `A | B` a choice, `[ A ]` an option, `{ A }` any number of `A`, `( … )` a group; `(* … *)` is
   a note. A rule's name begins with a capital; a name in capitals is a class of tokens of
   [01](01-lexical.md).
2. A quoted **word** is the reserved word, or, for a contextual word (01 §3 rule 3), a name
   spelled that way: `'type'` is `IDENTIFIER` written `type`. Everywhere an `IDENTIFIER` stands, a
   contextual word may stand too; a reserved word never does.
3. A quoted **sign** is the token of [01 §5](01-lexical.md#5-punctuation-and-operators). The
   signs `'>>'`, `'>='` and `'>>='` are also the `'>'` that closes a list of type arguments or
   type parameters followed by the rest, written against it (01 §1 rule 2): `List<List<int>>`
   closes two lists, `type Pair<T>= (T, T);` closes one before its `=`.
4. The grammar takes a superset of the programs a compiler accepts. A program it takes may still
   be refused by a rule beside it — a name that resolves to nothing, a type that does not fit, a
   pattern where none may bind — and where the grammar leaves two readings of one text, §7 says
   which one the parser takes.
5. **The list rule** (08 D5/D6): a list of one element may stand without its brackets — `struct
   S :: I`, `throws E`, `catch (e in E)`, `<T :: Display>`, `@Test` —; a list of several stands in
   brackets — `:: [I, J]`, `throws [A, B]`, `catch (e in [A, B])`, `@[A, B]`. **A list may end
   in a comma** (08 Y9) wherever it stands between brackets, parentheses, braces or angle
   brackets; a tuple keeps its two elements before it.

The token classes:

| Class | Chapter 01 |
|---|---|
| `IDENTIFIER` | a name, §3 rule 1; `_` is one |
| `INT_LITERAL`, `FLOAT_LITERAL` | §4.1, §4.2 |
| `CHAR_LITERAL` | §4.3 |
| `STRING_LITERAL` | §4.4: one line, raw, multi-line |
| `BYTE_STRING` | §4.5 |
| `FSTRING_START`, `FSTRING_TEXT`, `HOLE_START`, `FORMAT_SPEC`, `HOLE_END`, `FSTRING_END` | §4.6: an f-string's opening (`f"`, `fr"`, `f"""`, `fr"""`), a run of its text, the `{` and `}` around a hole, the text after a hole's `:` at the hole's top level, and its closing quotes |
| `AT_NAME` | `@` and a name written against it, §5 rule 1 |

## 2. Files and declarations

```ebnf
Module          = { Attribute } [ 'module' ';' ] { TopLevelDecl } .
TopLevelDecl    = ImportDecl
                | { Attribute } [ Visibility ] Declaration .
Visibility      = 'pub' | 'internal' | 'private' .
Declaration     = FunctionDecl | StructDecl | ClassDecl | EnumDecl | InterfaceDecl | ExtendDecl
                | GlobalBinding | TypeAlias | ExternDecl | ExternBlock .
Name            = IDENTIFIER | Splice .

ImportDecl      = [ 'pub' ] 'import' Path [ ImportList | 'as' IDENTIFIER ] ';' .
ImportList      = '{' ImportItem { ',' ImportItem } [ ',' ] '}' .
ImportItem      = IDENTIFIER [ 'as' IDENTIFIER ] .
Path            = IDENTIFIER { '.' IDENTIFIER } .

Attribute       = AT_NAME AttributeRest
                | '@[' IDENTIFIER AttributeRest { ',' IDENTIFIER AttributeRest } [ ',' ] ']' .
AttributeRest   = { '.' IDENTIFIER } [ '{' [ FieldValue { ',' FieldValue } [ ',' ] ] '}'
                                     | '(' Expr ')' ] .
FieldValue      = IDENTIFIER '=' Expr .
```

1. A file is a module ([04 §2](04-modules.md)). `module;` alone is its header, which names
   nothing and carries the module's attributes; attributes at the top of a file without it belong
   to the first declaration.
2. An import takes no attribute, and of the visibility words only `pub` (`LYR-PAR0053`).

```ebnf
FunctionDecl    = FunctionHead ( Block | ';' ) .
FunctionHead    = [ 'inline' ] [ 'mut' ] ( 'fn' | 'macro' ) Name [ GenericParams ]
                  '(' [ Params ] ')' [ ':' ReturnType ] [ ThrowsClause ] .
Params          = Param { ',' Param } [ ',' ] .
Param           = { Attribute } [ '&' ] Name ':' Type [ '...' ] [ '=' Expr ] .
ThrowsClause    = 'throws' [ Type | '[' Type { ',' Type } [ ',' ] ']' ] .

ExternDecl      = 'extern' STRING_LITERAL ExternFunction .
ExternBlock     = 'extern' STRING_LITERAL '{' ExternMember { ExternMember } '}' .
ExternMember    = { Attribute } [ Visibility ] ExternFunction .
ExternFunction  = [ 'inline' ] [ 'mut' ] 'fn' Name [ GenericParams ] '(' [ ExternParams ] ')'
                  [ ':' ReturnType ] [ ThrowsClause ] [ '=' STRING_LITERAL ] ';' .
ExternParams    = '...' | Param { ',' Param } [ ',' [ '...' ] ] .

GlobalBinding   = ( 'let' | 'var' ) IDENTIFIER [ ':' Type ] [ '=' Expr ] ';' .
TypeAlias       = 'type' Name [ GenericParams ] '=' Type ';' .

GenericParams   = '<' GenericParam { ',' GenericParam } [ ',' ] '>' .
GenericParam    = IDENTIFIER [ '::' Bounds ] [ '=' Type ] .
Bounds          = Type | '[' Type { ',' Type } [ ',' ] ']' .
```

3. A function's `throws` is the function's own, written after its return type; `throws` alone
   is `Error` ([06](06-errors.md)). In a member, `static` stands before `inline` and `mut`
   (`LYR-PAR0032`).
4. A parameter's `&` marks a place ([03 §8](03-types.md)); `T...` makes the last parameter
   variadic. A bare `...` is C's variadic arguments and closes the parameters of an `extern`
   function alone ([13](13-abi.md)).

```ebnf
StructDecl      = 'struct' Name [ GenericParams ] [ '::' Conformances ] TypeBody .
ClassDecl       = 'class' Name [ GenericParams ] [ '::' Conformances ] TypeBody .
Conformances    = Conformance | '[' Conformance { ',' Conformance } [ ',' ] ']' .
Conformance     = Type [ 'by' IDENTIFIER ] .
TypeBody        = '{' { TypeMember } [ { Attribute } FieldDecl ] '}' .
TypeMember      = { Attribute } ( FieldDecl ',' | MemberBody [ ',' ] ) .
FieldDecl       = [ Visibility ] [ 'var' ] Name ':' Type [ '=' Expr ] .

EnumDecl        = 'enum' Name [ GenericParams ] [ '::' Bounds ]
                  '{' [ Variant { ',' Variant } [ ',' ] ] [ ';' { MemberDecl } ] '}' .
Variant         = { Attribute } Name [ '(' [ Type { ',' Type } [ ',' ] ] ')'
                                     | '{' [ VariantField { ',' VariantField } [ ',' ] ] '}'
                                     | '=' Expr ] .
VariantField    = { Attribute } Name ':' Type [ '=' Expr ] .

InterfaceDecl   = [ 'sealed' ] 'interface' Name [ GenericParams ] [ '::' Bounds ]
                  '{' { MemberDecl } '}' .
ExtendDecl      = 'extend' [ GenericParams ] Type [ '::' Bounds ] '{' { MemberDecl } '}' .

MemberDecl      = { Attribute } MemberBody .
MemberBody      = AssociatedType
                | [ Visibility ] ( 'static' StaticBinding | [ 'static' ] FunctionDecl ) .
StaticBinding   = ( 'let' | 'var' ) IDENTIFIER [ ':' Type ] [ '=' Expr ] ';' .
AssociatedType  = 'type' Name [ '::' Bounds ] [ '=' Type ] ';' .
```

5. In a struct or a class, a **field** is followed by `,` unless it stands last; a member that
   closes itself — a body's `}`, a `;` — needs none and may have one (08 D1). In an enum the
   variants are separated by `,` and end with `;` before the members (08 D2); an interface, an
   `extend` block and the members of an enum take no separator.
6. `by` delegates a conformance of a struct or a class to one of its fields (08 D7); after an
   enum's, an interface's or an `extend` block's `::` it has no place (`LYR-PAR0047`).

## 3. Types

```ebnf
Type            = { '?' | '??' } TypeCore [ 'throws' [ Type ] ] .
ReturnType      = { '?' | '??' } TypeCore .
TypeCore        = TypeAtom [ '.' '[' IDENTIFIER ']' ] { '[' [ INT_LITERAL ] ']' } .
TypeAtom        = Path [ TypeArgs ]
                | FunctionType
                | 'extern' STRING_LITERAL FunctionType
                | '(' Type ')'
                | TupleType
                | Splice .
TypeArgs        = '<' TypeArg { ',' TypeArg } [ ',' ] '>' .
TypeArg         = [ IDENTIFIER '=' ] Type .
FunctionType    = 'fn' '(' [ FnTypeParam { ',' FnTypeParam } [ ',' ] ] ')' '->' ReturnType
                  [ 'throws' [ ReturnType | '[' Type { ',' Type } [ ',' ] ']' ] ] .
FnTypeParam     = [ '&' ] Type .
TupleType       = '(' TupleElement ',' TupleElement { ',' TupleElement } [ ',' ] ')' .
TupleElement    = [ IDENTIFIER ':' ] Type .
```

1. `?` makes an optional of what follows it with its suffixes: `?T[]` is an optional array, an
   array of optionals is `(?T)[]`; `??T` is an optional of an optional ([03 §3](03-types.md)).
   `T[]` is an array, `T[4]` an inline array of four.
2. A function type reaches as far right as it can: `fn(int) -> void[]` returns `void[]`, and an
   array of functions is `(fn(int) -> void)[]`.
3. `throws` after a type is the type's own only where a type stands for a value — a field, a
   parameter, a binding, a type argument: `Coroutine<int> throws IoError`. After the return type
   of a function, a lambda or a function type, the `throws` belongs to the function; that is why
   a return type is read as `ReturnType`. Where a function type is itself a return type, a
   `throws` behind it says neither whose it is, and parentheses must (`LYR-PAR0056`).
4. `T.[f]` is the type of the field a `comptime for` round names ([11](11-metaprogramming.md)).

## 4. Statements

```ebnf
Block           = '{' { Statement } '}' .
ValueBlock      = '{' { Statement } [ Expr | 'throw' Expr ] '}' .
Statement       = ';'
                | Block
                | 'unsafe' Block
                | LetStmt
                | 'using' 'let' IDENTIFIER [ ':' Type ] '=' Expr ';'
                | FunctionDecl
                | IfStmt
                | 'comptime' ( IfStmt | ForStmt )
                | [ IDENTIFIER ':' ] ( WhileStmt | DoStmt | ForStmt )
                | LoopExpr
                | MatchExpr
                | 'break' [ IDENTIFIER ] [ Expr ] ';'
                | 'continue' [ IDENTIFIER ] ';'
                | 'return' [ Expr ] ';'
                | 'yield' [ Expr ] ';'
                | 'defer' ( Block | Expr ';' )
                | 'throw' Expr ';'
                | 'try' Block { CatchClause }
                | ExprStmt .

LetStmt         = ( 'let' | 'var' ) ( IDENTIFIER [ ':' Type ] [ '=' Expr [ 'else' Block ] ]
                                    | Pattern [ ':' Type ] '=' Expr [ 'else' Block ] ) ';' .
IfStmt          = 'if' '(' Condition ')' Block [ 'else' ( IfStmt | Block ) ] .
Condition       = Expr | 'let' Pattern '=' Expr .
WhileStmt       = 'while' '(' Condition ')' Block .
DoStmt          = 'do' Block 'while' '(' Expr ')' ';' .
ForStmt         = 'for' '(' ( IDENTIFIER | TuplePattern ) 'in' Expr ')' Block .
CatchClause     = 'catch' '(' CatchBinding ')' Block .
CatchBinding    = IDENTIFIER [ ':' Type | 'in' Bounds ] .

ExprStmt        = Expr ';'
                | BlockEnded [ ';' ] .
BlockEnded      = Postfix TrailingLambda
                | MacroCall
                | Splice .
```

1. A statement's body is a block, always (08 S1): `if (c) x;` is refused (`LYR-PAR0017`).
2. A **value block** — a match arm, a lambda's body, a branch of an `if` expression, a clause of
   a `try` expression, the right of `??`, the block of `comptime` — may end in an expression
   without `;`, its value ([07 §3](07-statements.md#3-value-blocks)). An `if` with its final
   `else`, a `match` and a `loop` standing last there are that value; elsewhere they are
   statements. Every other block ends with its statements.
3. A statement that ends in a block — a call with a trailing block, a macro site with a block —
   needs no `;` and may have one. An expression statement is a call, an assignment, an increment
   or an expression a rule of 07 names; what else stands there is the checker's to refuse.
4. A **local function** is a `fn` in a body: no type parameters, no default, no variadic
   parameter, a body of its own (`LYR-PAR0060`). `using` binds with `let` only (`LYR-PAR0052`).
5. A label names the loop that follows it and only a loop (`LYR-PAR0046`); `loop` is a word only
   before its `{`, `unsafe` only before its block, `using` only before `let`.
6. A `;` alone is an **empty statement** (08 S10): it stands wherever a statement may, a value
   block's included, does nothing, and `lyric fmt` drops it.

## 5. Expressions

| Level | Operators | Associativity |
|---|---|---|
| 1 | postfix `.` `?.` `[ ]` `( )` `++` `--` `!` `with { }`, a trailing block | left |
| 2 | prefix `!` `-` `~` `++` `--` `^`, `try`, `throw`, `comptime` | right |
| 3 | `as` | left |
| 4 | `*` `/` `%` `*%` | left |
| 5 | `+` `-` `+%` `-%` | left |
| 6 | `<<` `>>` | left |
| 7 | `..` `..=` | none |
| 8 | `&` | left |
| 9 | `^` | left |
| 10 | `\|` | left |
| 11 | `<` `<=` `>` `>=` `is` `in` `!in` | none |
| 12 | `==` `!=` | none |
| 13 | `&&` | left |
| 14 | `\|\|` | left |
| 15 | `??` | right |
| 16 | `=` and the compound assignments | right |

```ebnf
Expr            = 'try' Expr { CatchExpr }
                | 'try' ( '?' | '!' ) Expr
                | Assignment .
CatchExpr       = 'catch' '(' CatchBinding ')' ( ValueBlock | Expr ) .
Assignment      = Coalesce [ AssignOp Expr ] .
AssignOp        = '=' | '+=' | '-=' | '*=' | '/=' | '%=' | '+%=' | '-%=' | '*%=' | '&=' | '|='
                | '^=' | '<<=' | '>>=' | '&&=' | '||=' | '??=' .
Coalesce        = Or [ '??' ( ValueBlock | Coalesce ) ] .
Or              = And { '||' And } .
And             = Equality { '&&' Equality } .
Equality        = Comparison [ ( '==' | '!=' ) Comparison ] .
Comparison      = BitOr [ CompareOp BitOr | 'is' Type ] .
CompareOp       = '<' | '<=' | '>' | '>=' | 'in' | '!in' .
BitOr           = BitXor { '|' BitXor } .
BitXor          = BitAnd { '^' BitAnd } .
BitAnd          = Range { '&' Range } .
Range           = Shift [ ( '..' | '..=' ) Shift ] .
Shift           = Additive { ( '<<' | '>>' ) Additive } .
Additive        = Multiplicative { ( '+' | '-' | '+%' | '-%' ) Multiplicative } .
Multiplicative  = Cast { ( '*' | '/' | '%' | '*%' ) Cast } .
Cast            = Prefix { 'as' Type } .
Prefix          = ( '!' | '-' | '~' | '++' | '--' | '^' | 'try' | 'throw' ) Prefix
                | 'comptime' ( ValueBlock | Prefix )
                | 'comptime' 'if' '(' Expr ')' Expr 'else' Expr
                | Postfix .

Postfix         = Primary { PostfixOp } .
PostfixOp       = '.' ( IDENTIFIER | INT_LITERAL | FLOAT_LITERAL )
                | '.' '[' Expr ']' [ InitBody ]
                | '.' '[' Expr ',' Expr ']'
                | '?.' IDENTIFIER
                | '[' IndexElement ']'
                | [ TypeArgs ] '(' [ Args ] ')'
                | '++' | '--' | '!'
                | 'with' '{' [ WithField { ',' WithField } [ ',' ] ] '}'
                | TrailingLambda .
IndexElement    = Expr
                | [ Expr ] ( '..' | '..=' ) [ Expr ] .
Args            = Arg { ',' Arg } [ ',' ] .
Arg             = [ IDENTIFIER ':' ] [ '&' ] Expr [ '...' ] .
WithField       = IDENTIFIER { '.' IDENTIFIER } '=' Expr .
TrailingLambda  = '{' [ BlockParam { ',' BlockParam } '=>' ] { Statement } [ Expr | 'throw' Expr ] '}' .
BlockParam      = [ '&' ] IDENTIFIER | TuplePattern .

Primary         = Literal
                | FString
                | 'this'
                | IDENTIFIER
                | Path TypeArgs
                | Path [ TypeArgs { '.' IDENTIFIER } ] InitBody
                | '.' IDENTIFIER [ InitBody ]
                | IDENTIFIER '=>' LambdaBody
                | '(' [ LambdaParam { ',' LambdaParam } [ ',' ] ] ')'
                  [ ':' ReturnType [ ThrowsClause ] ] '=>' LambdaBody
                | '(' Expr ')'
                | '(' Expr ',' Expr { ',' Expr } [ ',' ] ')'
                | '[' [ Expr { ',' Expr } [ ',' ] ] ']'
                | IfExpr
                | MatchExpr
                | LoopExpr
                | MacroCall
                | 'quote' ( '{' { TopLevelDecl } '}' | ValueBlock )
                | Splice
                | AT_NAME [ '(' [ Args ] ')' ] .
Literal         = INT_LITERAL | FLOAT_LITERAL | CHAR_LITERAL | STRING_LITERAL | BYTE_STRING
                | 'true' | 'false' | 'null' .
FString         = FSTRING_START { FSTRING_TEXT | HOLE_START Expr [ FORMAT_SPEC ] HOLE_END }
                  FSTRING_END .
InitBody        = '{' [ InitItem { ',' InitItem } [ ',' ] ] '}' .
InitItem        = IDENTIFIER [ '=' Expr ]
                | '[' Expr ']' '=' Expr
                | 'comptime' 'for' '(' IDENTIFIER 'in' Expr ')' '[' Expr ']' '=' Expr .
LambdaParam     = [ '&' ] IDENTIFIER [ ':' Type ]
                | TuplePattern [ ':' Type ] .
LambdaBody      = ValueBlock | Expr .
IfExpr          = 'if' '(' Expr ')' ( ValueBlock | Expr ) 'else' ( ValueBlock | Expr ) .
MatchExpr       = 'match' '(' Expr ')' '{' { MatchArm ',' | BlockArm [ ',' ] } [ MatchArm ] '}' .
MatchArm        = Pattern [ 'if' Expr ] '=>' Expr .
BlockArm        = Pattern [ 'if' Expr ] '=>' ValueBlock .
LoopExpr        = [ IDENTIFIER ':' ] 'loop' Block .
MacroCall       = IDENTIFIER '!' ( '(' [ Expr { ',' Expr } [ ',' ] ] ')' [ ValueBlock ]
                                 | ValueBlock ) .
Splice          = '#' '{' Expr '}' .
```

1. **Assignment is an expression** (08 S8), the lowest level, right-associative. A comparison and
   an equality do not chain: `a < b < c` is refused with the form to write (`LYR-PAR0059`), and
   `is`, a test at the comparisons' level ([08 §4](08-expressions.md)), chains with none of them.
   A range does not chain either (`LYR-PAR0005`).
2. `try` covers everything to its right ([06 §4](06-errors.md)): `try a + b` is `try (a + b)`.
   At the start of an expression it covers that expression and takes its `catch` clauses; to the
   right of an operator the plain `try` covers from where it stands, and `try?`, `try!` and a
   `try` with clauses stand at the start only (`LYR-PAR0050`, `LYR-PAR0051`). `throw e` is a
   prefix: `x ?? throw e`.
3. `a..b` is a value ([03](03-types.md)); in an index the bounds may be left open — `xs[..b]`,
   `xs[a..]`, `xs[..]` — and `^n` counts from the end.
4. A lambda is written in three forms (08 F1): `(n: int): int => …`, `x => …`, and a **trailing
   block** after a callee or a call, `xs.map { it * 2 }`, `fold(0) { acc, x => acc + x }`, its
   parameters before `=>` or the implicit `it`.
5. `if` as an expression has its `else` (`LYR-PAR0036`). `'comptime' 'if'` in an expression
   chooses between two (`LYR-PAR0061`).
6. A match arm whose body is an expression is followed by `,` unless it stands last; a block arm
   may omit it (08 S9).
7. `name!(…)` and `name! { … }` are a macro's site ([11 §5](11-metaprogramming.md#5-macros)):
   the `!` written against the name, before `(` or `{`. `quote { … }` holds declarations when
   its first token begins one, statements otherwise; `#{ e }` splices inside it, where an
   expression, a type or a declaration's name stands.
8. `e.[f]`, `e.[v, p]`, `E.[v] { … }` and the items `[f] = e` and `comptime for (f in …) [f] = e`
   of an initializer reach fields and variants by a compile-time info
   ([11](11-metaprogramming.md)).

## 6. Patterns

```ebnf
Pattern         = PatternTerm { '|' PatternTerm } .
PatternTerm     = PatternLiteral [ ( '..' | '..=' ) PatternLiteral ]
                | IDENTIFIER ( ':' Type | 'in' Bounds )
                | Path [ Payload ]
                | '.' IDENTIFIER [ Payload ]
                | '(' Pattern { ',' Pattern } [ ',' ] ')'
                | '[' [ ArrayElement { ',' ArrayElement } [ ',' ] ] ']' .
PatternLiteral  = [ '-' ] ( INT_LITERAL | FLOAT_LITERAL ) | STRING_LITERAL | CHAR_LITERAL
                | 'true' | 'false' | 'null' .
Payload         = '(' [ Pattern { ',' Pattern } [ ',' ] ] ')'
                | '{' [ FieldPattern { ',' FieldPattern } [ ',' ] ] '}' .
FieldPattern    = IDENTIFIER [ '=' Pattern ] .
ArrayElement    = Pattern | '..' [ IDENTIFIER ] .
TuplePattern    = '(' Pattern { ',' Pattern } [ ',' ] ')' .
```

1. A name alone binds, always; a variant is written `.Red` or `Signal.Red` (08 Y6,
   [09](09-patterns.md)). `_` binds nothing. `c: Circle` tests a type and `s in [Circle, Rect]`
   a set of them.
2. A pattern's literal may be negative; a range's bounds are literals. One parenthesized pattern
   is a group, two or more a tuple. An array pattern holds at most one `..` (`LYR-PAR0033`).

## 7. Where the grammar leaves two readings

The EBNF is ambiguous at a few places, on purpose: each is settled by looking ahead at the
tokens, never by meaning. In order of how often a program meets them:

1. **`<` after a name** opens type arguments when it closes balanced over tokens a type may hold
   and is followed by `(` — a call, `f<int>()` —, by `{` that opens an initializer, or, for a
   path in value position, by `.`, `)`, `]`, `}`, `,`, `;` or the end of the text
   (`map(xs, ident<int>)`). Everywhere else it is the comparison.
2. **A `{` after a name** opens an initializer when the braces are empty, hold `name =` whose
   value ends at `,` or `}`, hold names separated by `,` — the shorthand `S { v, w }` —, or open
   with `[` or `comptime for`. Otherwise the braces are a trailing block: `run { total = 5; }`,
   whose `;` makes it a statement's. **No statement begins with an initializer** — its value
   would be dropped (`LYR-PAR0055`); in a value position, inside any parentheses, brackets or
   braces, and after `=`, one may stand.
3. **A trailing block** follows a name, a member or a call; it holds statements when it begins
   with a statement's word or holds a `;` at its own level, and one expression otherwise.
   `{ a, b => … }` names its parameters.
4. **A `(`** begins a lambda when its matching `)` is followed by `=>` or by `:` and a return
   type and `=>`; a tuple when a `,` follows its first element; a group otherwise. In a match
   arm's guard, the first `(` is a group and a name before `=>` is no lambda.
5. **A name after `break`** is a label when a loop around the `break` carries it, the beginning
   of the value otherwise (07 §1 rule 3).
6. **An `if` at the start of a statement** in a value block is the block's value when its chain
   ends in an `else` and nothing follows it; otherwise, and in every other block, it is the
   statement. The same holds for `match` and `loop`.
7. **`try?` and `try!`**: the sign is written against the word; with a space between, `!` negates
   what follows — `try !done()`.
8. **`!` after a name** before `(` or `{`, written against the name, is a macro's site; anywhere
   else it unwraps: `x! in xs`, `x!.f()`.
9. **`.` and a digit**: `t.0` is a tuple's element, `t.0.1` two of them; `3.show()` calls on `3`;
   `1..3` is a range.

## 8. The check

1. `tools/grammar.py` reads the EBNF of this chapter, cuts a program into the tokens of 01 and
   asks whether it is a `Module`. Every program the suite expects to compile — each case that
   leads with `run` or `check` and expects no `error:`, every file of a package case — must be
   one; the check runs in this repository's CI.
2. The check runs one way. A program the grammar takes may be refused by a rule beside it (§1
   rule 4), so the cases that expect an error are not asked.

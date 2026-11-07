#!/usr/bin/env python3
"""The grammar of chapter 02, checked against the programs a compiler accepts.

Reads the EBNF out of spec/02-grammar.md, cuts each program into the tokens of chapter 01 and
asks an Earley recognizer whether the program is a `Module`. The check runs one way only: every
program the suite says compiles must be a sentence of the grammar. A program the grammar takes
may still be refused, by a rule beside it (02 §1).

    python3 tools/grammar.py                 every accepting case of the suite
    python3 tools/grammar.py PATH...         these files, or every .lyr below these directories

Only the standard library; Python 3.9 or later.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------------------------
# Tokens (chapter 01)
# ---------------------------------------------------------------------------------------------

RESERVED = set("""
    import as pub internal private static struct class enum interface extend fn mut let var
    if else while do for in is match break continue return yield defer try catch throw
    true false null this comptime inline quote macro
""".split())

# Longest first within each leading character; the '>' family is cut into single '>' (and a
# trailing '='), joined to what precedes, so a list of type arguments can close on each.
OPERATORS = sorted("""
    ... ..= .. . <<= << <= < -> => == = != ??= ?? ?. ? :: : +%= +% += ++ + -%= -% -= -- -
    *%= *% *= * /= / %= % &&= && &= & ||= || |= | ^= ^ ~ # ( ) [ ] { } , ;
""".split(), key=len, reverse=True)


@dataclass
class Token:
    kind: str      # 'IDENTIFIER', 'INT_LITERAL', … or the text of a word or a sign
    text: str
    line: int
    col: int
    joined: bool = False  # no space before it: the rest of a '>>', '>=' or '>>='


class LexError(Exception):
    pass


class Lexer:
    def __init__(self, text: str):
        if text.startswith("﻿"):
            text = text[1:]
        self.s = text
        self.i = 0
        self.out: list[Token] = []

    # position --------------------------------------------------------------------------------

    def at(self, k: int = 0) -> str:
        j = self.i + k
        return self.s[j] if j < len(self.s) else "\0"

    def where(self, i: int) -> tuple[int, int]:
        line = self.s.count("\n", 0, i) + 1
        return line, i - (self.s.rfind("\n", 0, i) + 1) + 1

    def emit(self, kind: str, start: int, joined: bool = False) -> None:
        line, col = self.where(start)
        self.out.append(Token(kind, self.s[start:self.i], line, col, joined))

    def fail(self, message: str) -> None:
        line, col = self.where(self.i)
        raise LexError(f"{line}:{col}: {message}")

    # trivia ----------------------------------------------------------------------------------

    def skip_trivia(self) -> None:
        while True:
            while self.at() in " \t\r\n":
                self.i += 1
            if self.at() == "/" and self.at(1) == "/":
                while self.at() not in "\n\0":
                    self.i += 1
                continue
            if self.at() == "/" and self.at(1) == "*":
                self.i += 2
                depth = 1
                while depth and self.at() != "\0":
                    if self.at() == "/" and self.at(1) == "*":
                        self.i += 2
                        depth += 1
                    elif self.at() == "*" and self.at(1) == "/":
                        self.i += 2
                        depth -= 1
                    else:
                        self.i += 1
                if depth:
                    self.fail("unterminated comment")
                continue
            return

    # the whole text --------------------------------------------------------------------------

    def tokens(self) -> list[Token]:
        self.run(hole=False)
        return self.out

    def run(self, hole: bool) -> None:
        """Tokens up to the end of the text, or, in a hole of an f-string, up to the '}' or ':'
        that ends the expression at its top level."""
        depth = 0
        while True:
            self.skip_trivia()
            c = self.at()
            if c == "\0":
                if hole:
                    self.fail("unterminated f-string hole")
                return
            if hole and depth == 0 and c == "}":
                return
            if hole and depth == 0 and c == ":" and self.at(1) != ":":
                return
            start = self.i
            if c == "f" and (self.at(1) == '"' or self.at(1) == "r" and self.at(2) == '"'):
                self.fstring()
            elif c == "r" and (self.at(1) == '"' or self.at(1) == "#" and self.hashes_then_quote(1)):
                self.raw_string()
            elif c == "b" and self.at(1) == '"':
                self.i += 1
                self.quoted('"')
                self.emit("BYTE_STRING", start)
            elif c == "@":
                self.i += 1
                if self.at() == "[":
                    self.i += 1
                    self.emit("@[", start)
                elif self.is_start(self.at()):
                    while self.is_cont(self.at()):
                        self.i += 1
                    self.emit("AT_NAME", start)
                else:
                    self.fail("'@' without a name")
            elif self.is_start(c):
                while self.is_cont(self.at()):
                    self.i += 1
                word = self.s[start:self.i]
                self.emit(word if word in RESERVED else "IDENTIFIER", start)
            elif c.isdigit():
                self.number()
            elif c == '"':
                if self.at(1) == '"' and self.at(2) == '"':
                    self.multiline(raw=False)
                else:
                    self.quoted('"')
                self.emit("STRING_LITERAL", start)
            elif c == "'":
                self.quoted("'")
                self.emit("CHAR_LITERAL", start)
            elif c == ">":
                # '>', '>>', '>=', '>>=': one '>' at a time, the rest joined to it
                self.i += 1
                self.emit(">", start)
                while self.at() == ">" or self.at() == "=" and self.s[self.i - 1] == ">":
                    if self.at() == "=" and self.at(1) == "=":
                        break
                    p = self.i
                    self.i += 1
                    self.emit(self.s[p], p, joined=True)
                    if self.s[p] == "=":
                        break
            elif c == "!" and self.at(1) == "i" and self.at(2) == "n" and not self.is_cont(self.at(3)):
                self.i += 3
                self.emit("!in", start)
            elif c == "!":
                self.i += 2 if self.at(1) == "=" else 1
                self.emit(self.s[start:self.i], start)
            else:
                for op in OPERATORS:
                    if self.s.startswith(op, self.i):
                        self.i += len(op)
                        self.emit(op, start)
                        break
                else:
                    self.fail(f"no token begins with {c!r}")
                if hole:
                    if c in "([{":
                        depth += 1
                    elif c in ")]}" and depth > 0:
                        depth -= 1

    @staticmethod
    def is_start(c: str) -> bool:
        return c == "_" or ("a" <= c <= "z") or ("A" <= c <= "Z")

    @classmethod
    def is_cont(cls, c: str) -> bool:
        return cls.is_start(c) or c.isdigit() and c.isascii()

    def hashes_then_quote(self, k: int) -> bool:
        while self.at(k) == "#":
            k += 1
        return self.at(k) == '"'

    # literals --------------------------------------------------------------------------------

    def number(self) -> None:
        start = self.i
        kind = "INT_LITERAL"
        if self.at() == "0" and self.at(1) in "xXoObB":
            self.i += 2
            while self.at().isalnum() or self.at() == "_":
                self.i += 1
        else:
            self.digits()
            if self.at() == "." and self.at(1).isdigit():
                kind = "FLOAT_LITERAL"
                self.i += 1
                self.digits()
            if self.at() in "eE" and (self.at(1).isdigit() or self.at(1) in "+-" and self.at(2).isdigit()):
                kind = "FLOAT_LITERAL"
                self.i += 2
                self.digits()
            if self.at() in "iuf" and self.at(1).isdigit():
                if self.at() == "f":
                    kind = "FLOAT_LITERAL"
                self.i += 1
                while self.at().isdigit():
                    self.i += 1
        self.emit(kind, start)

    def digits(self) -> None:
        while self.at().isdigit() or self.at() == "_":
            self.i += 1

    def quoted(self, q: str) -> None:
        """A one-line string, byte string or character, escapes skipped over."""
        self.i += 1
        while self.at() != q:
            if self.at() in "\n\0":
                self.fail("unterminated literal")
            self.i += 2 if self.at() == "\\" else 1
        self.i += 1

    def multiline(self, raw: bool) -> None:
        self.i += 3
        while not self.s.startswith('"""', self.i):
            if self.at() == "\0":
                self.fail("unterminated multi-line string")
            self.i += 2 if self.at() == "\\" and not raw else 1
        self.i += 3

    def raw_string(self) -> None:
        start = self.i
        self.i += 1  # 'r'
        hashes = 0
        while self.at() == "#":
            hashes += 1
            self.i += 1
        if hashes == 0 and self.s.startswith('"""', self.i):
            self.multiline(raw=True)
        else:
            close = '"' + "#" * hashes
            end = self.s.find(close, self.i + 1)
            if end < 0:
                self.fail("unterminated raw string")
            self.i = end + len(close)
        self.emit("STRING_LITERAL", start)

    def fstring(self) -> None:
        start = self.i
        self.i += 1
        raw = self.at() == "r"
        if raw:
            self.i += 1
        triple = self.s.startswith('"""', self.i)
        self.i += 3 if triple else 1
        self.emit("FSTRING_START", start)
        close = '"""' if triple else '"'
        while True:
            chunk = self.i
            while not self.s.startswith(close, self.i):
                c = self.at()
                if c == "\0" or c == "\n" and not triple:
                    self.fail("unterminated f-string")
                if c == "{" and self.at(1) == "{" or c == "}" and self.at(1) == "}":
                    self.i += 2
                elif c == "{":
                    break
                elif c == "\\" and not raw:
                    # '\u{…}' holds braces of its own, which open no hole
                    if self.at(1) == "u" and self.at(2) == "{":
                        end = self.s.find("}", self.i)
                        self.i = end + 1 if end > 0 else self.i + 3
                    else:
                        self.i += 2
                else:
                    self.i += 1
            if self.i > chunk:
                self.emit("FSTRING_TEXT", chunk)
            if self.s.startswith(close, self.i):
                p = self.i
                self.i += len(close)
                self.emit("FSTRING_END", p)
                return
            p = self.i
            self.i += 1
            self.emit("HOLE_START", p)
            self.run(hole=True)
            if self.at() == ":":
                self.i += 1
                p = self.i
                depth = 0
                while not (self.at() == "}" and depth == 0):
                    if self.at() in "\n\0":
                        self.fail("unterminated format spec")
                    if self.at() in "{([":
                        depth += 1
                    elif self.at() in "})]" and depth:
                        depth -= 1
                    self.i += 1
                self.emit("FORMAT_SPEC", p)
            p = self.i
            self.i += 1
            self.emit("HOLE_END", p)


# ---------------------------------------------------------------------------------------------
# The EBNF of chapter 02
# ---------------------------------------------------------------------------------------------
#
#   Rule      = Name '=' Choice '.'
#   Choice    = Sequence { '|' Sequence }
#   Sequence  = { Item }
#   Item      = Name | Terminal | '[' Choice ']' | '{' Choice '}' | '(' Choice ')'
#
# A Name in capitals is a token class of chapter 01; a quoted terminal is a sign or a word, and a
# word that is not reserved matches an IDENTIFIER spelled that way (01 §3 rule 3). '(* … *)' is
# a note.

TOKEN_CLASSES = {
    "IDENTIFIER", "INT_LITERAL", "FLOAT_LITERAL", "CHAR_LITERAL", "STRING_LITERAL", "BYTE_STRING",
    "FSTRING_START", "FSTRING_TEXT", "HOLE_START", "FORMAT_SPEC", "HOLE_END", "FSTRING_END",
    "AT_NAME",
}


class GrammarError(Exception):
    pass


def ebnf_blocks(markdown: str) -> str:
    return "\n".join(m.group(1) for m in re.finditer(r"```ebnf\n(.*?)```", markdown, re.S))


def read_rules(text: str) -> dict[str, list]:
    text = re.sub(r"\(\*.*?\*\)", " ", text, flags=re.S)
    toks = re.findall(r"'(?:[^'\\]|\\.)*'|\"[^\"]*\"|[A-Za-z_][A-Za-z0-9_]*|[=|.\[\]{}()]", text)
    pos = 0

    def peek() -> str | None:
        return toks[pos] if pos < len(toks) else None

    def take(expected: str | None = None) -> str:
        nonlocal pos
        if pos >= len(toks):
            raise GrammarError(f"the EBNF ends early; expected {expected}")
        t = toks[pos]
        if expected is not None and t != expected:
            raise GrammarError(f"expected {expected!r} in the EBNF, found {t!r} near {' '.join(toks[max(0, pos - 6):pos + 3])}")
        pos += 1
        return t

    def choice():
        alts = [sequence()]
        while peek() == "|":
            take()
            alts.append(sequence())
        return ("alt", alts)

    def sequence():
        items = []
        while peek() not in (None, "|", ".", "]", "}", ")"):
            t = take()
            if t == "[":
                items.append(("opt", choice()))
                take("]")
            elif t == "{":
                items.append(("rep", choice()))
                take("}")
            elif t == "(":
                items.append(choice())
                take(")")
            elif t[0] in "'\"":
                items.append(("t", t[1:-1]))
            else:
                items.append(("n", t))
        return ("seq", items)

    rules: dict[str, list] = {}
    while pos < len(toks):
        name = take()
        if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", name):
            raise GrammarError(f"a rule's name is a capitalised word: {name!r}")
        take("=")
        body = choice()
        take(".")
        if name in rules:
            raise GrammarError(f"rule {name} is given twice")
        rules[name] = body
    return rules


class Grammar:
    """The rules turned into plain productions: every '[…]', '{…}' and '(…)' a rule of its own."""

    def __init__(self, rules: dict[str, list]):
        self.prods: dict[str, list[tuple]] = {}
        self.fresh = 0
        self.literal_terminals: set[str] = set()
        for name, body in rules.items():
            self.prods[name] = self.alternatives(body)
        undefined = sorted({s[1] for alts in self.prods.values() for alt in alts for s in alt
                            if s[0] == "n" and s[1] not in self.prods and s[1] not in TOKEN_CLASSES})
        if undefined:
            raise GrammarError("used and never defined: " + ", ".join(undefined))
        used = {s[1] for alts in self.prods.values() for alt in alts for s in alt if s[0] == "n"}
        unused = sorted(n for n in rules if n not in used and n != "Module")
        if unused:
            raise GrammarError("defined and never used: " + ", ".join(unused))
        self.nullable = self.compute_nullable()
        self.first = self.compute_first()

    def new(self, alts: list[tuple]) -> tuple:
        self.fresh += 1
        name = f"#{self.fresh}"
        self.prods[name] = alts
        return ("n", name)

    def alternatives(self, node) -> list[tuple]:
        if node[0] == "alt":
            return [self.sequence(a) for a in node[1]]
        return [self.sequence(node)]

    def sequence(self, node) -> tuple:
        assert node[0] == "seq"
        return tuple(self.symbol(item) for item in node[1])

    def symbol(self, item) -> tuple:
        kind = item[0]
        if kind == "t":
            self.literal_terminals.add(item[1])
            return item
        if kind == "n":
            return item
        if kind == "alt":
            return self.new(self.alternatives(item))
        if kind == "opt":
            return self.new([()] + self.alternatives(item[1]))
        if kind == "rep":
            # left recursion, which an Earley recognizer walks in linear time
            inner = self.alternatives(item[1])
            self.fresh += 1
            name = f"#{self.fresh}"
            self.prods[name] = [()] + [(("n", name),) + alt for alt in inner]
            return ("n", name)
        raise AssertionError(kind)

    def compute_nullable(self) -> set[str]:
        nullable: set[str] = set()
        changed = True
        while changed:
            changed = False
            for name, alts in self.prods.items():
                if name in nullable:
                    continue
                if any(all(s[0] == "n" and s[1] in nullable for s in alt) for alt in alts):
                    nullable.add(name)
                    changed = True
        return nullable

    def compute_first(self) -> dict[str, set[str]]:
        """The terminals a rule can begin with, as match keys (see `keys`)."""
        first: dict[str, set[str]] = {n: set() for n in self.prods}
        changed = True
        while changed:
            changed = False
            for name, alts in self.prods.items():
                for alt in alts:
                    for s in alt:
                        if s[0] == "t":
                            add = {key_of_literal(s[1])}
                        elif s[1] in TOKEN_CLASSES:
                            add = {s[1]}
                        else:
                            add = first[s[1]]
                        if not add <= first[name]:
                            first[name] |= add
                            changed = True
                        if not (s[0] == "n" and s[1] in self.nullable):
                            break
        return first


def key_of_literal(text: str) -> str:
    """The key a terminal is filed under for the lookahead: a word that may be a name is filed
    under IDENTIFIER, a sign under its first token."""
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text) and text not in RESERVED:
        return "IDENTIFIER"
    if text.startswith(">"):
        return ">"
    return text


def match(symbol: tuple, tokens: list[Token], i: int) -> int:
    """How many tokens the terminal symbol takes at i: 0 when it does not match."""
    if i >= len(tokens):
        return 0
    t = tokens[i]
    if symbol[0] == "n":  # a token class
        return 1 if t.kind == symbol[1] else 0
    text = symbol[1]
    if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", text):
        if text in RESERVED:
            return 1 if t.kind == text else 0
        return 1 if t.kind == "IDENTIFIER" and t.text == text else 0
    if text in (">>", ">=", ">>="):
        n = len(text)
        if i + n > len(tokens) or tokens[i].kind != ">":
            return 0
        for k in range(1, n):
            if not tokens[i + k].joined or tokens[i + k].kind != text[k]:
                return 0
        return n
    return 1 if t.kind == text else 0


# ---------------------------------------------------------------------------------------------
# Earley
# ---------------------------------------------------------------------------------------------


class Rejected(Exception):
    def __init__(self, token: Token | None, expected: set[str]):
        self.token = token
        self.expected = expected


def recognize(g: Grammar, start: str, tokens: list[Token]) -> None:
    n = len(tokens)
    prods = g.prods
    nullable = g.nullable
    first = g.first
    # an item: (rule, alternative index, dot, origin)
    sets: list[dict] = [dict() for _ in range(n + 1)]
    # per set: items waiting on a rule, by rule name
    waiting: list[dict[str, list]] = [dict() for _ in range(n + 1)]
    # scans that land beyond the next set ('>>' takes two tokens)
    pending: list[list] = [[] for _ in range(n + 2)]

    def lookahead_ok(name: str, i: int) -> bool:
        if name in nullable:
            return True
        if i >= n:
            return False
        f = first[name]
        k = tokens[i].kind
        return k in f or (k == "IDENTIFIER" and "IDENTIFIER" in f)

    def add(i: int, item: tuple, agenda: list) -> None:
        if item not in sets[i]:
            sets[i][item] = True
            agenda.append(item)

    for a in range(len(prods[start])):
        sets[0][(start, a, 0, 0)] = True
    for i in range(n + 1):
        agenda = list(sets[i].keys())
        for item in pending[i]:
            add(i, item, agenda)
        while agenda:
            rule, a, dot, origin = agenda.pop()
            alt = prods[rule][a]
            if dot == len(alt):
                for (r2, a2, d2, o2) in waiting[origin].get(rule, ()):
                    add(i, (r2, a2, d2 + 1, o2), agenda)
                continue
            sym = alt[dot]
            if sym[0] == "n" and sym[1] not in TOKEN_CLASSES:
                name = sym[1]
                waiting[i].setdefault(name, []).append((rule, a, dot, origin))
                if lookahead_ok(name, i):
                    for k in range(len(prods[name])):
                        add(i, (name, k, 0, i), agenda)
                if name in nullable:  # Aycock and Horspool: step over what may be empty
                    add(i, (rule, a, dot + 1, origin), agenda)
            else:
                width = match(sym, tokens, i)
                if width == 1:
                    sets[i + 1][(rule, a, dot + 1, origin)] = True
                elif width > 1:
                    pending[i + width].append((rule, a, dot + 1, origin))
        if i < n and not sets[i + 1] and not any(pending[j] for j in range(i + 1, min(n, i + 3) + 1)):
            expected = set()
            for (rule, a, dot, origin) in sets[i]:
                alt = prods[rule][a]
                if dot < len(alt):
                    s = alt[dot]
                    if s[0] == "t":
                        expected.add(f"'{s[1]}'")
                    elif s[1] in TOKEN_CLASSES:
                        expected.add(s[1])
                    else:
                        expected |= {k if k.isupper() else f"'{k}'" for k in first[s[1]]}
            raise Rejected(tokens[i], expected)
    if not any(rule == start and dot == len(prods[rule][a]) and origin == 0
               for (rule, a, dot, origin) in sets[n]):
        raise Rejected(None, set())


# ---------------------------------------------------------------------------------------------
# The suite
# ---------------------------------------------------------------------------------------------


def header(path: Path) -> list[str]:
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("//!"):
            break
        lines.append(line[3:].strip())
    return lines


def accepted_case_files(cases: Path) -> list[Path]:
    """The programs of the suite a compiler accepts: a case that leads with 'run' or 'check' and
    expects no 'error:' — every source file of it, a package case's included."""
    found = []
    for entry in sorted(cases.rglob("*")):
        if entry.is_file() and entry.suffix == ".lyr" and "src" not in entry.relative_to(cases).parts:
            head = header(entry)
            if head and head[0].split()[0] in ("run", "check") and not any(h.startswith("error:") for h in head):
                found.append(entry)
        elif entry.is_dir() and (entry / "lyric.toml").is_file() and (entry / "src" / "main.lyr").is_file():
            head = header(entry / "src" / "main.lyr")
            if head and head[0].split()[0] in ("run", "check") and not any(h.startswith("error:") for h in head):
                found.extend(sorted(entry.rglob("*.lyr")))
    return found


def check(g: Grammar, path: Path) -> str | None:
    try:
        tokens = Lexer(path.read_text(encoding="utf-8")).tokens()
    except LexError as e:
        return f"{path}:{e}"
    try:
        recognize(g, "Module", tokens)
    except Rejected as r:
        if r.token is None:
            return f"{path}: the file ends inside a declaration"
        exp = ", ".join(sorted(r.expected)[:12])
        return f"{path}:{r.token.line}:{r.token.col}: the grammar takes no {r.token.text!r} here (expected {exp})"
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("paths", nargs="*", type=Path)
    ap.add_argument("--spec", type=Path, default=ROOT / "spec" / "02-grammar.md")
    ap.add_argument("--jobs", type=int, default=os.cpu_count() or 1)
    args = ap.parse_args()

    try:
        g = Grammar(read_rules(ebnf_blocks(args.spec.read_text(encoding="utf-8"))))
    except GrammarError as e:
        print(f"{args.spec}: {e}", file=sys.stderr)
        return 2

    if args.paths:
        files = []
        for p in args.paths:
            files.extend(sorted(p.rglob("*.lyr")) if p.is_dir() else [p])
    else:
        files = accepted_case_files(ROOT / "conformance" / "cases")

    if args.jobs > 1 and len(files) > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(args.jobs, initializer=_init, initargs=(args.spec,)) as pool:
            results = list(pool.map(_check_one, files, chunksize=8))
    else:
        results = [check(g, f) for f in files]

    failures = [r for r in results if r]
    for f in failures:
        print(f)
    print(f"{len(files) - len(failures)}/{len(files)} programs are sentences of the grammar")
    return 1 if failures or not files else 0


_grammar: Grammar | None = None


def _init(spec: Path) -> None:
    global _grammar
    _grammar = Grammar(read_rules(ebnf_blocks(spec.read_text(encoding="utf-8"))))


def _check_one(path: Path) -> str | None:
    assert _grammar is not None
    return check(_grammar, path)


if __name__ == "__main__":
    sys.exit(main())

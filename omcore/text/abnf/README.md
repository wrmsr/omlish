Parser toolbox for ABNF grammars.

Originally based on library by Charles Yeomans (see LICENSE file):

https://github.com/declaresub/abnf/tree/561ced67c0a8afc869ad0de5b39dbe4f6e71b0d8/src/abnf

It has however been entirely rewritten.

## Overview

Grammars are parsed from RFC 5234 (+7405) text by `parse_grammar` into an open `Op`-tree IR (`ops.py`), and executed by
pluggable engines (`engines/`). An `Engine` compiles a `Grammar` into a `CompiledGrammar` - the expensive, cacheable
step - whose `parse` / `iter_parse` do the per-call work. What each engine can do is data
(`EngineCapabilities`), and asking for something outside it raises rather than silently degrading:

- **`InterpEngine`** (the default, behind `Grammar.parse` / `parse`): the true-ABNF reference engine - a memoizing,
  all-matches recursive-descent interpreter. Op trees are closure-compiled per grammar for speed (a readable reference
  implementation remains as the `debug=` path and differential-test oracle). Any rule may be a parse root, partial
  matches are supported, and `iter_parse` yields every possible match.

- **`LrEngine`** (opt-in): a deterministic lexer + LALR(1) table engine for `%token`-annotated grammars. Trades the
  interpreter's nondeterminism for compile-time checking (non-LALR(1) grammars are rejected with per-state conflict
  reports) and much faster, linear-scaling parses. Single root, complete parses only, and *rule-level* match trees
  (parser-rule nodes and named-token leaves - the shape `only_match_rules` gives). `LrCompiledGrammar.lex` exposes the
  full token stream including hidden whitespace/comment tokens, with exact spans.

Optimization (`opto.py`) converts provably-safe subtrees to compiled regexes, gated by a local prefix-freeness proof
by default (span-preserving) or by grammar-wide FIRST/FOLLOW analysis (`analysis.py`) under
`optimize_grammar(parse_only=True)` (preserves `parse()` results only).

## Meta-grammar extensions

All extensions are opt-in supersets: unannotated RFC 5234 grammars parse and run unchanged (and the meta-grammar
accepts bare LF line endings).

- **`|` alternation**: first-match ('committed choice') alternation alongside `/`'s all-matches semantics. The two may
  not be mixed in one un-parenthesized alternation.

- **`%token` rule modifier**: marks a rule as a lexical token for token-mode engines. Token rules must be
  non-recursive and non-nullable; rules they reference are inlined as fragments. Literals appearing in parser rules
  become implicit tokens automatically (ANTLR-style), outranking named tokens on ties - keywords beat identifiers.

- **`%channel(...)` rule modifier**: assigns the rule's `Channel` from grammar text. Tokens channeled `space` or
  `comment` are *hidden*: lexed and retained in the token stream but not fed to the parser - this is how whitespace
  and hot comments are picked up.

Conventional `SKIP = WS / comment` / `S = *SKIP` / `R = 1*SKIP` whitespace threading is recognized structurally: the
interpreter honors it literally, character by character, while token-mode engines elide it (`S`) or enforce it as a
token-boundary gap assertion (`R`) - one grammar text, both engines, aligned semantics. An adjacency check rejects
grammars whose char-level and token-level readings would diverge. See `tests/minisql.abnf` for a full worked example,
and the differential suite in `tests/test_minisql.py` for the agreement contract (including the one inherent
divergence: char-level identifier rules match reserved words, maximal-munch lexing reserves them).

## Mini-reference

| Feature                   | EBNF           | ABNF             |
| ------------------------- | -------------- | ---------------- |
| Rule terminator           | `;`            | none             |
| Alternation               | `|`            | `/`              |
| Optional                  | `[a]` or `a?`  | `[a]`            |
| Zero or more              | `a*`           | `*a`             |
| One or more               | `a+`           | `1*a`            |
| Bounded repetition        | `1..5 a`       | `1*5a`           |
| Character ranges          | sometimes:     | `%xNN-NN`        |
|                           | `"0" .. "9"`   |                  |
| Literal chars             | `'a'` or `"a"` | `"a"` only       |
| Case-insensitive literals | no             | `%i"..."`        |
| Comments                  | `(* *)` or     | `;`              |
|                           | `/* */` or     |                  |
|                           | `-- `          |                  |
| Rule names                | case-sensitive | case-insensitive |

(This package extends ABNF with `|` for committed choice - see above.)

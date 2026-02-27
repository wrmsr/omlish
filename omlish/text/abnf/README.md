Parser generator for ABNF grammars.

Originally based on library by Charles Yeomans (see LICENSE file):

https://github.com/declaresub/abnf/tree/561ced67c0a8afc869ad0de5b39dbe4f6e71b0d8/src/abnf

It has however been entirely rewritten.

Not quite ready for production use, but ready enough for initial use.

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

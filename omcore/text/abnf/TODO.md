TODO:
- codegen / AOT: serialize parsed Grammars (op trees) and LR tables to build artifacts keyed by source hash, with
  runtime fallback to live construction - the dataclass-codegen analogue. Kills the meta-parse import cost.
- lazy memoization in the interp engine, unlocking an endpos-enumerating Regex fallback so *every* regexable subtree
  converts (analysis-provable ones stay single-greedy-match, the rest enumerate ends lazily)
- rule specialization (duplicate rules per follow-class) to sharpen the FOLLOW analysis - json's `ws` is the motivating
  precision gap
- multiple compiled roots per LrCompiledGrammar; `%root` modifier?
- GLR driver over the same LALR tables, if ever needed (all-parses with AOT tables)
- token-mode CI keyword caveat: exotic Unicode case-foldings of a keyword's first char aren't seen by the lexer's
  first-char dispatch ('K' Kelvin-sign etc); document or close
- relax CRLF core rule for *user* grammars by default? (meta-grammar already accepts LF)
- grammar transform? helper kwarg?
- ebnf mode?

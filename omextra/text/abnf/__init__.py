"""
Parser generator for ABNF grammars.

Originally based on library by Charles Yeomans (see LICENSE file):

  https://github.com/declaresub/abnf/tree/561ced67c0a8afc869ad0de5b39dbe4f6e71b0d8/src/abnf

It has however been nearly entirely rewritten.

====

TODO:
 - cache lol
 - get greedier
 - match-powered optimizer
  - greedily compile regexes
 - error reporting
 - codegen
"""


from .base import (  # noqa
    Match,
    longest_match,

    Parser,

    Rule,
    Grammar,

    iter_parse,
    parse,
)

from .core import (  # noqa
    CORE_RULES,
)

from .errors import (  # noqa
    AbnfError,
    AbnfGrammarParseError,
)

from .meta import (  # noqa
    META_GRAMMAR_RULES,
    META_GRAMMAR,

    parse_grammar,
)

from .parsers import (  # noqa
    Literal,
    StringLiteral,
    CaseInsensitiveStringLiteral,
    RangeLiteral,
    literal,

    Concat,
    concat,

    Repeat,
    Option,
    repeat,

    Either,
    either,

    RuleRef,
    rule,
)

from .utils import (  # noqa
    strip_insignificant_match_rules,
    only_match_rules,

    parse_rules,

    fix_grammar_ws,
)

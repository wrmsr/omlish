"""
Parser generator for ABNF grammars.

Originally based on library by Charles Yeomans (see LICENSE file):

  https://github.com/declaresub/abnf/tree/561ced67c0a8afc869ad0de5b39dbe4f6e71b0d8/src/abnf

It has however been entirely rewritten.

====

TODO:
 - opto
 - error reporting
 - codegen?
 - fix_ws problem
  - auto? no, need to keep lines / offsets accurate for errors
  - relax CRLF rule by default?
  - grammar transform? helper kwarg?
 - kwarg to mark uppercase rules insignificant
"""
from omlish import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from .base import (  # noqa
    Op,
)

from .core import (  # noqa
    CORE_RULES,
)

from .errors import (  # noqa
    AbnfError,
    AbnfGrammarParseError,
)

from .grammars import (  # noqa
    Channel,
    Rule,
    RulesCollection,

    Grammar,
)

from .matches import (  # noqa
    Match,

    longest_match,
    filter_matches,
)

from .meta import (  # noqa
    META_GRAMMAR_RULES,
    META_GRAMMAR,

    parse_grammar,
)

from .ops import (  # noqa
    Literal,
    StringLiteral,
    CaseInsensitiveStringLiteral,
    RangeLiteral,
    literal,

    Concat,
    concat,

    Repeat,
    repeat,
    option,

    Either,
    either,

    RuleRef,
    rule,
)

from .parsing import (  # noqa
    iter_parse,
    parse,
)

from .utils import (  # noqa
    only_match_rules,

    parse_rules,

    fix_ws,
)

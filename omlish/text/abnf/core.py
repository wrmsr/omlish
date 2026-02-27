"""
https://datatracker.ietf.org/doc/html/rfc5234
"""
import typing as ta

from .grammars import Channel
from .grammars import Grammar
from .grammars import Rule
from .ops import concat
from .ops import either
from .ops import literal
from .ops import repeat
from .ops import rule
from .opto import optimize_grammar


##


CORE_RULES: ta.Sequence[Rule] = [

    Rule(
        'ALPHA',
        either(
            literal('\x41', '\x5a'),
            literal('\x61', '\x7a'),
        ),
        channel=Channel.CONTENT,
    ),

    Rule(
        'BIT',
        either(
            literal('0'),
            literal('1'),
        ),
        channel=Channel.CONTENT,
    ),

    Rule(
        'CHAR',
        literal('\x01', '\x7f'),
        channel=Channel.CONTENT,
    ),

    Rule(
        'CTL',
        either(
            literal('\x00', '\x1f'),
            literal('\x7f', case_sensitive=True),
        ),
        channel=Channel.CONTENT,
    ),

    Rule(
        'CR',
        literal('\x0d', case_sensitive=True),
        channel=Channel.SPACE,
    ),

    Rule(
        'CRLF',
        concat(
            rule('CR'),
            rule('LF'),
        ),
        channel=Channel.SPACE,
    ),

    Rule(
        'DIGIT',
        literal('\x30', '\x39'),
        channel=Channel.CONTENT,
    ),

    Rule(
        'DQUOTE',
        literal('\x22', case_sensitive=True),
        channel=Channel.CONTENT,
    ),

    Rule(
        'HEXDIG',
        either(
            rule('DIGIT'),
            literal('A'),
            literal('B'),
            literal('C'),
            literal('D'),
            literal('E'),
            literal('F'),
        ),
        channel=Channel.CONTENT,
    ),

    Rule(
        'HTAB',
        literal('\x09', case_sensitive=True),
        channel=Channel.SPACE,
    ),

    Rule(
        'LF',
        literal('\x0a', case_sensitive=True),
        channel=Channel.SPACE,
    ),

    Rule(
        'LWSP',
        repeat(
            either(
                rule('WSP'),
                concat(
                    rule('CRLF'),
                    rule('WSP'),
                ),
            ),
        ),
        channel=Channel.SPACE,
    ),

    Rule(
        'OCTET',
        literal('\x00', '\xff'),
        channel=Channel.CONTENT,
    ),

    Rule(
        'SP',
        literal('\x20', case_sensitive=True),
        channel=Channel.SPACE,
    ),

    Rule(
        'VCHAR',
        literal('\x21', '\x7e'),
        channel=Channel.CONTENT,
    ),

    Rule(
        'WSP',
        either(
            rule('SP'),
            rule('HTAB'),
        ),
        channel=Channel.SPACE,
    ),

]


RAW_CORE_GRAMMAR = Grammar(*CORE_RULES)
CORE_GRAMMAR = optimize_grammar(RAW_CORE_GRAMMAR)

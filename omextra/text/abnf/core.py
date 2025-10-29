"""
https://datatracker.ietf.org/doc/html/rfc5234
"""
import typing as ta

from .base import Grammar
from .base import Rule
from .parsers import concat
from .parsers import either
from .parsers import literal
from .parsers import repeat
from .parsers import rule


##


CORE_RULES: ta.Sequence[Rule] = [

    Rule(
        'ALPHA',
        either(
            literal('\x41', '\x5a'),
            literal('\x61', '\x7a'),
        ),
    ),

    Rule(
        'BIT',
        either(
            literal('0'),
            literal('1'),
        ),
    ),

    Rule(
        'CHAR',
        literal('\x01', '\x7f'),
    ),

    Rule(
        'CTL',
        either(
            literal('\x00', '\x1f'),
            literal('\x7f', case_sensitive=True),
        ),
    ),

    Rule(
        'CR',
        literal('\x0d', case_sensitive=True),
        insignificant=True,
    ),

    Rule(
        'CRLF',
        concat(
            rule('CR'),
            rule('LF'),
        ),
        insignificant=True,
    ),

    Rule(
        'DIGIT',
        literal('\x30', '\x39'),
    ),

    Rule(
        'DQUOTE',
        literal('\x22', case_sensitive=True),
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
    ),

    Rule(
        'HTAB',
        literal('\x09', case_sensitive=True),
        insignificant=True,
    ),

    Rule(
        'LF',
        literal('\x0a', case_sensitive=True),
        insignificant=True,
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
        insignificant=True,
    ),

    Rule(
        'OCTET',
        literal('\x00', '\xff'),
    ),

    Rule(
        'SP',
        literal('\x20', case_sensitive=True),
        insignificant=True,
    ),

    Rule(
        'VCHAR',
        literal('\x21', '\x7e'),
    ),

    Rule(
        'WSP',
        either(
            rule('SP'),
            rule('HTAB'),
        ),
        insignificant=True,
    ),

]


CORE_GRAMMAR = Grammar(*CORE_RULES)

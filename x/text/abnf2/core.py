import typing as ta

from .base import Parser
from .base import alternate
from .base import concat
from .base import literal
from .base import repeat
from .base import rule


##


BOOTSTRAP_RULES: ta.Mapping[str, Parser] = {

    'ALPHA': alternate(
        literal('\x41', '\x5a'),
        literal('\x61', '\x7a'),
    ),

    'BIT': alternate(
        literal('0'),
        literal('1'),
    ),

    'CHAR': literal('\x01', '\x7f'),

    'CTL': alternate(
        literal('\x00', '\x1f'),
        literal('\x7f', case_sensitive=True),
    ),

    'CR': literal('\x0d', case_sensitive=True),

    'CRLF': concat(
        rule('CR'),
        rule('LF'),
    ),

    'DIGIT': literal('\x30', '\x39'),

    'DQUOTE': literal('\x22', case_sensitive=True),

    'HEXDIG': alternate(
        rule('DIGIT'),
        literal('A'),
        literal('B'),
        literal('C'),
        literal('D'),
        literal('E'),
        literal('F'),
    ),

    'HTAB': literal('\x09', case_sensitive=True),

    'LF': literal('\x0a', case_sensitive=True),

    'LWSP': repeat(
        alternate(
            rule('WSP'),
            concat(
                rule('CRLF'),
                rule('WSP'),
            ),
        ),
    ),

    'OCTET': literal('\x00', '\xff'),

    'SP': literal('\x20', case_sensitive=True),

    'VCHAR': literal('\x21', '\x7e'),

    'WSP': alternate(
        rule('SP'),
        rule('HTAB'),
    ),

}

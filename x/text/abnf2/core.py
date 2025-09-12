import typing as ta

from .base import Parser
from .base import alternate
from .base import concat
from .base import literal
from .base import repeat
from .base import rule
from .base import option


##


CORE_RULES: ta.Mapping[str, Parser] = {

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


GRAMMAR_RULES: ta.Mapping[str, Parser] = {

    'rulelist': repeat(
        1,
        alternate(
            rule('rule'),
            concat(
                repeat(
                    rule('c-wsp'),
                ),
                rule('c-nl'),
            ),
        ),
    ),

    'rule': concat(
        rule('rulename'),
        rule('defined-as'),
        rule('elements'),
        rule('c-nl'),
    ),

    'rulename': concat(
        rule('ALPHA'),
        repeat(
            alternate(
                rule('ALPHA'),
                rule('DIGIT'),
                literal('-'),
            ),
        ),
    ),

    'defined-as': concat(
        repeat(
            rule('c-wsp'),
        ),
        alternate(
            literal('=/'),
            literal('='),
        ),
        repeat(
            rule('c-wsp'),
        ),
    ),

    'elements': concat(
        rule('alternation'),
        repeat(
            rule('c-wsp'),
        ),
    ),

    'c-wsp': alternate(
        rule('WSP'),
        concat(
            rule('c-nl'),
            rule('WSP'),
        ),
    ),

    'c-nl': alternate(
        rule('comment'),
        rule('CRLF'),
    ),

    'comment': concat(
        literal(';'),
        repeat(
            alternate(
                rule('WSP'),
                rule('VCHAR'),
            )),
        rule('CRLF'),
    ),

    'alternation': concat(
        rule('concatenation'),
        repeat(
            concat(
                repeat(
                    rule('c-wsp'),
                ),
                literal('/'),
                repeat(
                    rule('c-wsp'),
                ),
                rule('concatenation'),
            ),
        ),
    ),

    'concatenation': concat(
        rule('repetition'),
        repeat(
            concat(
                repeat(
                    1,
                    rule('c-wsp'),
                ),
                rule('repetition'),
            ),
        ),
    ),

    'repetition': concat(
        option(
            rule('repeat'),
        ),
        rule('element'),
    ),

    'repeat': alternate(
        concat(
            repeat(
                rule('DIGIT'),
            ),
            literal('*'),
            repeat(
                rule('DIGIT'),
            ),
        ),
        repeat(
            1,
            rule('DIGIT'),
        ),
    ),

    'element': alternate(
        rule('rulename'),
        rule('group'),
        rule('option'),
        rule('char-val'),
        rule('num-val'),
        rule('prose-val'),
    ),

    'group': concat(
        literal('('),
        repeat(
            rule('c-wsp'),
        ),
        rule('alternation'),
        repeat(
            rule('c-wsp'),
        ),
        literal(')'),
    ),

    'option': concat(
        literal('['),
        repeat(
            rule('c-wsp'),
        ),
        rule('alternation'),
        repeat(
            rule('c-wsp'),
        ),
        literal(']'),
    ),

    'num-val': concat(
        literal('%'),
        alternate(
            rule('bin-val'),
            rule('dec-val'),
            rule('hex-val'),
        ),
    ),

    'bin-val': concat(
        literal('b'),
        concat(
            repeat(
                1,
                rule('BIT'),
            ),
            option(
                alternate(
                    repeat(
                        1,
                        concat(
                            literal('.'),
                            repeat(
                                1,
                                rule('BIT'),
                            ),
                        ),
                    ),
                    concat(
                        literal('-'),
                        repeat(
                            1,
                            rule('BIT'),
                        ),
                    ),
                ),
            ),
        ),
    ),

    'dec-val': concat(
        literal('d'),
        concat(
            repeat(
                1,
                rule('DIGIT'),
            ),
            option(
                alternate(
                    repeat(
                        1,
                        concat(
                            literal('.'),
                            repeat(
                                1,
                                rule('DIGIT'),
                            ),
                        ),
                    ),
                    concat(
                        literal('-'),
                        repeat(
                            1,
                            rule('DIGIT'),
                        ),
                    ),
                ),
            ),
        ),
    ),

    'hex-val': concat(
        literal('x'),
        concat(
            repeat(
                1,
                rule('HEXDIG'),
            ),
            option(
                alternate(
                    repeat(
                        1,
                        concat(
                            literal('.'),
                            repeat(
                                1,
                                rule('HEXDIG'),
                            ),
                        ),
                    ),
                    concat(
                        literal('-'),
                        repeat(
                            1,
                            rule('HEXDIG'),
                        ),
                    ),
                ),
            ),
        ),
    ),

    'prose-val': concat(
        literal('<'),
        repeat(
            alternate(
                literal('\x20', '\x3d'),
                literal('\x3f', '\x7e'),
            ),
        ),
        literal('>'),
    ),

    # definitions from RFC 7405
    'char-val': alternate(
        rule('case-insensitive-string'),
        rule('case-sensitive-string'),
    ),

    'case-insensitive-string': concat(
        option(
            literal('%i'),
        ),
        rule('quoted-string'),
    ),

    'case-sensitive-string': concat(
        literal('%s'),
        rule('quoted-string'),
    ),

    'quoted-string': concat(
        rule('DQUOTE'),
        repeat(
            alternate(
                literal('\x20', '\x21'),
                literal('\x23', '\x7e'),
            ),
        ),
        rule('DQUOTE'),
    ),

}

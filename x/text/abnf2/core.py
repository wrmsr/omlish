"""
https://datatracker.ietf.org/doc/html/rfc5234
"""
import typing as ta

from .base import Grammar
from .base import Rule
from .parsers import concat
from .parsers import either
from .parsers import literal
from .parsers import option
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


##


GRAMMAR_RULES: ta.Sequence[Rule] = [

    Rule(
        'rulelist',
        repeat(
            1,
            either(
                rule('rule'),
                concat(
                    repeat(
                        rule('c-wsp'),
                    ),
                    rule('c-nl'),
                ),
            ),
        ),
    ),

    Rule(
        'rule',
        concat(
            rule('rulename'),
            rule('defined-as'),
            rule('elements'),
            rule('c-nl'),
        ),
    ),

    Rule(
        'rulename',
        concat(
            rule('ALPHA'),
            repeat(
                either(
                    rule('ALPHA'),
                    rule('DIGIT'),
                    literal('-'),
                ),
            ),
        ),
    ),

    Rule(
        'defined-as',
        concat(
            repeat(
                rule('c-wsp'),
            ),
            either(
                literal('=/'),
                literal('='),
            ),
            repeat(
                rule('c-wsp'),
            ),
        ),
    ),

    Rule(
        'elements',
        concat(
            rule('alternation'),
            repeat(
                rule('c-wsp'),
            ),
        ),
    ),

    Rule(
        'c-wsp',
        either(
            rule('WSP'),
            concat(
                rule('c-nl'),
                rule('WSP'),
            ),
        ),
        insignificant=True,
    ),

    Rule(
        'c-nl',
        either(
            rule('comment'),
            rule('CRLF'),
        ),
        insignificant=True,
    ),

    Rule(
        'comment',
        concat(
            literal(';'),
            repeat(
                either(
                    rule('WSP'),
                    rule('VCHAR'),
                )),
            rule('CRLF'),
        ),
    ),

    Rule(
        'alternation',
        concat(
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
    ),

    Rule(
        'concatenation',
        concat(
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
    ),

    Rule(
        'repetition',
        concat(
            option(
                rule('repeat'),
            ),
            rule('element'),
        ),
    ),

    Rule(
        'repeat',
        either(
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
    ),

    Rule(
        'element',
        either(
            rule('rulename'),
            rule('group'),
            rule('option'),
            rule('char-val'),
            rule('num-val'),
            rule('prose-val'),
        ),
    ),

    Rule(
        'group',
        concat(
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
    ),

    Rule(
        'option',
        concat(
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
    ),

    Rule(
        'num-val',
        concat(
            literal('%'),
            either(
                rule('bin-val'),
                rule('dec-val'),
                rule('hex-val'),
            ),
        ),
    ),

    Rule(
        'bin-val',
        concat(
            literal('b'),
            concat(
                repeat(
                    1,
                    rule('BIT'),
                ),
                option(
                    either(
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
    ),

    Rule(
        'dec-val',
        concat(
            literal('d'),
            concat(
                repeat(
                    1,
                    rule('DIGIT'),
                ),
                option(
                    either(
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
    ),

    Rule(
        'hex-val',
        concat(
            literal('x'),
            concat(
                repeat(
                    1,
                    rule('HEXDIG'),
                ),
                option(
                    either(
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
    ),

    Rule(
        'prose-val',
        concat(
            literal('<'),
            repeat(
                either(
                    literal('\x20', '\x3d'),
                    literal('\x3f', '\x7e'),
                ),
            ),
            literal('>'),
        ),
    ),

    # definitions from RFC 7405
    Rule(
        'char-val',
        either(
            rule('case-insensitive-string'),
            rule('case-sensitive-string'),
        ),
    ),

    Rule(
        'case-insensitive-string',
        concat(
            option(
                literal('%i'),
            ),
            rule('quoted-string'),
        ),
    ),

    Rule(
        'case-sensitive-string',
        concat(
            literal('%s'),
            rule('quoted-string'),
        ),
    ),

    Rule(
        'quoted-string',
        concat(
            rule('DQUOTE'),
            repeat(
                either(
                    literal('\x20', '\x21'),
                    literal('\x23', '\x7e'),
                ),
            ),
            rule('DQUOTE'),
        ),
    ),

]


##


GRAMMAR_GRAMMAR = Grammar(
    *CORE_RULES,
    *GRAMMAR_RULES,
    root='rulelist',
)


def fix_grammar_ws(s: str) -> str:
    return s.rstrip().replace('\r', '').replace('\n', '\r\n') + '\r\n'

"""
https://datatracker.ietf.org/doc/html/rfc5234
"""
import typing as ta

from .base import Grammar
from .base import Rule
from .core import CORE_RULES
from .parsers import concat
from .parsers import either
from .parsers import literal
from .parsers import option
from .parsers import repeat
from .parsers import rule


##


META_GRAMMAR_RULES: ta.Sequence[Rule] = [

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


META_GRAMMAR = Grammar(
    *CORE_RULES,
    *META_GRAMMAR_RULES,
    root='rulelist',
)

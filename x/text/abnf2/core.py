import typing as ta

from .base import Parser
from .base import alternate
from .base import concat
from .base import literal
from .base import repeat
from .base import rule


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

    ('rulelist', Repetition(
        Repeat(1),
        Alternation(
            rule('rule'),
            Concatenation(
                Repetition(
                    Repeat(),
                    rule('c-wsp'),
                ),
                rule('c-nl'),
            ),
        ),
    )),

    ('rule', Concatenation(
        rule('rulename'),
        rule('defined-as'),
        rule('elements'),
        rule('c-nl'),
    )),

    ('rulename', Concatenation(
        Rule('ALPHA'),
        Repetition(
            Repeat(),
            Alternation(
                Rule('ALPHA'),
                Rule('DIGIT'),
                Literal('-'),
            ),
        ),
    )),

    ('defined-as', Concatenation(
        Repetition(
            Repeat(),
            rule('c-wsp'),
        ),
        Alternation(
            Literal('=/'),
            Literal('='),
        ),
        Repetition(
            Repeat(),
            rule('c-wsp'),
        ),
    )),

    ('elements', Concatenation(
        rule('alternation'),
        Repetition(
            Repeat(),
            rule('c-wsp'),
        ),
    )),

    ('c-wsp', Alternation(
        Rule('WSP'),
        Concatenation(
            rule('c-nl'),
            Rule('WSP'),
        ),
    )),

    ('c-nl', Alternation(
        rule('comment'),
        Rule('CRLF'),
    )),

    ('comment', Concatenation(
        Literal(';'),
        Repetition(
            Repeat(),
            Alternation(
                Rule('WSP'),
                Rule('VCHAR'),
            )),
        Rule('CRLF'),
    )),

    ('alternation', Concatenation(
        rule('concatenation'),
        Repetition(
            Repeat(),
            Concatenation(
                Repetition(
                    Repeat(),
                    rule('c-wsp'),
                ),
                Literal('/'),
                Repetition(
                    Repeat(),
                    rule('c-wsp'),
                ),
                rule('concatenation'),
            ),
        ),
    )),

    ('concatenation', Concatenation(
        rule('repetition'),
        Repetition(
            Repeat(),
            Concatenation(
                Repetition(
                    Repeat(1),
                    rule('c-wsp'),
                ),
                rule('repetition'),
            ),
        ),
    )),

    ('repetition', Concatenation(
        Option(
            rule('repeat'),
        ),
        rule('element'),
    )),

    ('repeat', Alternation(
        Concatenation(
            Repetition(
                Repeat(0, None),
                Rule('DIGIT'),
            ),
            Literal('*'),
            Repetition(
                Repeat(0, None),
                Rule('DIGIT'),
            ),
        ),
        Repetition(
            Repeat(1, None),
            Rule('DIGIT'),
        ),
    )),

    ('element', Alternation(
        rule('rulename'),
        rule('group'),
        rule('option'),
        rule('char-val'),
        rule('num-val'),
        rule('prose-val'),
    )),

    ('group', Concatenation(
        Literal('('),
        Repetition(
            Repeat(),
            rule('c-wsp'),
        ),
        rule('alternation'),
        Repetition(
            Repeat(),
            rule('c-wsp'),
        ),
        Literal(')'),
    )),

    ('option', Concatenation(
        Literal('['),
        Repetition(
            Repeat(),
            rule('c-wsp'),
        ),
        rule('alternation'),
        Repetition(
            Repeat(),
            rule('c-wsp'),
        ),
        Literal(']'),
    )),

    ('num-val', Concatenation(
        Literal('%'),
        Alternation(
            rule('bin-val'),
            rule('dec-val'),
            rule('hex-val'),
        ),
    )),

    ('bin-val', Concatenation(
        Literal('b'),
        Concatenation(
            Repetition(
                Repeat(1),
                Rule('BIT'),
            ),
            Option(
                Alternation(
                    Repetition(
                        Repeat(1),
                        Concatenation(
                            Literal('.'),
                            Repetition(
                                Repeat(1),
                                Rule('BIT'),
                            ),
                        ),
                    ),
                    Concatenation(
                        Literal('-'),
                        Repetition(
                            Repeat(1),
                            Rule('BIT'),
                        ),
                    ),
                ),
            ),
        ),
    )),

    ('dec-val', Concatenation(
        Literal('d'),
        Concatenation(
            Repetition(
                Repeat(1),
                Rule('DIGIT'),
            ),
            Option(
                Alternation(
                    Repetition(
                        Repeat(1),
                        Concatenation(
                            Literal('.'),
                            Repetition(
                                Repeat(1),
                                Rule('DIGIT'),
                            ),
                        ),
                    ),
                    Concatenation(
                        Literal('-'),
                        Repetition(
                            Repeat(1),
                            Rule('DIGIT'),
                        ),
                    ),
                ),
            ),
        ),
    )),

    ('hex-val', Concatenation(
        Literal('x'),
        Concatenation(
            Repetition(
                Repeat(1),
                Rule('HEXDIG'),
            ),
            Option(
                Alternation(
                    Repetition(
                        Repeat(1),
                        Concatenation(
                            Literal('.'),
                            Repetition(
                                Repeat(1),
                                Rule('HEXDIG'),
                            ),
                        ),
                    ),
                    Concatenation(
                        Literal('-'),
                        Repetition(
                            Repeat(1),
                            Rule('HEXDIG'),
                        ),
                    ),
                ),
            ),
        ),
    )),

    ('prose-val', Concatenation(
        Literal('<'),
        Repetition(
            Repeat(),
            Alternation(
                Literal(('\x20', '\x3d')),
                Literal(('\x3f', '\x7e')),
            ),
        ),
        Literal('>'),
    )),

    # definitions from RFC 7405
    ('char-val', Alternation(
        rule('case-insensitive-string'),
        rule('case-sensitive-string'),
    )),

    ('case-insensitive-string', Concatenation(
        Option(
            Literal('%i'),
        ),
        rule('quoted-string'),
    )),

    ('case-sensitive-string', Concatenation(
        Literal('%s'),
        rule('quoted-string'),
    )),

    ('quoted-string', Concatenation(
        Rule('DQUOTE'),
        Repetition(
            Repeat(),
            Alternation(
                Literal(('\x20', '\x21')),
                Literal(('\x23', '\x7e')),
            ),
        ),
        Rule('DQUOTE'),
    )),

}

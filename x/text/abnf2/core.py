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
            GrammarRule('rule'),
            Concatenation(
                Repetition(
                    Repeat(),
                    GrammarRule('c-wsp'),
                ),
                GrammarRule('c-nl'),
            ),
        ),
    )),

    ('rule', Concatenation(
        GrammarRule('rulename'),
        GrammarRule('defined-as'),
        GrammarRule('elements'),
        GrammarRule('c-nl'),
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
            GrammarRule('c-wsp'),
        ),
        Alternation(
            Literal('=/'),
            Literal('='),
        ),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
    )),

    ('elements', Concatenation(
        GrammarRule('alternation'),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
    )),

    ('c-wsp', Alternation(
        Rule('WSP'),
        Concatenation(
            GrammarRule('c-nl'),
            Rule('WSP'),
        ),
    )),

    ('c-nl', Alternation(
        GrammarRule('comment'),
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
        GrammarRule('concatenation'),
        Repetition(
            Repeat(),
            Concatenation(
                Repetition(
                    Repeat(),
                    GrammarRule('c-wsp'),
                ),
                Literal('/'),
                Repetition(
                    Repeat(),
                    GrammarRule('c-wsp'),
                ),
                GrammarRule('concatenation'),
            ),
        ),
    )),

    ('concatenation', Concatenation(
        GrammarRule('repetition'),
        Repetition(
            Repeat(),
            Concatenation(
                Repetition(
                    Repeat(1),
                    GrammarRule('c-wsp'),
                ),
                GrammarRule('repetition'),
            ),
        ),
    )),

    ('repetition', Concatenation(
        Option(
            GrammarRule('repeat'),
        ),
        GrammarRule('element'),
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
        GrammarRule('rulename'),
        GrammarRule('group'),
        GrammarRule('option'),
        GrammarRule('char-val'),
        GrammarRule('num-val'),
        GrammarRule('prose-val'),
    )),

    ('group', Concatenation(
        Literal('('),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
        GrammarRule('alternation'),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
        Literal(')'),
    )),

    ('option', Concatenation(
        Literal('['),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
        GrammarRule('alternation'),
        Repetition(
            Repeat(),
            GrammarRule('c-wsp'),
        ),
        Literal(']'),
    )),

    ('num-val', Concatenation(
        Literal('%'),
        Alternation(
            GrammarRule('bin-val'),
            GrammarRule('dec-val'),
            GrammarRule('hex-val'),
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
        GrammarRule('case-insensitive-string'),
        GrammarRule('case-sensitive-string'),
    )),

    ('case-insensitive-string', Concatenation(
        Option(
            Literal('%i'),
        ),
        GrammarRule('quoted-string'),
    )),

    ('case-sensitive-string', Concatenation(
        Literal('%s'),
        GrammarRule('quoted-string'),
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

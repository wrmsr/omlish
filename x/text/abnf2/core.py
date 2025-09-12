import typing as ta

from .base import Parser
from .base import either
from .base import concat
from .base import literal
from .base import repeat
from .base import rule
from .base import option
from .base import Grammar


##


CORE_RULES: ta.Mapping[str, Parser] = {

    'ALPHA': either(
        literal('\x41', '\x5a'),
        literal('\x61', '\x7a'),
    ),

    'BIT': either(
        literal('0'),
        literal('1'),
    ),

    'CHAR': literal('\x01', '\x7f'),

    'CTL': either(
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

    'HEXDIG': either(
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
        either(
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

    'WSP': either(
        rule('SP'),
        rule('HTAB'),
    ),

}


GRAMMAR_RULES: ta.Mapping[str, Parser] = {

    'rulelist': repeat(
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

    'rule': concat(
        rule('rulename'),
        rule('defined-as'),
        rule('elements'),
        rule('c-nl'),
    ),

    'rulename': concat(
        rule('ALPHA'),
        repeat(
            either(
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
        either(
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

    'c-wsp': either(
        rule('WSP'),
        concat(
            rule('c-nl'),
            rule('WSP'),
        ),
    ),

    'c-nl': either(
        rule('comment'),
        rule('CRLF'),
    ),

    'comment': concat(
        literal(';'),
        repeat(
            either(
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

    'repeat': either(
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

    'element': either(
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
        either(
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

    'dec-val': concat(
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

    'hex-val': concat(
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

    'prose-val': concat(
        literal('<'),
        repeat(
            either(
                literal('\x20', '\x3d'),
                literal('\x3f', '\x7e'),
            ),
        ),
        literal('>'),
    ),

    # definitions from RFC 7405
    'char-val': either(
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
            either(
                literal('\x20', '\x21'),
                literal('\x23', '\x7e'),
            ),
        ),
        rule('DQUOTE'),
    ),

}


GRAMMAR_GRAMMAR = Grammar(
    CORE_RULES,
    GRAMMAR_RULES,
    root='rulelist',
)


##


def _main() -> None:
    # # rfc_2616
    # source = r"""
    #     HTTP-date    = rfc1123-date / rfc850-date / asctime-date
    #     rfc1123-date = wkday "," SP date1 SP time SP "GMT"
    #     rfc850-date  = weekday "," SP date2 SP time SP "GMT"
    #     asctime-date = wkday SP date3 SP time SP 4DIGIT
    #     date1        = 2DIGIT SP month SP 4DIGIT
    #                     ; day month year (e.g., 02 Jun 1982)
    #     date2        = 2DIGIT "-" month "-" 2DIGIT
    #                     ; day-month-year (e.g., 02-Jun-82)
    #     date3        = month SP ( 2DIGIT / ( SP 1DIGIT ))
    #                     ; month day (e.g., Jun  2)
    #     time         = 2DIGIT ":" 2DIGIT ":" 2DIGIT
    #                     ; 00:00:00 - 23:59:59
    #     wkday        = "Mon" / "Tue" / "Wed"
    #                 / "Thu" / "Fri" / "Sat" / "Sun"
    #     weekday      = "Monday" / "Tuesday" / "Wednesday"
    #                 / "Thursday" / "Friday" / "Saturday" / "Sunday"
    #     month        = "Jan" / "Feb" / "Mar" / "Apr"
    #                 / "May" / "Jun" / "Jul" / "Aug"
    #                 / "Sep" / "Oct" / "Nov" / "Dec"
    #
    #     token = 1*( %x21 / %x23-27 / %x2A-2B / %x2D-2E / %x30-39 / %x41-5A / %x5E-7A / %x7C )
    # """

    source = 'a = SP'

    print(GRAMMAR_GRAMMAR.parse('abc123 = defg\r\n', 'rule'))

    # g = Grammar(
    #     CORE_RULES,
    #     {'root': concat(
    #         repeat(rule('WSP')),
    #         repeat(1, literal('a', 'z')),
    #         repeat(rule('WSP')),
    #         literal('='),
    #         repeat(rule('WSP')),
    #         literal('"'),
    #         repeat(
    #             either(
    #                 literal('a', 'z'),
    #                 literal(' '),
    #             ),
    #         ),
    #         literal('"'),
    #     )},
    #     root='root',
    # )
    # for s in [
    #     'x = "y"',
    #     'x=  "y"',
    #     'xy= "az"',
    # ]:
    #     m = g.parse(s)
    #     print(m)


if __name__ == '__main__':
    _main()

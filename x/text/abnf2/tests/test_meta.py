from ..meta import parse_grammar
from ..utils import only_match_rules
from ..utils import strip_insignificant_match_rules


def test_meta() -> None:
    # # rfc_2616
    source = r"""
        HTTP-date    = rfc1123-date / rfc850-date / asctime-date
        rfc1123-date = wkday "," SP date1 SP time SP "GMT"
        rfc850-date  = weekday "," SP date2 SP time SP "GMT"
        asctime-date = wkday SP date3 SP time SP 4DIGIT
        date1        = 2DIGIT SP month SP 4DIGIT          ; day month year (e.g., 02 Jun 1982)
        date2        = 2DIGIT "-" month "-" 2DIGIT        ; day-month-year (e.g., 02-Jun-82)
        date3        = month SP ( 2DIGIT / ( SP 1DIGIT )) ; month day (e.g., Jun  2)
        time         = 2DIGIT ":" 2DIGIT ":" 2DIGIT       ; 00:00:00 - 23:59:59
        wkday        = "Mon" / "Tue" / "Wed" / "Thu" / "Fri" / "Sat" / "Sun"
        weekday      = "Monday" / "Tuesday" / "Wednesday" / "Thursday" / "Friday" / "Saturday" / "Sunday"
        month        = "Jan" / "Feb" / "Mar" / "Apr" / "May" / "Jun" / "Jul" / "Aug" / "Sep" / "Oct" / "Nov" / "Dec"

        token        = 1*( %x21 / %x23-27 / %x2A-2B / %x2D-2E / %x30-39 / %x41-5A / %x5E-7A / %x7C )
    """

    rfc_gram = parse_grammar(source)

    rfc_m = rfc_gram.parse('Mon, 02 Jun 1982 00:00:00 GMT', 'HTTP-date')
    rfc_m = only_match_rules(rfc_m)
    rfc_m = strip_insignificant_match_rules(rfc_m, rfc_gram)
    print(rfc_m.render(indent=2))

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

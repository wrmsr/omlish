import dataclasses as dc
import itertools

from ..message import Message
from ..parsing import parse_line
from ..parsing import parse_line_strict
from ..rendering import render_line
from ..rendering import render_line_strict


##


def make_message(
        tags: dict[str, str] | None,
        source: str,
        command: str,
        *params: str,
) -> Message:
    return Message(
        source=source or None,
        command=command,
        params=list(params),
        tags=tags,
    )


##


@dc.dataclass(frozen=True)
class MessageTestData:
    raw: str
    message: Message


DECODE_TESTS = list(itertools.starmap(MessageTestData, [
    (':dan-!d@localhost PRIVMSG dan #test :What a cool message\r\n', make_message(None, 'dan-!d@localhost', 'PRIVMSG', 'dan', '#test', 'What a cool message')),  # noqa
    ('@time=2848 :dan-!d@localhost LIST\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'LIST')),
    ('@time=2848 LIST\r\n', make_message({'time': '2848'}, '', 'LIST')),
    ('LIST\r\n', make_message(None, '', 'LIST')),
    ('@time=12732;re TEST *a asda:fs :fhye tegh\r\n', make_message({'time': '12732', 're': ''}, '', 'TEST', '*a', 'asda:fs', 'fhye tegh')),  # noqa
    ('@time=12732;re TEST *\r\n', make_message({'time': '12732', 're': ''}, '', 'TEST', '*')),
    (':dan- TESTMSG\r\n', make_message(None, 'dan-', 'TESTMSG')),
    (':dan- TESTMSG dan \r\n', make_message(None, 'dan-', 'TESTMSG', 'dan')),
    ('@time=2019-02-28T19:30:01.727Z ping HiThere!\r\n', make_message({'time': '2019-02-28T19:30:01.727Z'}, '', 'PING', 'HiThere!')),  # noqa
    ('@+draft/test=hi\\nthere PING HiThere!\r\n', make_message({'+draft/test': 'hi\nthere'}, '', 'PING', 'HiThere!')),
    ('ping asdf\n', make_message(None, '', 'PING', 'asdf')),
    ('JoIN  #channel\n', make_message(None, '', 'JOIN', '#channel')),
    ('@draft/label=l  join   #channel\n', make_message({'draft/label': 'l'}, '', 'JOIN', '#channel')),
    ('list', make_message(None, '', 'LIST')),
    ('list ', make_message(None, '', 'LIST')),
    ('list  ', make_message(None, '', 'LIST')),
    ('@time=2848  :dan-!d@localhost  LIST \r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'LIST')),
    ('@time=2848 :dan-!d@localhost PRIVMSG a:b :\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'PRIVMSG', 'a:b', '')),  # noqa
    ('@time=2848 :dan-!d@localhost PRIVMSG a:b ::\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'PRIVMSG', 'a:b', ':')),  # noqa
    ('@time=2848 :dan-!d@localhost PRIVMSG a:b ::hi\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'PRIVMSG', 'a:b', ':hi')),  # noqa
    ('@time=2848 :dan-!d@localhost PRIVMSG a:b :hi\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'PRIVMSG', 'a:b', 'hi')),  # noqa
    # invalid UTF8:
    ('@time=2848 :dan-!d@localhost PRIVMSG a:b :hi\xf0\xf0\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'PRIVMSG', 'a:b', 'hi\xf0\xf0')),  # noqa
    ('@time=2848 :dan-!d@localhost PRIVMSG a:b :\xf0hi\xf0\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'PRIVMSG', 'a:b', '\xf0hi\xf0')),  # noqa
    ('@time=2848 :dan-!d@localhost PRIVMSG a:b :\xff\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'PRIVMSG', 'a:b', '\xff')),  # noqa
    ('@time=2848 :dan-!d@localhost PRIVMSG a:b :\xf9g\xa6=\xcf6s\xb2\xe2\xaf\xa0kSN?\x95\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'PRIVMSG', 'a:b', '\xf9g\xa6=\xcf6s\xb2\xe2\xaf\xa0kSN?\x95')),  # noqa
    ('@time=2848 :dan-!d@localhost PRIVMSG a:b \xf9g\xa6=\xcf6s\xb2\xe2\xaf\xa0kSN?\x95\r\n', make_message({'time': '2848'}, 'dan-!d@localhost', 'PRIVMSG', 'a:b', '\xf9g\xa6=\xcf6s\xb2\xe2\xaf\xa0kSN?\x95')),  # noqa
]))


def test_decode():
    for td in DECODE_TESTS:
        pm = parse_line(td.raw)
        assert pm == td.message


##


@dc.dataclass(frozen=True)
class MessageLenTestData:
    raw: str
    length: int
    message: Message
    truncate_expected: bool


DECODE_LEN_TESTS = list(itertools.starmap(MessageLenTestData, [
    (':dan-!d@localhost PRIVMSG dan #test :What a cool message\r\n', 22, make_message(None, 'dan-!d@localhost', 'PR'), True),  # noqa
    ('@time=12732;re TEST *\r\n', 512, make_message({'time': '12732', 're': ''}, '', 'TEST', '*'), False),
    ('@time=12732;re TEST *\r\n', 512, make_message({'time': '12732', 're': ''}, '', 'TEST', '*'), False),
    (':dan- TESTMSG\r\n', 2048, make_message(None, 'dan-', 'TESTMSG'), False),
    (':dan- TESTMSG dan \r\n', 14, make_message(None, 'dan-', 'TESTMS'), True),
    ('TESTMSG\r\n', 6, make_message(None, '', 'TEST'), True),
    ('TESTMSG\r\n', 7, make_message(None, '', 'TESTM'), True),
    ('TESTMSG\r\n', 8, make_message(None, '', 'TESTMS'), True),
    ('TESTMSG\r\n', 9, make_message(None, '', 'TESTMSG'), False),
    ('PRIVMSG #chat :12 345🐬', 27, make_message(None, '', 'PRIVMSG', '#chat', '12 345🐬'), False),
    # test utf-8 aware truncation:
    # ("PRIVMSG #chat :12 345🐬", 26, make_message(None, "", "PRIVMSG", "#chat", "12 345"), True),
    ('PRIVMSG #chat :12 345', 23, make_message(None, '', 'PRIVMSG', '#chat', '12 345'), False),
]))


def test_decode_len():
    for td in DECODE_LEN_TESTS:
        pl = parse_line_strict(td.raw, True, td.length)
        assert pl.message == td.message
        assert pl.truncated == td.truncate_expected


##


ENCODE_TESTS = list(itertools.starmap(MessageTestData, [
    (':dan-!d@localhost PRIVMSG dan #test :What a cool message\r\n', make_message(None, 'dan-!d@localhost', 'PRIVMSG', 'dan', '#test', 'What a cool message')),  # noqa
    ('@time=12732 TEST *a asda:fs :fhye tegh\r\n', make_message({'time': '12732'}, '', 'TEST', '*a', 'asda:fs', 'fhye tegh')),  # noqa
    ('@time=12732 TEST *\r\n', make_message({'time': '12732'}, '', 'TEST', '*')),
    ('@re TEST *\r\n', make_message({'re': ''}, '', 'TEST', '*')),
]))


def test_encode():
    for td in ENCODE_TESTS:
        rl = render_line(td.message)
        assert rl == td.raw.encode('utf-8')


##


ENCODE_LEN_TESTS = list(itertools.starmap(MessageLenTestData, [
    (':dan-!d@lo\r\n', 12, make_message(None, 'dan-!d@localhost', 'PRIVMSG', 'dan', '#test', 'What a cool message'), True),  # noqa
    ('@time=12732 TEST *\r\n', 52, make_message({'time': '12732'}, '', 'TEST', '*'), False),
    ('@riohwihowihirgowihre TEST *\r\n', 8, make_message({'riohwihowihirgowihre': ''}, '', 'TEST', '*', '*'), True),
]))


def test_encode_len():
    for td in ENCODE_LEN_TESTS:
        rl = render_line_strict(td.message, True, td.length)
        assert rl.raw == td.raw.encode('utf-8')
        assert rl.truncated == td.truncate_expected

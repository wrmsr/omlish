from ...json.stream.utils import stream_parse_one_value


def parse(s):
    return stream_parse_one_value(
        s,
        allow_comments=True,
    )


def test_comments():
    assert parse('{//comment\n}') == {}
    assert parse('{}//comment') == {}
    assert parse('{/*comment\n** */}') == {}
    assert parse('{"abc": 420//comment\n}') == {'abc': 420}

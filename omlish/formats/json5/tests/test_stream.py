from ..stream import stream_parse_one_value


def parse(s):
    return stream_parse_one_value(s)


def test_comments():
    assert parse('{//comment\n}') == {}
    assert parse('{}//comment') == {}
    assert parse('{/*comment\n** */}') == {}
    assert parse('{"abc": 420//comment\n}') == {'abc': 420}


def test_strings():
    assert parse('"abc"') == 'abc'
    assert parse("'abc'") == 'abc'
    assert parse("""['"',"'"]""") == ['"', "'"]
    assert parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f'""") == """\b\f\n\r\t\v\0\x0f"""  # noqa
    assert parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f\\u01fF\\\n\\\r\n\\\r\\a\\'\\"'""") == """\b\f\n\r\t\v\0\x0f\u01FFa'\""""  # noqa
    assert parse("""'\\b\\f\\n\\r\\t\\v\\0\\x0f\\u01fF\\\n\\\r\n\\\r\\\u2028\\\u2029\\a\\'\\"'""") == """\b\f\n\r\t\v\0\x0f\u01FFa'\""""  # noqa
    assert parse("'\u2028\u2029'") == '\u2028\u2029'

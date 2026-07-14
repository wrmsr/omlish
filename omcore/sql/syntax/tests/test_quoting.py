from ..quoting import QuoteStyles


def test_double_quote():
    assert QuoteStyles.DOUBLE.quote('foo') == '"foo"'
    assert QuoteStyles.DOUBLE.quote('a"b') == '"a""b"'


def test_backtick():
    assert QuoteStyles.BACKTICK.quote('foo') == '`foo`'
    assert QuoteStyles.BACKTICK.quote('a`b') == '`a``b`'


def test_bracket():
    assert QuoteStyles.BRACKET.quote('foo') == '[foo]'
    assert QuoteStyles.BRACKET.quote('a]b') == '[a]]b]'

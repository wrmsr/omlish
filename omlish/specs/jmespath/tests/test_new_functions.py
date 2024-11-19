from ..parser import search


def test_match():
    assert search('[?match(@, `".e."`)]', ['abc', 'def']) == ['def']


def test_contains_variadic():
    assert search('[?contains(@, `"e"`)]', ['abc', 'def', 'ghi']) == ['def']
    assert search('[?contains(@, `"e"`, `"h"`)]', ['abc', 'def', 'ghi']) == ['def', 'ghi']


def test_in():
    assert search('[?in(@, `"def"`)]', ['abc', 'def', 'ghi']) == ['def']
    assert search('[?in(@, `"def"`, `"ghi"`)]', ['abc', 'def', 'ghi']) == ['def', 'ghi']


def test_filter_keys():
    assert search('filter_keys(&!starts_with(@, `"_"`), @)', {'a': 'a', 'b': 'b', '_c': '_c'}) == {'a': 'a', 'b': 'b'}  # noqa

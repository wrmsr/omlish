from .. import matchers as matchers_
from .. import types as types_


def test_match():
    capture = types_.Capture()
    pattern = types_.Pattern.typed(int).captured(capture)
    match = matchers_.DefaultMatcher().match(pattern, 5)
    assert match.captures.get(capture) == 5

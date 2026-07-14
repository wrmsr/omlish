from ..registry import lookup


def test_registry():
    assert lookup('utf-8').new().encode('hi') == b'hi'

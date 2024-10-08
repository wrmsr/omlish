from ..templates import DictTemplater


def test_templates():
    assert DictTemplater(dict(x='foo')).apply('hi {x}!') == 'hi foo!'

from ..parser import search


def test_drop_underscore_keys():
    d = {'a': 'a!', 'b': 'b!', '_c': '_c!'}
    assert search('items(@)', d) == [['a', 'a!'], ['b', 'b!'], ['_c', '_c!']]
    assert search('items(@)[?!starts_with(@[0],`"_"`)]|from_items(@)', d) == {'a': 'a!', 'b': 'b!'}

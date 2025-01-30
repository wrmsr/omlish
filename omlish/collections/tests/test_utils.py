from .. import utils


def test_indexes():
    assert utils.indexes('bac') == {'b': 0, 'a': 1, 'c': 2}

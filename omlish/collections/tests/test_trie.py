from ..trie import Trie


def test_trie():
    pt = Trie[str, int]()
    pt['abcd'] = 0
    assert len(pt) == 1
    assert pt['abcd'] == 0
    pt['abed'] = 1
    assert len(pt) == 2
    assert pt['abed'] == 1
    assert list(pt.items()) == [
        (('a', 'b', 'c', 'd'), 0),
        (('a', 'b', 'e', 'd'), 1),
    ]
    del pt['abcd']
    assert len(pt) == 1
    assert list(pt.items()) == [
        (('a', 'b', 'e', 'd'), 1),
    ]

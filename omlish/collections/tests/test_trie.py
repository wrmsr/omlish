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

    pt['aced'] = 2
    pt['aaed'] = 3
    pt['abea'] = 4
    assert list(pt.items()) == [
        (('a', 'b', 'e', 'd'), 1),
        (('a', 'b', 'e', 'a'), 4),
        (('a', 'c', 'e', 'd'), 2),
        (('a', 'a', 'e', 'd'), 3),
    ]
    assert list(pt.iter_items(sort_children=True)) == [
        (('a', 'a', 'e', 'd'), 3),
        (('a', 'b', 'e', 'a'), 4),
        (('a', 'b', 'e', 'd'), 1),
        (('a', 'c', 'e', 'd'), 2),
    ]

    assert pt[['a', 'a', 'e', 'd']] == 3
    pt[['a', 'b', 'ee', 'a']] = 5
    assert pt['abea'] == 4
    assert pt[['a', 'b', 'ee', 'a']] == 5
    assert list(pt.items()) == [
        (('a', 'b', 'e', 'd'), 1),
        (('a', 'b', 'e', 'a'), 4),
        (('a', 'b', 'ee', 'a'), 5),
        (('a', 'c', 'e', 'd'), 2),
        (('a', 'a', 'e', 'd'), 3),
    ]
    assert list(pt.iter_items(sort_children=True)) == [
        (('a', 'a', 'e', 'd'), 3),
        (('a', 'b', 'e', 'a'), 4),
        (('a', 'b', 'e', 'd'), 1),
        (('a', 'b', 'ee', 'a'), 5),
        (('a', 'c', 'e', 'd'), 2),
    ]
    assert list(pt.iter_items(sort_children=lambda cl: cl.sort(key=lambda ct: (-len(ct[0]), ct[0])))) == [
        (('a', 'a', 'e', 'd'), 3),
        (('a', 'b', 'ee', 'a'), 5),
        (('a', 'b', 'e', 'a'), 4),
        (('a', 'b', 'e', 'd'), 1),
        (('a', 'c', 'e', 'd'), 2),
    ]

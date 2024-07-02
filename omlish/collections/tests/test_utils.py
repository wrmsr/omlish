from .. import utils


def test_toposort():
    utils.toposort({
        0: frozenset(),
    })


def test_indexes():
    assert utils.indexes('bac') == {'b': 0, 'a': 1, 'c': 2}


def test_mut_unify_sets():
    ss = [
        {0, 1, 2},
        {0, 3, 4},
        {5, 6, 7},
        {6, 8, 9},
        {4, 10},
        {8, 11},
    ]
    us = utils.mut_unify_sets(ss)
    assert frozenset(map(frozenset, us)) == frozenset([
        frozenset([0, 1, 2, 3, 4, 10]),
        frozenset([5, 6, 7, 8, 9, 11]),
    ])

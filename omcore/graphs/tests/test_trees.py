from .. import trees


def test_basic():
    a0 = trees.BasicTreeAnalysis.from_parents({
        'a': None,
        'b': 'a',
        'c': 'a',
        'd': 'b',
    })

    a1 = trees.BasicTreeAnalysis.from_children({
        'a': ['b', 'c'],
        'b': ['d'],
        'c': [],
        'd': [],
    })

    assert a0.child_sets_by_node == a1.child_sets_by_node
    assert a0.get_lineage('d').rank('b') == 1

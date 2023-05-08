"""
TODO:
 - 'graph-like' adapter like nx?
"""
import pytest  # noqa

from .. import trees


@pytest.mark.xfail
def test_basic():
    a0 = trees.BasicTreeAnalysis.from_parents({
        'a': None,
        'b': 'a',
        'c': 'a',
        'd': 'b',
    })
    print(a0)

    a1 = trees.BasicTreeAnalysis.from_children({
        'a': ['b', 'c'],
        'b': ['d'],
        'c': [],
        'd': [],
    })
    print(a1)

    assert a0.child_sets_by_node == a1.child_sets_by_node

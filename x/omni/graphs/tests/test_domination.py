from .. import domination as domination_


def test_dom():
    g = domination_.ListDictDirectedGraph([
        (0, [1, 2]),
        (1, [4]),
        (2, [3]),
        (3, [4]),
        (4, []),
    ])

    d = domination_.DominatorTree(g, 0)

    assert d.immediate_dominators == {1: 0, 2: 0, 3: 2, 4: 0}
    assert d.dominator_tree == {0: {1, 2, 4}, 2: {3}}
    assert d.deep_dominated == {0: {1, 2, 3, 4}, 2: {3}}
    assert d.dominance_frontiers == {1: {4}, 2: {4}, 3: {4}}

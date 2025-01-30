from ..toposort import toposort


def test_toposort():
    toposort({
        0: frozenset(),
    })

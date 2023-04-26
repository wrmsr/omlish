from .. import utils


def test_toposort():
    utils.toposort({
        0: frozenset(),
    })

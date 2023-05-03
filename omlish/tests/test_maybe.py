from .. import maybe


def test_maybe():
    m = maybe.just(10)
    assert m.must() == 10

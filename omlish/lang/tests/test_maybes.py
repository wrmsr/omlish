from .. import maybes


def test_maybe():
    m = maybes.just(10)
    assert m.must() == 10

    m2 = maybes.just(maybes.just(10))
    assert m2.must().must() == 10

    m2 = maybes.just(maybes.empty())
    assert not m2.must().present

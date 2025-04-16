from ...lite import maybes as lite_maybes
from .. import maybes


def test_maybe():
    m = maybes.just(10)
    assert m.must() == 10

    m2 = maybes.just(maybes.just(10))
    assert m2.must().must() == 10

    m2 = maybes.just(maybes.empty())
    assert not m2.must().present


def test_lite():
    m = lite_maybes.as_maybe(maybes.just(10))
    assert isinstance(m, lite_maybes.Maybe)
    assert m.must() == 10

    assert lite_maybes.as_maybe(m) is m

    m2 = lite_maybes.as_maybe(maybes.just(maybes.just(10)))
    assert isinstance(m2, lite_maybes.Maybe)
    assert m2.must().must() == 10

    m2 = lite_maybes.as_maybe(maybes.just(maybes.empty()))
    assert isinstance(m2, lite_maybes.Maybe)
    assert not m2.must().present

from .. import maybes as maybes_


def test_maybe():
    assert maybes_.Maybe(1)
    assert not maybes_.Maybe.empty()
    assert maybes_.Maybe.empty() is maybes_.Maybe.empty()
    assert maybes_.Maybe('foo').value.endswith('o')
    assert next(iter(maybes_.Maybe('x'))).capitalize() == 'X'
    assert maybes_.Maybe(None)

    assert maybes_.Maybe(0) == maybes_.Maybe(0)
    assert not (maybes_.Maybe(0) != maybes_.Maybe(0))
    assert maybes_.Maybe(0) != maybes_.Maybe(1)

    assert maybes_.Maybe(0) != (0,)
    assert not (maybes_.Maybe(0) == (0,))

    assert maybes_.Maybe(0) < maybes_.Maybe(1)
    assert maybes_.Maybe(1) > maybes_.Maybe(0)

    assert maybes_.Maybe(3).map(lambda v: v + 1) == maybes_.Maybe(4)
    assert maybes_.Maybe.empty().map(lambda v: v + 1) is maybes_.Maybe.empty()

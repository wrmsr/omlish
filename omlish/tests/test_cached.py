from .. import cached


def test_nullary():
    n = 0

    @cached.nullary
    def fn():
        nonlocal n
        n += 1
        return n

    assert fn() == 1
    assert fn() == 1

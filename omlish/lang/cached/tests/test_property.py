from ..property import cached_property


def test_property():
    n = 0

    class C:
        @cached_property
        def x(self) -> int:
            nonlocal n
            n += 1
            return n

    c = C()
    assert c.x == 1
    assert c.x == 1
    assert C().x == 2
    assert C().x == 3

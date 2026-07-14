from .. import cached


def test_property():
    n = 0

    class C:
        @cached.property
        def x(self) -> int:
            nonlocal n
            n += 1
            return n

    c = C()
    assert c.x == 1
    assert c.x == 1
    assert C().x == 2
    assert C().x == 3

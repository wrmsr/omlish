import pickle

from ..attrs import transient_getattr
from ..attrs import transient_setattr


class Foo:
    def __init__(self, x: int) -> None:
        super().__init__()

        self._x = x

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(x={self.x!r}, y={self.y!r})'

    @property
    def x(self) -> int:
        return self._x

    @x.setter
    def x(self, val: int) -> None:
        self._x = val

    @property
    def y(self) -> int:
        return transient_getattr(self, 'y', 0)

    @y.setter
    def y(self, val: int) -> None:
        transient_setattr(self, 'y', val)


def test_transient():
    foo = Foo(5)
    foo.y = 6
    print(foo)
    assert foo.x == 5
    assert foo.y == 6

    foo2 = pickle.loads(pickle.dumps(foo))  # noqa
    print(foo2)
    assert foo2.x == 5
    assert foo2.y == 0

import pytest

from .. import dataclasses as dc
from ..dev import pytest as ptu


@dc.dataclass(frozen=True)
class Point:
    x: int
    y: int
    name: str = dc.field(default='foo', kw_only=True)


def test_dataclasses():
    pt = Point(1, 2)
    print(pt)


def test_reorder():
    @dc.dataclass()
    class C:
        x: int
        y: int = 5

    REQUIRED = object()

    @dc.dataclass()
    class D(C):
        z: int = dc.field(default=REQUIRED)

    # FIXME:
    # assert [f.name for f in dc.fields(D)] == ['x', 'z', 'y']


def test_check_init():
    @dc.dataclass()
    class C:
        x: int = dc.field(check=lambda x: x > 10)

        dc.check(lambda x: x < 20)

        @dc.check  # noqa
        @staticmethod
        def _check_x_not_15(x: int) -> bool:
            return x != 15

        @dc.init
        def _init_foo(self) -> None:
            self._foo = 100

    c = C(11)
    assert c._foo == 100

    with pytest.raises(Exception):
        C(9)


def test_md():
    @dc.tag(a=10)
    @dc.dataclass()
    class Foo:
        pass

    dc.tag(Foo, {'b': 20})

    assert dc.metadata(Foo) == {'a': 10, 'b': 20}


@ptu.skip_if_python_version_less_than((3, 10))
def test_kw_only():
    @dc.dataclass(**{'kw_only': True})
    class C:
        x: int

    assert C(x=10).x == 10
    with pytest.raises(Exception):
        C(10)  # noqa


def test_mcls():
    class C(dc.Data):
        x: int

    assert C(10).x == 10

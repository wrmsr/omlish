import dataclasses as _dc

import pytest

from ... import dataclasses as dc


@dc.dataclass()
class Foo:
    x: int
    y: int


@_dc.dataclass()
class Bar:
    x: int
    z: int


@dc.dataclass()
class Baz0(Foo, Bar):
    a: int


@_dc.dataclass()
class Baz1(Foo, Bar):
    a: int


def test_foo():
    print(Foo(1, 2))


@dc.dataclass()
class Bar:
    x: int = dc.field(coerce=int, check=lambda x: x < 10)


def test_bar():
    print(Bar(4))
    print(Bar('4'))  # noqa

    with pytest.raises(dc.CheckException):
        Bar(11)

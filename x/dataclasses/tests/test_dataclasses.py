import dataclasses as _dc

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

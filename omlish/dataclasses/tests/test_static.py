import abc
import dataclasses as dc
import itertools
import typing as ta

from ...manifests.base import ModAttrManifest
from ...manifests.base import NameAliasesManifest
from ..static import Static


##


FOO_COUNT = itertools.count()


@dc.dataclass(frozen=True)
class Foo:
    a: str
    b: str = 'default b'
    c: str = dc.field(default_factory=lambda: f'foo {next(FOO_COUNT)}')


class FooInst(Foo, Static):
    a = 'hi!'


class FooInst2(FooInst):
    b = 'default b 2'


def test_foo():
    print(FooInst())  # type: ignore[call-arg]
    assert FooInst() is FooInst()  # type: ignore[call-arg]
    assert FooInst().a == 'hi!'  # type: ignore[call-arg]
    assert FooInst.a == 'hi!'
    assert FooInst().b == 'default b'  # type: ignore[call-arg]
    assert FooInst.b == 'default b'
    assert FooInst().c == 'foo 0'  # type: ignore[call-arg]
    assert FooInst.c == 'foo 0'
    assert type(FooInst()) is Foo  # type: ignore[call-arg]

    print(FooInst2())  # type: ignore[call-arg]
    assert FooInst2().a == 'hi!'  # type: ignore[call-arg]
    assert FooInst2.a == 'hi!'
    assert FooInst2().b == 'default b 2'  # type: ignore[call-arg]
    assert FooInst2.b == 'default b 2'
    assert FooInst2().c == 'foo 1'  # type: ignore[call-arg]
    assert FooInst2.c == 'foo 1'
    assert type(FooInst2()) is Foo  # type: ignore[call-arg]


##


@dc.dataclass(frozen=True)
class MyManifest(NameAliasesManifest, ModAttrManifest):
    pass


class StaticModAttrManifest(ModAttrManifest, Static, abc.ABC):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        if abc.ABC not in cls.__bases__ and 'mod_name' not in cls.__dict__:
            setattr(cls, 'mod_name', cls.__module__)

        super().__init_subclass__(**kwargs)


class StaticMyManifest(MyManifest, StaticModAttrManifest, abc.ABC):
    pass


class MyManifestInst(StaticMyManifest):
    attr_name = 'FOO_COUNT'
    name = 'foo'


def test_manifest():
    print(MyManifestInst())  # type: ignore[call-arg]

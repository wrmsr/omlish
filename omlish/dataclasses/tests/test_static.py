import abc
import dataclasses as dc
import itertools
import typing as ta

from ... import lang
from ...manifests.base import ModAttrManifest
from ...manifests.base import NameAliasesManifest
from ..tools.static import Static


##


FOO_COUNT = itertools.count()


@dc.dataclass(frozen=True)
class Foo:
    a: str
    b: str = 'default b'
    c: str = dc.field(default_factory=lambda: f'foo {next(FOO_COUNT)}')


class FooInst(Static, Foo):
    a = 'hi!'


class FooInst2(FooInst):
    b = 'default b 2'


def test_foo():
    print(FooInst())
    assert FooInst() is FooInst()
    assert FooInst().a == 'hi!'
    assert FooInst.a == 'hi!'
    assert FooInst().b == 'default b'
    assert FooInst.b == 'default b'
    assert FooInst().c == 'foo 0'
    assert FooInst.c == 'foo 0'
    assert type(FooInst()) is Foo

    print(FooInst2())
    assert FooInst2().a == 'hi!'
    assert FooInst2.a == 'hi!'
    assert FooInst2().b == 'default b 2'
    assert FooInst2.b == 'default b 2'
    assert FooInst2().c == 'foo 1'
    assert FooInst2.c == 'foo 1'
    assert type(FooInst2()) is Foo


##


@dc.dataclass(frozen=True)
class MyManifest(NameAliasesManifest, ModAttrManifest):
    pass


class StaticModAttrManifest(Static, ModAttrManifest, abc.ABC):
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        if (
                not (lang.is_abstract_class(cls) or abc.ABC in cls.__bases__) and
                'mod_name' not in cls.__dict__
        ):
            setattr(cls, 'mod_name', cls.__module__)

        super().__init_subclass__(**kwargs)


class StaticMyManifest(StaticModAttrManifest, MyManifest, abc.ABC):
    pass


class MyManifestInst(StaticMyManifest):
    attr_name = 'FOO_COUNT'
    name = 'foo'


def test_manifest():
    print(MyManifestInst())

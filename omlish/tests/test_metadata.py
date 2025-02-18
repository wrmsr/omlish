import dataclasses as dc
import functools

import pytest

from ..metadata import ClassDecoratorObjectMetadata
from ..metadata import DecoratorObjectMetadata
from ..metadata import FunctionDecoratorObjectMetadata
from ..metadata import get_object_metadata


##


@dc.dataclass(frozen=True)
class FooMetadata(DecoratorObjectMetadata):
    foo: str


@dc.dataclass(frozen=True)
class BarMetadata(DecoratorObjectMetadata):
    bar: str


##


def test_function_metadata():
    def qux(x):
        return x + 1

    assert not get_object_metadata(qux)
    assert FooMetadata('1')(qux) is qux
    assert get_object_metadata(qux) == [FooMetadata('1')]

    assert get_object_metadata(functools.partial(qux, 1)) == [FooMetadata('1')]


##


class FooClass:
    def __init__(self):
        super().__init__()

    def f(self, x):
        return x + 1

    def g(self):
        pass

    @classmethod
    def h(cls, x):
        return x + 1

    @staticmethod
    def i():
        pass


def test_class_metadata():
    assert not get_object_metadata(FooClass)
    assert not get_object_metadata(FooClass.__init__)
    assert not get_object_metadata(FooClass.f)
    assert not get_object_metadata(FooClass.g)
    assert not get_object_metadata(FooClass.h)
    assert not get_object_metadata(FooClass.i)

    assert FooMetadata('1')(FooClass) is FooClass
    assert get_object_metadata(FooClass) == [FooMetadata('1')]
    assert not get_object_metadata(FooClass.__init__)
    assert not get_object_metadata(FooClass.f)

    assert BarMetadata('a')(FooClass) is FooClass
    assert get_object_metadata(FooClass) == [FooMetadata('1'), BarMetadata('a')]

    assert FooMetadata('2')(FooClass.f) is FooClass.f
    assert get_object_metadata(FooClass) == [FooMetadata('1'), BarMetadata('a')]
    assert not get_object_metadata(FooClass.__init__)
    assert get_object_metadata(FooClass.f) == [FooMetadata('2')]
    assert get_object_metadata(FooClass().f) == [FooMetadata('2')]
    assert get_object_metadata(functools.partial(FooClass().f, 1)) == [FooMetadata('2')]

    assert not get_object_metadata(FooClass.h)
    assert FooMetadata('3')(FooClass.h).__func__ is FooClass.__dict__['h'].__func__  # type: ignore[attr-defined]
    assert get_object_metadata(FooClass.h) == [FooMetadata('3')]
    assert get_object_metadata(FooClass.__dict__['h']) == [FooMetadata('3')]
    assert get_object_metadata(functools.partial(FooClass.h, 1)) == [FooMetadata('3')]

    assert FooMetadata('4')(FooClass.__dict__['h']) is FooClass.__dict__['h']
    assert get_object_metadata(FooClass.h) == [FooMetadata('3'), FooMetadata('4')]
    assert get_object_metadata(FooClass.__dict__['h']) == [FooMetadata('3'), FooMetadata('4')]


##


@dc.dataclass(frozen=True)
class ClassBazMetadata(ClassDecoratorObjectMetadata):
    baz: str


@dc.dataclass(frozen=True)
class FunctionBazMetadata(FunctionDecoratorObjectMetadata):
    baz: str


class BazTargetClass:
    def f(self):
        pass


def test_type_specific_subclasses():
    def qux(x):
        return x + 1

    assert not get_object_metadata(qux)
    assert FunctionBazMetadata('a')(qux) is qux
    assert get_object_metadata(qux) == [FunctionBazMetadata('a')]
    with pytest.raises(TypeError):
        ClassBazMetadata('b')(qux)

    assert not get_object_metadata(BazTargetClass)
    assert ClassBazMetadata('b')(BazTargetClass) is BazTargetClass
    assert get_object_metadata(BazTargetClass) == [ClassBazMetadata('b')]
    with pytest.raises(TypeError):
        FunctionBazMetadata('b')(BazTargetClass)

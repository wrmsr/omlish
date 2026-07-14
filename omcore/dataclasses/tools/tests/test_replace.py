import dataclasses as dc
import operator

from ..replace import deep_replace
from ..replace import merge_if
from ..replace import merge_is_not
from ..replace import merge_ne
from ..replace import replace_if
from ..replace import replace_is_not
from ..replace import replace_ne


def test_deep_replace_empty():
    @dc.dataclass(frozen=True)
    class Point:
        x: int
        y: int

    p = Point(1, 2)
    assert deep_replace(p) == p


def test_deep_replace_with_function():
    @dc.dataclass(frozen=True)
    class Point:
        x: int
        y: int

    p = Point(1, 2)
    result = deep_replace(p, lambda o: {'x': o.x * 2})
    assert result.x == 2
    assert result.y == 2


def test_deep_replace_nested():
    @dc.dataclass(frozen=True)
    class Inner:
        value: int

    @dc.dataclass(frozen=True)
    class Outer:
        inner: Inner
        name: str

    obj = Outer(Inner(10), 'test')
    result = deep_replace(obj, 'inner', lambda o: {'value': o.value + 5})
    assert result.inner.value == 15
    assert result.name == 'test'


def test_replace_if():
    @dc.dataclass(frozen=True)
    class Point:
        x: int
        y: int

    p = Point(1, 2)
    result = replace_if(operator.ne, p, x=1, y=3)
    assert result.x == 1
    assert result.y == 3


def test_replace_if_no_changes():
    @dc.dataclass(frozen=True)
    class Point:
        x: int
        y: int

    p = Point(1, 2)
    result = replace_if(operator.ne, p, x=1, y=2)
    assert result is p


def test_replace_ne():
    @dc.dataclass(frozen=True)
    class Point:
        x: int
        y: int

    p = Point(1, 2)
    result = replace_ne(p, x=5, y=2)
    assert result.x == 5
    assert result.y == 2


def test_replace_ne_no_changes():
    @dc.dataclass(frozen=True)
    class Point:
        x: int
        y: int

    p = Point(1, 2)
    result = replace_ne(p, x=1, y=2)
    assert result is p


def test_replace_is_not():
    @dc.dataclass(frozen=True)
    class Container:
        items: list[int] | None = None

    c = Container(None)
    new_list = [1, 2, 3]
    result = replace_is_not(c, items=new_list)
    assert result.items is new_list


def test_replace_is_not_same_object():
    @dc.dataclass(frozen=True)
    class Container:
        items: list[int] | None = None

    shared_list = [1, 2, 3]
    c = Container(shared_list)
    result = replace_is_not(c, items=shared_list)
    assert result is c


def test_merge_if():
    @dc.dataclass(frozen=True)
    class Config:
        a: int
        b: int
        c: int

    base = Config(1, 2, 3)
    override1 = Config(10, 2, 30)
    override2 = Config(100, 200, 30)

    result = merge_if(operator.ne, base, override1, override2)
    assert result.a == 100
    assert result.b == 200
    assert result.c == 30


def test_merge_if_no_changes():
    @dc.dataclass(frozen=True)
    class Config:
        a: int
        b: int

    base = Config(1, 2)
    override = Config(1, 2)

    result = merge_if(operator.ne, base, override)
    assert result is base


def test_merge_ne():
    @dc.dataclass(frozen=True)
    class Config:
        a: int
        b: int
        c: int

    base = Config(1, 2, 3)
    override = Config(10, 2, 30)

    result = merge_ne(base, override)
    assert result.a == 10
    assert result.b == 2
    assert result.c == 30


def test_merge_ne_multiple():
    @dc.dataclass(frozen=True)
    class Config:
        x: int
        y: int
        z: int

    base = Config(0, 0, 0)
    override1 = Config(1, 0, 0)
    override2 = Config(1, 2, 0)
    override3 = Config(1, 0, 3)

    result = merge_ne(base, override1, override2, override3)
    assert result.x == 1
    assert result.y == 2
    assert result.z == 3


def test_merge_is_not_none_multiple():
    @dc.dataclass(frozen=True)
    class Config:
        x: int | None = None
        y: int | None = None
        z: int | None = None

    base = Config(z=3)
    override1 = Config(x=1)
    override2 = Config(y=2)
    override3 = Config(y=3)

    assert merge_if(None, base, override1, override2, override3) == Config(1, 3, 3)
    assert merge_if(None, base, override1, override3, override2) == Config(1, 2, 3)


def test_merge_is_not():
    @dc.dataclass(frozen=True)
    class Container:
        a: list[int] | None = None
        b: list[int] | None = None

    list1 = [1, 2]
    list2 = [3, 4]

    base = Container(None, None)
    override = Container(list1, list2)

    result = merge_is_not(base, override)
    assert result.a is list1
    assert result.b is list2


def test_merge_is_not_same_object():
    @dc.dataclass(frozen=True)
    class Container:
        a: list[int] | None = None
        b: list[int] | None = None

    shared = [1, 2]

    base = Container(shared, shared)
    override = Container(shared, [3, 4])

    result = merge_is_not(base, override)
    assert result.a is shared
    assert result.b == [3, 4]

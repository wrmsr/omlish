import typing as ta

from ..bindable import BindableClass


T = ta.TypeVar('T')


class MyBindable(BindableClass[T]):
    @classmethod
    def foo(cls, foo: ta.Any) -> dict:
        return {
            '_bound': cls._bound,
            'foo': foo,
        }

    @classmethod
    def bar(cls, foo: ta.Any, bar: ta.Any) -> dict:
        return {
            **cls.foo(foo),
            'bar': bar,
        }


def test_bindable():
    assert MyBindable.foo(1) == {'_bound': None, 'foo': 1}
    assert MyBindable[int].foo(1) == {'_bound': int, 'foo': 1}
    assert MyBindable.bar(1, 2) == {'_bound': None, 'foo': 1, 'bar': 2}
    assert MyBindable[int].bar(1, 2) == {'_bound': int, 'foo': 1, 'bar': 2}

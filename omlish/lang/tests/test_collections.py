import typing as ta

import pytest

from ..collections import yield_dict_init


def test_yield_dict_init_simple():
    assert list(yield_dict_init([(1, 2), (3, 4)])) == [(1, 2), (3, 4)]
    assert list(yield_dict_init([(1, 2), (3, 4)], foo=5)) == [(1, 2), (3, 4), ('foo', 5)]

    assert list(yield_dict_init({1: 2, 3: 4})) == [(1, 2), (3, 4)]


def test_yield_dict_init_mapping_uses_items():
    class BadError(Exception):
        pass

    class CustomMapping(ta.Mapping):
        def __getitem__(self, key, /):
            raise BadError

        def __len__(self):
            raise BadError

        def __iter__(self):
            raise BadError

        def items(self):
            return iter([(1, 2), (3, 4)])

    assert list(yield_dict_init(CustomMapping())) == [(1, 2), (3, 4)]


def test_yield_dict_init_keys_iter():
    class TooFarError(Exception):
        pass

    class Foo:
        def keys(self):
            return [1, 2]

        def __getitem__(self, k):
            if k > 2:
                raise TooFarError
            return k * 2

    with pytest.raises(TooFarError):
        # Per https://docs.python.org/3/library/functions.html#iter Foo iter()'s infinitely - assert this behavior.
        list(Foo())  # type: ignore[call-overload]

    assert dict(Foo()) == {1: 2, 2: 4}
    assert list(yield_dict_init(Foo())) == [(1, 2), (2, 4)]

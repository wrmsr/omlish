import typing as ta

from .. import check
from .. import dataclasses as dc
from .types import Injector
from .types import Key
from .types import MultiBinding
from .types import MultiProvider


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


class SetBinding(dc.Pure, MultiBinding[T]):
    pass


class SetProvider(dc.Pure, MultiProvider[ta.AbstractSet[T]]):
    set_key: Key[ta.AbstractSet[T]]

    def __call__(self) -> ta.AbstractSet[T]:
        ret = set()
        bindings = Injector.current.get_bindings(Key(SetBinding[self.set_key.type], self.set_key.annotation))
        for binding in bindings:
            check.isinstance(binding, SetBinding)
            ret.add(binding.provide())
        return ret


class DictBinding(dc.Pure, MultiBinding[K]):
    assignment: K


class DictProvider(dc.Pure, MultiProvider[ta.Mapping[K, V]]):
    dict_key: Key[ta.Mapping[K, V]]

    def __call__(self) -> ta.Mapping[K, V]:
        ret = {}
        bindings = Injector.current.get_bindings(Key(DictBinding[self.dict_key.type], self.dict_key.annotation))
        for binding in bindings:
            check.isinstance(binding, DictBinding)
            check.not_in(binding.assignment, ret)
            ret[binding.assignment] = binding.provide()
        return ret

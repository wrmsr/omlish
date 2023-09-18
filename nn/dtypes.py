import abc
import functools
import typing as ta

from omlish import check
from omlish import dataclasses as dc
from omlish import lang
import numpy as np_


@functools.total_ordering
class Dtype(lang.Abstract, lang.Sealed):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def priority(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def np(self) -> ta.Any:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def item_size(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def is_int(self) -> bool:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def sz(self) -> int:  # vector_size / num_items
        raise NotImplementedError

    def __repr__(self) -> str:
        return f'<Dtype:{self.name}>'

    def __lt__(self, other):
        o = check.isinstance(other, Dtype)
        return self.priority < o.priority and self.item_size < o.item_size

    @staticmethod
    def of_np(npdt: np_.dtype) -> 'Dtype':
        if npdt == np_.float32:
            return Float32
        raise ValueError(npdt)


@dc.dataclass(frozen=True, repr=False, eq=False)
class ConcreteDtype(Dtype, lang.Final):
    name: str = dc.field(override=True)
    priority: int = dc.field(override=True)
    np: ta.Any = dc.field(override=True)
    item_size: int = dc.field(override=True)

    is_int: bool = dc.field(False, override=True)

    sz: int = dc.field(1, override=True)


Float32 = ConcreteDtype('float32', 4, np_.float32, 4)
Float4 = ConcreteDtype('float4', 4, None, 1, sz=4)


@dc.dataclass(frozen=True, repr=False, eq=False)
class PtrDtype(Dtype, lang.Final):
    elem: Dtype

    @property
    def name(self) -> str:
        return f'ptr.{self.elem.name}'

    @property
    def priority(self) -> int:
        return self.elem.priority

    @property
    def np(self) -> ta.Any:
        raise TypeError

    @property
    def item_size(self) -> int:
        return self.elem.item_size

    @property
    def is_int(self) -> bool:
        return self.elem.is_int

    @property
    def sz(self) -> int:  # vector_size / num_items
        return self.elem.sz


def ptr(elem: Dtype) -> PtrDtype:
    return PtrDtype(elem)

import functools
import typing as ta

from omlish import check
from omlish import dataclasses as dc
import numpy as np


@functools.total_ordering
@dc.dataclass(frozen=True, repr=False, eq=False)
class Dtype:
    name: str
    priority: int
    np: ta.Any
    item_size: int

    is_int: bool = False

    sz: int = 1

    def __repr__(self) -> str:
        return f'<Dtype:{self.name}>'

    def __lt__(self, other):
        o = check.isinstance(other, Dtype)
        return self.priority < other.priority and self.item_size < other.item_size

    @staticmethod
    def of_np(npdt: np.dtype) -> 'Dtype':
        if npdt == np.float32:
            return Float32
        raise ValueError(npdt)


Float32 = Dtype('float32', 4, np.float32, 4)
Float4 = Dtype('float4', 4, None, 1, sz=4)

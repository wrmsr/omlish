import typing as ta

from omlish import dataclasses as dc
import numpy as np


@dc.dataclass(frozen=True, repr=False)
class Dtype:
    name: str
    np: ta.Any
    item_size: int

    is_int: bool = False

    sz: ta.Final[int] = 1   # FIXME:

    def __repr__(self) -> str:
        return f'<Dtype:{self.name}>'

    @staticmethod
    def of_np(npdt: np.dtype) -> 'Dtype':
        if npdt == np.float32:
            return Float32
        raise ValueError(npdt)


Float32 = Dtype('float32', np.float32, 4)
Float4 = Dtype('float4', None, 1)

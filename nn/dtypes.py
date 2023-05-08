from omlish import dataclasses as dc
import numpy as np


@dc.dataclass(frozen=True)
class Dtype:
    name: str

    @staticmethod
    def of_np(npdt: np.dtype) -> 'Dtype':
        if npdt == np.float32:
            return Float32
        raise ValueError(npdt)


Float32 = Dtype('float32')

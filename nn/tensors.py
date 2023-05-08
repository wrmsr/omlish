import typing as ta

from omlish import check

from .funcs import Func
from .lazy import LazyBuffer


class Tensor:
    def __init__(self, data: LazyBuffer, requires_grad: ta.Optional[bool]) -> None:
        super().__init__()

        self._data = check.isinstance(data, LazyBuffer)
        self._requires_grad = check.isinstance(requires_grad, (bool, None))

        self._grad: ta.Optional['Tensor'] = None
        self._func: ta.Optional[Func] = None

    @property
    def data(self) -> LazyBuffer:
        return self._data

    @property
    def requires_grad(self) -> ta.Optional[bool]:
        return self._requires_grad

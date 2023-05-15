import abc
import itertools
import typing as ta

from omlish import check
from omlish import lang

from .tensor import Tensor


class Optimizer(lang.Abstract):

    def __init__(self, ts: ta.Iterable[Tensor]) -> None:
        super().__init__()

        ts = [check.isinstance(t, Tensor) for t in ts]

        # if it's None, but being put into an optimizer, set it to True
        for t in ts:
            if t.requires_grad is None:
                t.set_requires_grad(True)

        self._params: ta.List[Tensor] = [x for x in ts if x.requires_grad]
        self._buffers: ta.List[Tensor] = [x for x in ts if not x.requires_grad]  # buffers are still realized

    @abc.abstractmethod
    def step(self) -> None:
        raise NotImplementedError

    def zero_grad(self) -> None:
        for p in self._params:
            p.zero_grad()

    def realize(self, extra: ta.Optional[ta.Iterable[Tensor]] = None) -> None:
        # TODO: corealize  # TODO: wut
        # NOTE: in extra is too late for most of the params due to issues with assign
        for t in itertools.chain(
                (extra if extra else []),
                self._params,
                self._buffers,
        ):
            t.realize()

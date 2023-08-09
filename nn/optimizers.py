import abc
import itertools
import typing as ta

from omlish import check
from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang

from .tensor import Tensor


class Optimizer(lang.Abstract):

    def __init__(self, ts: ta.Iterable[Tensor], lr: float) -> None:
        super().__init__()

        ts = [check.isinstance(t, Tensor) for t in ts]

        # if it's None, but being put into an optimizer, set it to True
        for t in ts:
            if t.requires_grad is None:
                t.set_requires_grad(True)

        self._params: ta.List[Tensor] = col.unique((x for x in ts if x.requires_grad), identity=True)
        self._buffers: ta.List[Tensor] = col.unique((x for x in ts if not x.requires_grad), identity=True)  # buffers are still realized  # noqa
        self._lr = Tensor(lr, requires_grad=False)

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


class Sgd(Optimizer):
    class Config(dc.Data):
        lr: float = 0.001
        momentum: float = 0.
        nesterov: bool = False
        weight_decay: float = 0.

    def __init__(self, ts: ta.Iterable[Tensor], config: Config = Config()) -> None:
        super().__init__(ts, config.lr)
        self._config = config

        self._b = [
            Tensor.zeros(*t.shape, device=t.device, requires_grad=False)
            for t in self._params
        ] if config.momentum else []

    def step(self) -> None:
        # https://pytorch.org/docs/stable/generated/torch.optim.SGD.html
        for i, t in enumerate(self._params):
            g = check.not_none(t.get_grad()).realize() + self._config.weight_decay * t.detach()
            if self._config.momentum:
                self._b[i].assign(
                    # NOTE: self.b[i] is zero on the first run, no if required
                    self._config.momentum * self._b[i] + g
                ).realize()
                if self._config.nesterov:
                    g = g + self._config.momentum * self._b[i]
                else:
                    g = self._b[i]
            t.assign(t.detach() - g * self._lr)

        self.realize(self._b)

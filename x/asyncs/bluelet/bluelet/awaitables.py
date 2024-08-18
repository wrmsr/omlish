import dataclasses as dc
import typing as ta


from .core import BlueletCoro
from .core import BlueletEventT
from .core import ReturnBlueletEvent


R = ta.TypeVar('R')


@dc.dataclass(eq=False)
class BlueletFuture(ta.Generic[BlueletEventT, R]):
    event: BlueletEventT
    done: bool = False
    result: R = None

    def __await__(self):
        if not self.done:
            yield self
        if not self.done:
            raise RuntimeError("await wasn't used with task")
        return self.result


def bluelet_drive_awaitable(a: ta.Awaitable) -> BlueletCoro:
    g = a.__await__()
    gi = iter(g)
    while True:
        try:
            f = gi.send(None)
        except StopIteration as e:
            yield ReturnBlueletEvent(e.value)
            break
        else:
            if not isinstance(f, BlueletFuture):
                raise TypeError(f)
            res = yield f.event
            f.done = True
            f.result = res

"""
TODO:
 - weird switching crap: https://greenlet.readthedocs.io/en/latest/switching.html
 - SpawnedRealThreadlet vs GraftedRealThreadlet prob

"""
import abc
import dataclasses as dc
import threading
import typing as ta

import greenlet

from omlish import lang


##


class Threadlet(abc.ABC):
    """Not safe to identity-key - use `underlying`."""

    @property
    @abc.abstractmethod
    def underlying(self) -> ta.Any:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def parent(self) -> ta.Optional['Threadlet']:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def dead(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def switch(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def throw(self, ex: Exception) -> ta.Any:
        raise NotImplementedError


class Threadlets(abc.ABC):
    @abc.abstractmethod
    def spawn(self, fn: ta.Callable[[], None]) -> Threadlet:
        raise NotImplementedError

    @abc.abstractmethod
    def get_current(self) -> Threadlet:
        raise NotImplementedError


##


@dc.dataclass(frozen=True)
class GreenletThreadlet(Threadlet):
    g: greenlet.greenlet

    @property
    def underlying(self) -> greenlet.greenlet:
        return self.g

    @property
    def parent(self) -> ta.Optional['GreenletThread']:
        return GreenletThreadlet(self.g.parent)

    @property
    def dead(self) -> bool:
        return self.g.dead

    def switch(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        return self.g.switch(*args, **kwargs)

    def throw(self, ex: Exception) -> ta.Any:
        return self.g.throw(ex)


class GreenletThreadlets(Threadlets):
    def spawn(self, fn: ta.Callable[[], None]) -> Threadlet:
        return GreenletThreadlet(greenlet.greenlet(fn))

    def get_current(self) -> Threadlet:
        return GreenletThreadlet(greenlet.getcurrent())


##


class RealThreadlet(Threadlet, abc.ABC):
    def __init__(self, t: threading.Thread) -> None:
        super().__init__()
        self._t = t

    @property
    def underlying(self) -> threading.Thread:
        return self._t

    @property
    def dead(self) -> bool:
        return self._t.is_alive()


class SpawnedRealThreadlet(RealThreadlet):
    def __init__(self, fn: ta.Callable[[], None]) -> None:
        super().__init__(threading.Thread(target=self._main))
        self._fn = fn

    @property
    def parent(self) -> ta.Optional['Threadlet']:
        raise NotImplementedError

    def switch(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        raise NotImplementedError

    def throw(self, ex: Exception) -> ta.Any:
        raise NotImplementedError

    #

    def _main(self) -> None:
        self._fn()


class RealThreadlets(Threadlets):
    def spawn(self, fn: ta.Callable[[], None]) -> Threadlet:
        return SpawnedRealThreadlet(fn)

    def get_current(self) -> Threadlet:
        raise NotImplementedError


##


def _test_threadlets(api: Threadlets):
    done = 0

    def test1():
        gr2.switch()
        gr2.switch()
        nonlocal done
        done += 1

    def test2():
        def f():
            gr1.switch()
        f()
        nonlocal done
        done += 1
        gr1.switch()

    gr1 = api.spawn(test1)
    gr2 = api.spawn(test2)
    gr1.switch()
    assert done == 2


def test_greenlet():
    _test_threadlets(GreenletThreadlets())


def test_real():
    _test_threadlets(RealThreadlets())

"""
TODO:
 - this has to be named brownlet doesnt it
 - weird switching crap: https://greenlet.readthedocs.io/en/latest/switching.html
 - SpawnedRealThreadlet vs GraftedRealThreadlet prob

"""
import abc
import dataclasses as dc
import itertools
import logging
import threading
import typing as ta

import greenlet

from omlish import lang
from omlish import logs


log = logging.getLogger(__name__)


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


def _squash_args(args: lang.Args) -> ta.Any:
    a, k = tuple(args.args), args.kwargs
    if a:
        if k:
            return a, k
        else:
            return a
    elif k:
        return k
    else:
        return None


class RealThreadlet(Threadlet, abc.ABC):
    _seq_counter = itertools.count()

    def __init__(
            self,
            s: 'RealThreadlets',
            t: threading.Thread, *, seq: int | None = None,
    ) -> None:
        super().__init__()
        self._s = s
        self._t = t
        self._seq = seq if seq is not None else next(self._seq_counter)

        self._lock = threading.Lock()

        self._started = False
        self._paused = False

        self._in_value: lang.Maybe[lang.Args] = lang.empty()
        self._in_event = threading.Event()

    @property
    def underlying(self) -> threading.Thread:
        return self._t

    @property
    def parent(self) -> ta.Optional['Threadlet']:
        raise NotImplementedError

    @property
    def dead(self) -> bool:
        return self._t.is_alive()

    @classmethod
    def _switch(cls, src: 'RealThreadlet', dst: 'RealThreadlet') -> ta.Any:
        log.debug('switch: begin: %d -> %d', id(src), id(dst))

        with self._lock:
            if not self._started:
                log.debug('switch: thread not started, starting')

                if self._t.is_alive():
                    raise Exception

                self._switch_in_value = lang.just(lang.Args(*args, **kwargs))
                self._switch_in_event.set()

                self._t.start()
                self._started = True

            else:
                log.debug('switch: thread already started')

                if not self._paused:
                    raise Exception

                self._switch_in_value = lang.just(lang.Args(*args, **kwargs))
                self._switch_in_event.set()

        log.debug('switch: _switch_out_event.wait: begin')
        self._switch_out_event.wait()
        log.debug('switch: _switch_out_event.wait: end')

        with self._lock:
            self._switch_out_event.clear()

            out_value = self._switch_out_value.must()
            self._switch_out_value = lang.empty()

        log.debug('switch: end: %r', out_value)

        return _squash_args(out_value)

    def switch(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        src = self._s.get_current()
        return self._switch(src, self)

    def throw(self, ex: Exception) -> ta.Any:
        raise NotImplementedError


class SpawnedRealThreadlet(RealThreadlet):
    def __init__(
            self,
            s: 'RealThreadlets',
            fn: ta.Callable[[], ta.Any],
    ) -> None:
        seq = next(self._seq_counter)

        super().__init__(
            s,
            threading.Thread(
                target=self._main,
                name=f'{self.__class__.__name__}-{seq}',
            ),
            seq=seq,
        )

        self._fn = fn

    #

    def _inner_switch(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        log.debug('_inner_switch: begin')

        with self._lock:
            self._switch_out_value = lang.Args(*args, **kwargs)
            self._switch_out_event.set()

            self._paused = True

        log.debug('_inner_switch: _switch_in_event.wait: begin')
        self._switch_in_event.wait()
        log.debug('_inner_switch: _switch_in_event.wait: end')

        with self._lock:
            self._switch_in_event.clear()

            self._paused = False

    def _main(self) -> None:
        log.debug('_main: begin')

        log.debug('_main: _switch_in_event.wait: begin')
        self._switch_in_event.wait()
        log.debug('_main: _switch_in_event.wait: end')

        with self._lock:
            self._switch_in_event.clear()

            in_value = self._switch_in_value.must()
            self._switch_in_value = lang.empty()

        out_value = self._fn(*in_value.args, **in_value.kwargs)

        with self._lock:
            self._switch_out_value = lang.just(out_value)
            self._switch_out_event.set()

        log.debug('_main: end')


class GraftedRealThreadlet(RealThreadlet):
    pass


class RealThreadlets(Threadlets):
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.Lock()
        self._dct: dict[threading.Thread, RealThreadlet] = {}

    def spawn(self, fn: ta.Callable[[], None]) -> RealThreadlet:
        new = SpawnedRealThreadlet(self, fn)

        with self._lock:
            self._dct[new.underlying] = new

        return new

    def get_current(self) -> RealThreadlet:
        with self._lock:
            try:
                return self._dct[threading.current_thread()]
            except KeyError:
                pass

            new = GraftedRealThreadlet(self, threading.current_thread())
            self._dct[new.underlying] = new
            return new


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


# def test_greenlet():
#     _test_threadlets(GreenletThreadlets())


class ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record):
        self.records.append(record)


LOG_LIST = ListHandler()


def test_real():
    logs.configure_standard_logging('DEBUG')
    log.addHandler(LOG_LIST)

    _test_threadlets(RealThreadlets())

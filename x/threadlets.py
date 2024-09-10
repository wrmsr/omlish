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
            t: threading.Thread,
            *,
            paused: bool,
            seq: int | None = None,
    ) -> None:
        super().__init__()
        self._s = s
        self._t = t
        self._seq = seq if seq is not None else next(self._seq_counter)

        self._lock = threading.Lock()

        self._paused = paused

        self._in_value: lang.Maybe[lang.Args | Exception] = lang.empty()
        self._in_event = threading.Event()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self._t!r})'

    @property
    def underlying(self) -> threading.Thread:
        return self._t

    @property
    def dead(self) -> bool:
        return not self._t.is_alive()

    def _unswitch(self) -> lang.Args:
        self._in_event.wait()

        with self._lock:
            self._in_event.clear()

            in_value = self._in_value.must()
            self._in_value = lang.empty()

            self._paused = False

        log.info('UNSWITCHED: %r :: %r', self, in_value)

        if isinstance(in_value, Exception):
            raise in_value

        return in_value

    @classmethod
    def _switch(
            cls,
            src: 'RealThreadlet',
            dst: 'RealThreadlet',
            in_value: lang.Args | Exception,
    ) -> None:
        log.info('SWITCHING: %r -> %r :: %r', src, dst, in_value)

        t0, t1 = sorted((src, dst), key=lambda t: t._seq)  # noqa
        with t0._lock:  # noqa
            with t1._lock:  # noqa
                if src._paused:
                    raise Exception
                if not dst._paused:
                    raise Exception

                if isinstance(dst, SpawnedRealThreadlet) and not dst._started:
                    dst._t.start()
                    dst._started = True
                else:
                    if not dst._paused:
                        raise Exception

                dst._in_value = lang.just(in_value)
                dst._in_event.set()

                src._paused = True

    def switch(self, *args: ta.Any, **kwargs: ta.Any) -> ta.Any:
        src = self._s.get_current()

        self._switch(src, self, lang.Args(*args, **kwargs))

        in_value = src._unswitch()

        return _squash_args(in_value)

    def throw(self, ex: Exception) -> ta.Any:
        raise NotImplementedError


class SpawnedRealThreadlet(RealThreadlet):
    def __init__(
            self,
            s: 'RealThreadlets',
            fn: ta.Callable[[], ta.Any],
            parent: RealThreadlet,
    ) -> None:
        seq = next(self._seq_counter)

        super().__init__(
            s,
            threading.Thread(
                target=self._main,
                name=f'{self.__class__.__name__}-{seq}',
            ),
            paused=True,
            seq=seq,
        )

        self._fn = fn
        self._parent = parent

        self._started = False

    @property
    def parent(self) -> RealThreadlet:
        return self._parent

    def _main(self) -> None:
        try:
            log.info('ENTERING: %r', self)

            in_value = self._unswitch()

            out_value = self._fn(*in_value.args, **in_value.kwargs)

            RealThreadlet._switch(self, self._parent, lang.Args(out_value))

        except ShutdownException:
            log.info('SHUTDOWN: %r', self)

        finally:
            log.info('EXITING: %r', self)


class GraftedRealThreadlet(RealThreadlet):
    def __init__(
            self,
            s: 'RealThreadlets',
            t: threading.Thread,
    ) -> None:
        super().__init__(s, t, paused=False)

    @property
    def parent(self) -> Threadlet | None:
        return None


class RealThreadlets(Threadlets):
    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.Lock()
        self._dct: dict[threading.Thread, RealThreadlet] = {}
        self._main: GraftedRealThreadlet | None = None

    def spawn(self, fn: ta.Callable[[], None]) -> RealThreadlet:
        new = SpawnedRealThreadlet(self, fn, self.get_current())

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


class ShutdownException(Exception):
    pass


# def test_greenlet():
#     _test_threadlets(GreenletThreadlets())


LOG_LIST = logs.ListHandler()


def test_real():
    logs.configure_standard_logging('DEBUG')
    log.addHandler(LOG_LIST)

    s = RealThreadlets()
    _test_threadlets(s)
    for t in s._dct.values():
        if isinstance(t, SpawnedRealThreadlet):
            log.info('MAYBE SHUTDOWN: %r', t)
            # if t.dead:
            #     breakpoint()
            if not t.dead:
                log.info('SHUTDOWN: %r', t)
                t._switch(s.get_current(), t, ShutdownException())

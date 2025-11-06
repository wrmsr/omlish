"""
TODO:
 - more aggressive import metapath hook to forbid early imports
 - mode to make main thread the executor? :/
"""
import concurrent.futures as cf
import dataclasses as dc
import functools
import queue
import threading
import typing as ta

from omlish import check
from omlish import lang
from omlish.logs import all as logs


T = ta.TypeVar('T')
P = ta.ParamSpec('P')

O = ta.TypeVar('O')
I = ta.TypeVar('I')
R = ta.TypeVar('R')


log = logs.get_module_logger(globals())


##


class DedicatedThreadExecutor:
    """
    TODO:
     - error / thread death reporting lol
     - stop sync is busted im sure
     - timeouts lol
     - some kinda import guard, at least an attempt
    """

    def __init__(
            self,
            *,
            daemon: bool = True,
    ) -> None:
        super().__init__()

        self._daemon = daemon

        self._lock = threading.RLock()

        self._startup_callbacks: list[ta.Callable[[], None]] = []

        self._thread: threading.Thread | None = None

    _queue: queue.Queue

    _thread_exception: BaseException | None = None

    @property
    def _self_repr_str(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}'

    def __repr__(self) -> str:
        return f'{self._self_repr_str}(thread={self._thread!r})'

    @property
    def thread(self) -> threading.Thread | None:
        return self._thread

    @property
    def in_thread(self) -> bool:
        return threading.current_thread() is self._thread

    #

    class NotRunningError(Exception):
        pass

    def _check_running(self) -> None:
        if self._thread is None or not self._thread.is_alive():
            raise self.NotRunningError

    class AlreadyRunningError(Exception):
        pass

    def _check_not_running(self) -> None:
        if self._thread is not None:
            raise self.AlreadyRunningError

    #

    def start(self) -> None:
        with self._lock:
            self._check_not_running()

            self._pre_start()

            self._queue = queue.Queue()

            if su_cbs := self._startup_callbacks:
                def run_su_cbs() -> None:
                    # FIXME: stack exceptions lol
                    for cb in su_cbs:
                        cb()

                self._queue.put(DedicatedThreadExecutor._Call(run_su_cbs))

            del self._startup_callbacks

            self._thread = threading.Thread(
                target=self._main,
                name=f'{self._self_repr_str}._main',
                daemon=self._daemon,
            )
            self._thread.start()

    def _pre_start(self) -> None:
        """Overridable."""

    #

    @ta.final
    class _Stop:
        pass

    def stop(self) -> None:
        with self._lock:
            self._check_running()

            self._queue.put(DedicatedThreadExecutor._Stop())
            check.not_none(self._thread).join()

            while True:
                try:
                    o = self._queue.get_nowait()
                except queue.Empty:
                    break

                if isinstance(o, DedicatedThreadExecutor._Call):
                    o.fut.set_exception(self.NotRunningError())

                elif isinstance(o, DedicatedThreadExecutor._Stop):
                    pass

                else:
                    raise TypeError(o)

    #

    @ta.final
    @dc.dataclass(frozen=True)
    class _Call:
        fn: ta.Callable
        fut: cf.Future | None = None

    def submit(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> cf.Future[T]:
        fut: cf.Future = cf.Future()
        with self._lock:
            self._check_running()
            self._queue.put(DedicatedThreadExecutor._Call(functools.partial(fn, *args, **kwargs), fut))
        return fut

    def call(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        fut = self.submit(fn, *args, **kwargs)
        return fut.result()

    def call_gen(
            self,
            fn: ta.Callable[P, ta.Generator[O, I, R]],
            *args: P.args,
            **kwargs: P.kwargs,
    ) -> ta.Generator[O, I, R]:
        """Does not support `g.throw` - box inputs and outputs if that's needed."""

        iq: queue.Queue = queue.Queue()
        oq: queue.Queue = queue.Queue()

        def inner():
            try:
                g = fn(*args, **kwargs)

                try:
                    while True:
                        iv = oq.get()
                        if isinstance(iv, DedicatedThreadExecutor._Stop):
                            break

                        try:
                            iv = g.send(iv)
                        except StopIteration as e:  # noqa
                            return e.value

                        iq.put(iv)

                finally:
                    g.close()

            finally:
                iq.put(DedicatedThreadExecutor._Stop())

        oq.put(None)

        fut = self.submit(inner)

        try:
            while True:
                ov = iq.get()
                if isinstance(ov, DedicatedThreadExecutor._Stop):
                    break

                oq.put((yield ov))

        finally:
            oq.put(DedicatedThreadExecutor._Stop())

        return fut.result()

    #

    def add_startup_callback(self, cb: ta.Callable[[], None]) -> None:
        with self._lock:
            self._check_not_running()
            self._startup_callbacks.append(cb)

    #

    @ta.final
    @dc.dataclass(frozen=True, eq=False)
    class ShutdownCallback(lang.Final):
        fn: ta.Callable[[], None]

        def __repr__(self) -> str:
            return f'{self.__class__.__name__}@{id(self):x}({self.fn!r})'

    @ta.final
    @dc.dataclass(frozen=True)
    class _ShutdownCallbackTask:
        op: ta.Literal['add', 'remove']
        cb: 'DedicatedThreadExecutor.ShutdownCallback'
        fut: cf.Future

    @dc.dataclass()
    class ShutdownCallbackNotRegisteredError(Exception):
        cb: 'DedicatedThreadExecutor.ShutdownCallback'

    def _do_shutdown_callback_op(self, op: ta.Literal['add', 'remove'], cb: ShutdownCallback) -> None:
        fut: cf.Future = cf.Future()
        with self._lock:
            self._check_running()
            self._queue.put(DedicatedThreadExecutor._ShutdownCallbackTask(op, cb, fut))
        fut.result()

    def add_shutdown_callback(self, cb: ShutdownCallback | ta.Callable[[], None]) -> ShutdownCallback:
        if not isinstance(cb, DedicatedThreadExecutor.ShutdownCallback):
            cb = DedicatedThreadExecutor.ShutdownCallback(check.callable(cb))
        self._do_shutdown_callback_op('add', cb)
        return cb

    def remove_shutdown_callback(self, cb: ShutdownCallback) -> ShutdownCallback:
        check.isinstance(cb, DedicatedThreadExecutor.ShutdownCallback)
        self._do_shutdown_callback_op('remove', cb)
        return cb

    #

    _POLL_INTERVAL: ta.ClassVar[float] = 3

    @logs.exception_logging(log)
    def _main(self) -> None:
        try:
            log_pfx = f'{self._self_repr_str} native_id={threading.get_native_id():x}'
            log.debug(f'{log_pfx}: starting')

            #

            sd_cbs: set[DedicatedThreadExecutor.ShutdownCallback] = set()

            try:
                while True:
                    try:
                        o = self._queue.get(timeout=self._POLL_INTERVAL)
                    except queue.Empty:
                        continue

                    if isinstance(o, DedicatedThreadExecutor._Stop):
                        log.debug(f'{log_pfx}: stopping')
                        break

                    elif isinstance(o, DedicatedThreadExecutor._Call):
                        v: ta.Any = None
                        try:
                            v = o.fn()
                        except BaseException as e:  # noqa
                            if o.fut is not None:
                                o.fut.set_exception(e)
                        else:
                            if o.fut is not None:
                                o.fut.set_result(v)
                        del v

                    elif isinstance(o, DedicatedThreadExecutor._ShutdownCallbackTask):
                        try:
                            if o.op == 'add':
                                sd_cbs.add(o.cb)
                            elif o.op == 'remove':
                                try:
                                    sd_cbs.remove(o.cb)
                                except KeyError:
                                    raise self.ShutdownCallbackNotRegisteredError(o.cb)
                            else:
                                raise TypeError(o.op)  # noqa
                        except BaseException as e:  # noqa
                            o.fut.set_exception(e)
                        else:
                            o.fut.set_result(None)

                    else:
                        raise TypeError(o)  # noqa

                    del o

            finally:
                # FIXME: stack exceptions lol
                for cb in sd_cbs:
                    cb.fn()

        except BaseException as e:
            self._thread_exception = e
            raise

import abc
import concurrent.futures as cf
import functools
import queue
import threading
import typing as ta

from .. import check
from .. import lang


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


class ThreadRunnerClosedError(Exception):
    pass


class ThreadRunner(lang.Abstract):
    @abc.abstractmethod
    def run(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        raise NotImplementedError

    DEFAULT_CLOSE_TIMEOUT: ta.ClassVar[float | None] = 10.

    @abc.abstractmethod
    def close(self, *, wait: bool = False, timeout: float | None = DEFAULT_CLOSE_TIMEOUT) -> None:
        raise NotImplementedError

    #

    def __enter__(self) -> ta.Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close(wait=True)


##


class BaseThreadRunner(ThreadRunner, lang.Abstract):
    def __init__(
            self,
            *,
            name: str | None = None,
    ) -> None:
        super().__init__()

        self._name = name

        self._lock = threading.Lock()

        self._thread: threading.Thread | None = None
        self._closed = False

    @property
    def name(self) -> str | None:
        return self._name

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}({f"name={self._name!r}" if self._name is not None else ""})'

    class _Stop:
        pass

    def _ensure_thread(self) -> threading.Thread:
        if self._thread is None:
            t = threading.Thread(
                target=self._thread_main,
                name=f'{self!r}-worker',
                daemon=True,
            )
            t.start()
            self._thread = t
        return self._thread

    @abc.abstractmethod
    def _thread_main(self) -> None:
        raise NotImplementedError

    def run(self, fn: ta.Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        if args or kwargs:
            fn = functools.partial(fn, *args, **kwargs)

        return self._run(fn)

    @abc.abstractmethod
    def _run(self, fn: ta.Callable[[], T]) -> T:
        raise NotImplementedError


##


class SingleThreadRunner(BaseThreadRunner):
    def __init__(
            self,
            *,
            name: str | None = None,
    ) -> None:
        super().__init__(name=name)

        self._req_cv = threading.Condition(self._lock)
        self._res_cv = threading.Condition(self._lock)

        self._req: ta.Callable[[], ta.Any] | SingleThreadRunner._Stop | None = None
        self._res: SingleThreadRunner._Result | None = None

        self._run_lock = threading.Lock()

    class _Result(ta.NamedTuple):
        v: ta.Any
        e: BaseException | None

    def _thread_main(self) -> None:
        while True:
            with self._req_cv:
                while self._req is None:
                    self._req_cv.wait()

                check.none(self._res)
                req = check.not_none(self._req)
                self._req = None

            if isinstance(req, self._Stop):
                with self._res_cv:
                    self._res = self._Result(req, None)
                    self._res_cv.notify()
                return

            v: ta.Any = None
            e: BaseException | None = None
            try:
                v = req()  # type: ignore[operator]
            except BaseException as e2:  # noqa
                e = e2

            res = self._Result(v, e)
            del v, e

            with self._res_cv:
                check.none(self._res)
                self._res = res
                self._res_cv.notify()

    def _run(self, fn: ta.Callable[[], T]) -> T:
        with self._run_lock:
            with self._lock:
                check.state(not self._closed, ThreadRunnerClosedError)
                check.none(self._req)
                check.none(self._res)

                self._ensure_thread()

                self._req = fn
                self._req_cv.notify()

                while self._res is None:
                    self._res_cv.wait()

                res = check.not_none(self._res)

                self._res = None

        if res.e is not None:
            raise res.e
        return res.v

    def close(self, *, wait: bool = False, timeout: float | None = BaseThreadRunner.DEFAULT_CLOSE_TIMEOUT) -> None:
        with self._run_lock:
            t = self._thread
            if t is None:
                self._closed = True
                return

            with self._lock:
                if not self._closed:
                    self._closed = True
                    check.none(self._req)
                    check.none(self._res)

                    self._req = self._Stop()
                    self._req_cv.notify()

                    while self._res is None:
                        self._res_cv.wait()

                    res = check.not_none(self._res)
                    check.isinstance(res.v, self._Stop)

                    self._req = None
                    self._res = None

        if wait:
            t.join(timeout)
            if t.is_alive():
                raise TimeoutError


##


class QueueThreadRunner(BaseThreadRunner):
    def __init__(
            self,
            *,
            name: str | None = None,
    ) -> None:
        super().__init__(name=name)

        self._queue: queue.Queue[QueueThreadRunner._Call | QueueThreadRunner._Stop] = queue.Queue()

    class _Call(ta.NamedTuple):
        fn: ta.Callable[[], ta.Any]
        fut: cf.Future[ta.Any]

    def _thread_main(self) -> None:
        while True:
            o = self._queue.get()
            try:
                if isinstance(o, self._Stop):
                    return

                try:
                    o.fut.set_result(o.fn())
                except BaseException as e:  # noqa
                    o.fut.set_exception(e)

            finally:
                self._queue.task_done()

    def _run(self, fn: ta.Callable[[], T]) -> T:
        fut: cf.Future[T] = cf.Future()

        with self._lock:
            if self._closed:
                raise ThreadRunnerClosedError

            self._ensure_thread()
            self._queue.put(self._Call(
                fn,
                fut,
            ))

        return fut.result()

    @ta.override
    def close(self, *, wait: bool = False, timeout: float | None = BaseThreadRunner.DEFAULT_CLOSE_TIMEOUT) -> None:
        with self._lock:
            if self._closed:
                t = self._thread
            else:
                self._closed = True
                t = self._thread
                if t is not None:
                    self._queue.put(self._Stop())

        if t is None:
            return

        if wait:
            t.join(timeout)
            if t.is_alive():
                raise TimeoutError

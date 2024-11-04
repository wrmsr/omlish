# ruff: noqa: UP006 UP007
# @omlish-lite
"""
TODO:
 - implement stop lol
 - collective heartbeat monitoring - ThreadWorkerGroups
 - group -> 'context'? :|
  - shared stop_event?
"""
import abc
import dataclasses as dc
import threading
import time
import typing as ta

from omlish.lite.contextmanagers import ExitStacked
from omlish.lite.logs import log


T = ta.TypeVar('T')
ThreadWorkerT = ta.TypeVar('ThreadWorkerT', bound='ThreadWorker')


##


class ThreadWorker(ExitStacked, abc.ABC):
    def __init__(
            self,
            *,
            stop_event: ta.Optional[threading.Event] = None,
    ) -> None:
        super().__init__()

        if stop_event is None:
            stop_event = threading.Event()
        self._stop_event = stop_event

        self._lock = threading.RLock()
        self._thread: ta.Optional[threading.Thread] = None
        self._last_heartbeat: ta.Optional[float] = None

    #

    def __enter__(self: ThreadWorkerT) -> ThreadWorkerT:
        with self._lock:
            return super().__enter__()  # noqa

    #

    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    class Stopping(Exception):  # noqa
        pass

    #

    @property
    def last_heartbeat(self) -> ta.Optional[float]:
        return self._last_heartbeat

    def _heartbeat(
            self,
            *,
            no_stop_check: bool = False,
    ) -> None:
        self._last_heartbeat = time.time()

        if not no_stop_check and self.should_stop():
            log.info('Stopping: %s', self)
            raise ThreadWorker.Stopping

    #

    def has_started(self) -> bool:
        return self._thread is not None

    def is_alive(self) -> bool:
        return (thr := self._thread) is not None and thr.is_alive()

    def start(self) -> None:
        with self._lock:
            if self._thread is not None:
                raise RuntimeError('Thread already started: %r', self)

            thr = threading.Thread(target=self.__run)
            self._thread = thr
            thr.start()

    #

    def __run(self) -> None:
        try:
            self._run()
        except ThreadWorker.Stopping:
            log.exception('Thread worker stopped: %r', self)
        except Exception:  # noqa
            log.exception('Error in worker thread: %r', self)
            raise

    @abc.abstractmethod
    def _run(self) -> None:
        raise NotImplementedError

    #

    def stop(self) -> None:
        self._stop_event.set()

    def join(self, timeout: ta.Optional[float] = None) -> None:
        with self._lock:
            if self._thread is None:
                raise RuntimeError('Thread not started: %r', self)
            self._thread.join(timeout)


##


class ThreadWorkerGroup:
    @dc.dataclass()
    class State:
        worker: ThreadWorker

    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.RLock()
        self._states: ta.Dict[ThreadWorker, ThreadWorkerGroup.State] = {}

    def add(self, *workers: ThreadWorker) -> 'ThreadWorkerGroup':
        with self._lock:
            for w in workers:
                if w in self._states:
                    raise KeyError(w)
                self._states[w] = ThreadWorkerGroup.State(w)

        return self

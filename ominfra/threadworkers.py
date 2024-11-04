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
import contextlib
import dataclasses as dc
import threading
import time
import typing as ta

from omlish.lite.check import check_not_none
from omlish.lite.check import check_state
from omlish.lite.logs import log


T = ta.TypeVar('T')
ThreadWorkerT = ta.TypeVar('ThreadWorkerT', bound='ThreadWorker')


##


class ThreadWorker(abc.ABC):
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
        self._exit_stack: ta.Optional[contextlib.ExitStack] = None
        self._thread: ta.Optional[threading.Thread] = None
        self._last_heartbeat: ta.Optional[float] = None

    #

    def __enter__(self: ThreadWorkerT) -> ThreadWorkerT:
        with self._lock:
            check_state(self._exit_stack is None)
            es = self._exit_stack = contextlib.ExitStack()
            es.__enter__()
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if (es := self._exit_stack) is None:
            return None
        return es.__exit__(exc_type, exc_val, exc_tb)

    def _enter_context(self, cm: ta.ContextManager[T]) -> T:
        es = check_not_none(self._exit_stack)
        return es.enter_context(cm)

    #

    def should_stop(self) -> bool:
        return self._stop_event.is_set()

    @property
    def last_heartbeat(self) -> ta.Optional[float]:
        return self._last_heartbeat

    def _heartbeat(self) -> bool:
        self._last_heartbeat = time.time()

        if self.should_stop():
            log.info('Stopping: %s', self)
            return False

        return True

    #

    def has_started(self) -> bool:
        return self._thread is not None

    def is_alive(self) -> bool:
        return (thr := self._thread) is not None and thr.is_alive()

    def start(self) -> None:
        with self._lock:
            if self._thread is not None:
                raise RuntimeError('Thread already started: %r', self)

            thr = threading.Thread(target=self._run)
            self._thread = thr
            thr.start()

    @abc.abstractmethod
    def _run(self) -> None:
        raise NotImplementedError

    #

    def stop(self) -> None:
        raise NotImplementedError


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

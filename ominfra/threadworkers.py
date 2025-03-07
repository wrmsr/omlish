# ruff: noqa: UP006 UP007
# @omlish-lite
"""
FIXME:
 - group is racy af - meditate on has_started, etc

TODO:
 - overhaul stop lol
 - group -> 'context'? :|
  - shared stop_event?
"""
import abc
import contextlib
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
            worker_groups: ta.Optional[ta.Iterable['ThreadWorkerGroup']] = None,
    ) -> None:
        super().__init__()

        if stop_event is None:
            stop_event = threading.Event()
        self._stop_event = stop_event

        self._lock = threading.RLock()
        self._thread: ta.Optional[threading.Thread] = None
        self._last_heartbeat: ta.Optional[float] = None

        for g in worker_groups or []:
            g.add(self)

    #

    @contextlib.contextmanager
    def _exit_stacked_init_wrapper(self) -> ta.Iterator[None]:
        with self._lock:
            yield

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

            thr = threading.Thread(target=self.__thread_main)
            self._thread = thr
            thr.start()

    #

    def __thread_main(self) -> None:
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

    def join(
            self,
            timeout: ta.Optional[float] = None,
            *,
            unless_not_started: bool = False,
    ) -> None:
        with self._lock:
            if self._thread is None:
                if not unless_not_started:
                    raise RuntimeError('Thread not started: %r', self)
                return
            self._thread.join(timeout)


##


class ThreadWorkerGroup:
    @dc.dataclass()
    class _State:
        worker: ThreadWorker

        last_heartbeat: ta.Optional[float] = None

    def __init__(self) -> None:
        super().__init__()

        self._lock = threading.RLock()
        self._states: ta.Dict[ThreadWorker, ThreadWorkerGroup._State] = {}
        self._last_heartbeat_check: ta.Optional[float] = None

    #

    def add(self, *workers: ThreadWorker) -> 'ThreadWorkerGroup':
        with self._lock:
            for w in workers:
                if w in self._states:
                    raise KeyError(w)
                self._states[w] = ThreadWorkerGroup._State(w)

        return self

    #

    def start_all(self) -> None:
        thrs = list(self._states)
        with self._lock:
            for thr in thrs:
                if not thr.has_started():
                    thr.start()

    def stop_all(self) -> None:
        for w in reversed(list(self._states)):
            if w.has_started():
                w.stop()

    def join_all(self, timeout: ta.Optional[float] = None) -> None:
        for w in reversed(list(self._states)):
            if w.has_started():
                w.join(timeout, unless_not_started=True)

    #

    def get_dead(self) -> ta.List[ThreadWorker]:
        with self._lock:
            return [thr for thr in self._states if not thr.is_alive()]

    def check_heartbeats(self) -> ta.Dict[ThreadWorker, float]:
        with self._lock:
            dct: ta.Dict[ThreadWorker, float] = {}
            for thr, st in self._states.items():
                if not thr.has_started():
                    continue
                hb = thr.last_heartbeat
                if hb is None:
                    hb = time.time()
                st.last_heartbeat = hb
                dct[st.worker] = time.time() - hb
            self._last_heartbeat_check = time.time()
        return dct

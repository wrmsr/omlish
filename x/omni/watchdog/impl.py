import contextlib
import logging
import pprint
import sys
import threading
import time
import typing as ta
import weakref

from .. import check
from .. import configs as cfg
from .. import defs
from .report import ReporterImpl
from .types import Report
from .types import Reporter
from .types import Watch
from .types import Watchdog


log = logging.getLogger(__name__)


Meta = ta.Mapping[ta.Any, ta.Any]
FloatOrInt = ta.Union[float, int]


class Suspension(ta.NamedTuple):
    start_time: float
    duration: ta.Optional[FloatOrInt] = None
    frame: ta.Optional[ta.Any] = None


class WatchImpl(Watch):

    # __del__ can be called before __init__ completes so these need class-level defaults
    _entered = False
    _exited = False
    _parent = None
    _thread = None

    def __init__(
            self,
            parent: 'WatchdogImpl',
            thread: threading.Thread,
            obj: ta.Any,
            *,
            meta: ta.Optional[Meta] = None,
    ) -> None:
        super().__init__()

        self._parent = check.isinstance(parent, WatchdogImpl)
        self._thread = weakref.ref(check.isinstance(thread, threading.Thread), self._on_thread_die)
        self._obj = weakref.ref(check.not_none(obj), self._on_obj_die)
        self._meta = dict(meta or {})

        self._thread_ident = thread.ident
        self._obj_id = id(obj)

        self._entered = False
        self._exited = False

        self._start_time = time.time()
        self._last_checkpoint_time: ta.Optional[float] = None
        self._suspensions: ta.List[Suspension] = []

        self._parent._watches.add(self)
        try:
            thread_watches = self._parent._watch_sets_by_thread[thread]
        except KeyError:
            thread_watches = self._parent._watch_sets_by_thread[thread] = set()
        thread_watches.add(self)

    defs.getter('thread_ident', 'obj_id', 'age', 'staleness')
    defs.repr('thread', 'obj', 'age', 'staleness', 'suspended')

    @property
    def thread(self) -> ta.Optional[threading.Thread]:
        return self._thread()

    @property
    def obj(self) -> ta.Optional[ta.Any]:
        return self._obj()

    @property
    def active(self) -> bool:
        return self._entered and not self._exited

    @property
    def suspended(self) -> bool:
        return bool(self._suspensions)

    @property
    def age(self) -> float:
        return time.time() - self._start_time

    @property
    def last_time(self) -> float:
        return self._last_checkpoint_time if self._last_checkpoint_time is not None else self._start_time

    @property
    def staleness(self) -> float:
        return time.time() - self.last_time

    def _remove(self) -> bool:
        if self._parent is None:
            return False
        ret = False

        if self._thread is not None:
            thread = self._thread()
            if thread is not None:
                try:
                    thread_watches = self._parent._watch_sets_by_thread[thread]
                except KeyError:
                    pass
                else:
                    try:
                        thread_watches.remove(self)
                    except KeyError:
                        pass
                    else:
                        ret = True

        try:
            self._parent._watches.remove(self)
        except KeyError:
            pass
        else:
            ret = True

        return ret

    def __enter__(self) -> 'Watch':
        check.state(threading.current_thread() is self._thread())
        check.state(not self._entered and not self._exited)

        self._entered = True
        return self

    def __exit__(self, et, e, tb) -> None:
        check.state(threading.current_thread() is self._thread())
        check.state(self._entered and not self._exited)

        self._remove()

        self._exited = True
        return None

    def __del__(self):
        if self.active:
            log.warning(f'Leaked watch: {hex(id(self))}')
        self._remove()

    def checkpoint(self) -> None:
        check.state(self.active)
        check.state(threading.current_thread() is self._thread())

        self._last_checkpoint_time = time.time()

    @contextlib.contextmanager
    def suspend(self, duration: ta.Optional[FloatOrInt] = None) -> ta.ContextManager[None]:
        check.state(self.active)
        check.state(threading.current_thread() is self._thread())

        suspension = Suspension(time.time(), duration, sys._getframe())
        self._suspensions.append(suspension)
        self._last_checkpoint_time = time.time()
        try:
            yield
        finally:
            self._last_checkpoint_time = time.time()
            popped_suspension = self._suspensions.pop()
            check.state(popped_suspension is suspension)

    def _on_thread_die(self, ref: weakref.ref) -> None:
        if self.active:
            log.warning(f'Leaked watch (thread died): {hex(id(self))}')
        self._remove()

    def _on_obj_die(self, ref: weakref.ref) -> None:
        if self.active:
            log.warning(f'Leaked watch (object died): {hex(id(self))}')
        self._remove()


class WatchdogImpl(cfg.Configurable, Watchdog):

    class Config(cfg.Config):
        checker_interval: float = 0.25
        threshold: float = 2.
        report_throttle: float = 10.

    def __init__(
            self,
            *,
            shutdown_event: ta.Optional[threading.Event] = None,
            reporter: Reporter = ReporterImpl(),
            config: Config = Config(),
    ) -> None:
        super().__init__(config)

        if shutdown_event is None:
            shutdown_event = threading.Event()
        self._shutdown_event = check.isinstance(shutdown_event, threading.Event)
        self._reporter = check.isinstance(reporter, Reporter)

        self._checker: threading.Thread = threading.Thread(
            target=self._checker_proc,
            name='WatchdogChecker',
            daemon=True
        )

        self._watches: ta.Set[WatchImpl] = set()
        self._watch_sets_by_thread: ta.MutableMapping[threading.Thread, ta.Set[WatchImpl]] = weakref.WeakKeyDictionary()

        self._last_report_time: ta.Optional[float] = None

    def _do_lifecycle_start(self) -> None:
        self._checker.start()

    def _do_lifecycle_stop(self) -> None:
        self._shutdown_event.set()

        if self._checker.is_alive():
            self._checker.join(self._config.checker_interval * 3)
            if self._checker.is_alive():
                log.error('Failed to shutdown watchdog checker')

    def _checker_proc(self):
        try:
            log.info('Watchdog checker started')

            while not self._shutdown_event.wait(self._config.checker_interval):
                try:
                    self._check()
                except Exception:
                    log.exception('Watchdog checker exception')

            log.info('Watchdog checker shutdown')

        except Exception:
            log.exception('Watchdog checker exception')
            raise

    def watch(
            self,
            obj: ta.Any,
            *,
            thread: ta.Optional[threading.Thread] = None,
            meta: ta.Optional[Meta] = None,
    ) -> ta.ContextManager[Watch]:
        if thread is None:
            thread = threading.current_thread()

        return WatchImpl(
            self,
            thread,
            obj,
            meta=meta,
        )

    @property
    def current(self) -> ta.Set[Watch]:
        return set(self._watches)

    @property
    def thread_current(self) -> ta.Set[Watch]:
        current_thread = threading.current_thread()
        try:
            return set(self._watch_sets_by_thread[current_thread])
        except KeyError:
            return set()

    def _is_violation(self, watch: WatchImpl) -> bool:
        if watch.suspended:
            return False
        if watch.staleness < self._config.threshold:
            return False
        return True

    def _check(self) -> None:
        watches = set(self._watches)

        if log.isEnabledFor(logging.DEBUG):
            log.debug('\n' + pprint.pformat(watches))

        violations = {w for w in watches if self._is_violation(w)}

        if violations:
            if (
                    self._last_report_time is None or
                    (time.time() - self._last_report_time) >= self._config.report_throttle
            ):
                self._reporter.report_violations(self, watches, violations)
                self._last_report_time = time.time()

    def build_report(self) -> ta.Optional[Report]:
        watches = set(self._watches)
        violations = {w for w in watches if self._is_violation(w)}
        return self._reporter.build_report(
            self,
            watches=watches,
            violations=violations,
        )

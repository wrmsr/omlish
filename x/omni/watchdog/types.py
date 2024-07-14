import abc
import contextlib
import threading
import typing as ta

from .. import dataclasses as dc
from .. import lang
from .. import lifecycles as lc


Meta = ta.Mapping[ta.Any, ta.Any]
FloatOrInt = ta.Union[float, int]


class Watch(lang.Abstract):

    def __enter__(self) -> 'Watch':
        return self

    def __exit__(self, et, e, tb) -> None:
        return None

    @abc.abstractproperty
    def thread(self) -> ta.Optional[threading.Thread]:
        raise NotImplementedError

    @abc.abstractproperty
    def thread_ident(self) -> int:
        raise NotImplementedError

    @abc.abstractproperty
    def obj(self) -> ta.Optional[ta.Any]:
        raise NotImplementedError

    @abc.abstractproperty
    def obj_id(self) -> int:
        raise NotImplementedError

    @abc.abstractproperty
    def age(self) -> float:
        raise NotImplementedError

    @abc.abstractproperty
    def staleness(self) -> float:
        raise NotImplementedError

    @abc.abstractproperty
    def suspended(self) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def checkpoint(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def suspend(self, duration: ta.Optional[FloatOrInt] = None) -> ta.ContextManager[None]:
        raise NotImplementedError


class NopWatch(Watch):

    @property
    def thread(self) -> ta.Optional[threading.Thread]:
        return None

    @property
    def thread_ident(self) -> int:
        raise TypeError

    @property
    def obj(self) -> ta.Optional[ta.Any]:
        return None

    @property
    def obj_id(self) -> int:
        raise TypeError

    @property
    def age(self) -> float:
        return 0.

    @property
    def staleness(self) -> float:
        return 0.

    @property
    def suspended(self) -> bool:
        return False

    def checkpoint(self) -> None:
        pass

    @contextlib.contextmanager
    def suspend(self, duration: ta.Optional[FloatOrInt] = None) -> ta.Iterator[None]:
        yield


class Watchdog(lc.ContextManageableLifecycle, lang.Abstract):

    @lang.abstract
    def watch(
            self,
            obj: ta.Any,
            *,
            thread: ta.Optional[threading.Thread] = None,
            meta: ta.Optional[Meta] = None,
    ) -> ta.ContextManager[Watch]:
        raise NotImplementedError

    @abc.abstractproperty
    def current(self) -> ta.Set[Watch]:
        raise NotImplementedError

    @abc.abstractproperty
    def thread_current(self) -> ta.Set[Watch]:
        raise NotImplementedError

    def _do_for_thread_current(self, fn: ta.Callable[[Watch], None]) -> None:
        watches = self.thread_current
        for watch in watches:
            fn(watch)

    @contextlib.contextmanager
    def _enter_for_thread_current(self, fn: ta.Callable[[Watch], ta.ContextManager[None]]) -> ta.Iterator[None]:
        watches = self.thread_current
        if not watches:
            yield
        else:
            with contextlib.ExitStack() as es:
                for watch in watches:
                    es.enter_context(fn(watch))
                yield

    def checkpoint_thread_current(self) -> None:
        return self._do_for_thread_current(lambda w: w.checkpoint())

    def suspend_thread_current(self, duration: ta.Optional[FloatOrInt] = None) -> ta.ContextManager[None]:
        return self._enter_for_thread_current(lambda w: w.suspend(duration))

    @lang.abstract
    def build_report(self) -> ta.Optional['Report']:
        raise NotImplementedError


class NopWatchdog(Watchdog):

    def watch(
            self,
            obj: ta.Any,
            *,
            thread: ta.Optional[threading.Thread] = None,
            meta: ta.Optional[Meta] = None,
    ) -> ta.ContextManager[Watch]:
        return NopWatch()

    @property
    def current(self) -> ta.Set[Watch]:
        return set()

    @property
    def thread_current(self) -> ta.Set[Watch]:
        return set()

    def build_report(self) -> ta.Optional['Report']:
        return None


class WatchReport(dc.Pure):
    thread_ident: int
    obj_id: int
    obj_repr: ta.Optional[str]
    age: float
    staleness: float
    suspended: float


class ThreadReportFrame(dc.Pure):
    filename: str
    lineno: int
    name: ta.Optional[str]


class ThreadReport(dc.Pure):
    ident: int
    name: str
    stack: ta.List[ThreadReportFrame]


class Report(dc.Pure):
    violations: ta.List[WatchReport]
    others: ta.List[WatchReport]
    threads: ta.List[ThreadReport]
    meta: ta.Optional[ta.Mapping[str, ta.Any]] = None


class Reporter(lang.Abstract):

    def build_report(
            self,
            watchdog: Watchdog,
            *,
            watches: ta.Optional[ta.Set[Watch]] = None,
            violations: ta.Optional[ta.Set[Watch]] = None,
    ) -> ta.Optional[Report]:
        raise NotImplementedError

    def report_violations(
            self,
            watchdog: Watchdog,
            watches: ta.Set[Watch],
            violations: ta.Set[Watch],
    ) -> None:
        raise NotImplementedError


class NopReporter(Reporter):

    def build_report(
            self,
            watchdog: Watchdog,
            *,
            watches: ta.Optional[ta.Set[Watch]] = None,
            violations: ta.Optional[ta.Set[Watch]] = None,
    ) -> None:
        return None

    def report_violations(
            self,
            watchdog: Watchdog,
            watches: ta.Set[Watch],
            violations: ta.Set[Watch],
    ) -> None:
        pass

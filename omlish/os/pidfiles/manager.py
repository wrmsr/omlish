# ruff: noqa: UP007 UP045
# @omlish-lite
import contextlib
import os
import threading
import typing as ta

from ...lite.check import check
from ..forkhooks import ForkHook
from .pidfile import Pidfile


##


class _PidfileManager(ForkHook):
    """
    Manager for controlled inheritance of Pidfiles across forks in the presence of multiple threads. There is of course
    no safe or correct way to mix the use of fork and multiple active threads, and one should never write code which
    does so, but in the Real World one may still find oneself in such a situation outside of their control (such as when
    running under Pycharm's debugger which forces the use of forked multiprocessing).
    """

    _lock: ta.ClassVar[threading.Lock] = threading.Lock()
    _pidfile_threads: ta.ClassVar[ta.MutableMapping[Pidfile, threading.Thread]] = {}
    _num_kills: ta.ClassVar[int] = 0

    @classmethod
    def num_kills(cls) -> int:
        return cls._num_kills

    @classmethod
    def _after_fork_in_child(cls) -> None:
        with cls._lock:
            th = threading.current_thread()
            for pf, pf_th in list(cls._pidfile_threads.items()):
                if pf_th is not th:
                    pf.close()
                    del cls._pidfile_threads[pf]
                    cls._num_kills += 1

    @classmethod
    @contextlib.contextmanager
    def inheritable_pidfile_context(
            cls,
            path: str,
            *,
            inheritable: bool = True,
            **kwargs: ta.Any,
    ) -> ta.Iterator[Pidfile]:
        """
        A contextmanager for creating and managing a Pidfile which will only be inherited by forks of the calling /
        creating thread.
        """

        check.arg(inheritable)

        cls.install()

        pf = Pidfile(
            path,
            inheritable=False,
            **kwargs,
        )

        with cls._lock:
            cls._pidfile_threads[pf] = threading.current_thread()

        try:
            with pf:
                os.set_inheritable(check.not_none(pf.fileno()), True)
                yield pf

        finally:
            with cls._lock:
                del cls._pidfile_threads[pf]


def open_inheritable_pidfile(path: str, **kwargs: ta.Any) -> ta.ContextManager[Pidfile]:
    return _PidfileManager.inheritable_pidfile_context(path, **kwargs)  # noqa

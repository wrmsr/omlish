# ruff: noqa: UP007
# @omlish-lite
import contextlib
import os
import threading
import typing as ta
import weakref

from ...lite.check import check
from .pidfile import Pidfile


##


class _PidfileManager:
    """
    Manager for controlled inheritance of Pidfiles across forks in the presence of multiple threads. There is of course
    no safe or correct way to mix the use of fork and multiple active threads, and one should never write code which
    does so, but in the Real World one may still find oneself in such a situation outside of their control (such as when
    running under Pycharm's debugger which forces the use of forked multiprocessing).

    Not implemented as an instantiated class as there is no way to unregister at_fork listeners, and because Pidfiles
    may be pickled and there must be no possibility of accidentally unpickling and instantiating a new instance of the
    manager.
    """

    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    _lock: ta.ClassVar[threading.Lock] = threading.Lock()
    _installed: ta.ClassVar[bool] = False
    _pidfile_threads: ta.ClassVar[ta.MutableMapping[Pidfile, threading.Thread]] = weakref.WeakKeyDictionary()

    @classmethod
    def _before_fork(cls) -> None:
        cls._lock.acquire()

    @classmethod
    def _after_fork_in_parent(cls) -> None:
        cls._lock.release()

    @classmethod
    def _after_fork_in_child(cls) -> None:
        th = threading.current_thread()
        for pf, pf_th in list(cls._pidfile_threads.items()):
            if pf_th is not th:
                pf.close()
                del cls._pidfile_threads[pf]

        cls._lock.release()

    #

    @classmethod
    def _install(cls) -> None:
        check.state(not cls._installed)

        os.register_at_fork(
            before=cls._before_fork,
            after_in_parent=cls._after_fork_in_parent,
            after_in_child=cls._after_fork_in_child,
        )

        cls._installed = True

    @classmethod
    def install(cls) -> bool:
        with cls._lock:
            if cls._installed:
                return False

            cls._install()
            return True

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

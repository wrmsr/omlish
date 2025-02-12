# ruff: noqa: UP006 UP007
# @omlish-lite
import os
import threading
import typing as ta

from omlish.lite.check import check


##


class _ForkDepthTracker:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    _lock: ta.ClassVar[threading.Lock] = threading.Lock()
    _installed: ta.ClassVar[bool] = False
    _fork_depth: int = 0

    @classmethod
    def _after_fork_in_child(cls) -> None:
        with cls._lock:
            cls._fork_depth += 1

    #

    @classmethod
    def _install(cls) -> None:
        check.state(not cls._installed)

        os.register_at_fork(
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


    #

    @classmethod
    def get_fork_depth(cls) -> int:
        cls.install()

        return cls._fork_depth


def get_fork_depth() -> int:
    return _ForkDepthTracker.get_fork_depth()

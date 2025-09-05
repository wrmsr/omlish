# ruff: noqa: UP045
# @omlish-lite
import os.path
import sys
import threading
import typing as ta

from ..lite.abstract import Abstract


##


class LoggingContextInfo(Abstract):
    pass


##


@ta.final
class LoggingSourceFileInfo(LoggingContextInfo, ta.NamedTuple):
    file_name: str
    module: str

    @classmethod
    def build(cls, file_path: ta.Optional[str]) -> ta.Optional['LoggingSourceFileInfo']:
        if file_path is None:
            return None

        # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L331-L336  # noqa
        try:
            file_name = os.path.basename(file_path)
            module = os.path.splitext(file_name)[0]
        except (TypeError, ValueError, AttributeError):
            return None

        return cls(
            file_name,
            module,
        )


##


@ta.final
class LoggingThreadInfo(LoggingContextInfo, ta.NamedTuple):
    ident: int
    native_id: ta.Optional[int]
    name: str

    @classmethod
    def build(cls) -> 'LoggingThreadInfo':
        return cls(
            threading.get_ident(),
            threading.get_native_id() if hasattr(threading, 'get_native_id') else None,
            threading.current_thread().name,
        )


##


@ta.final
class LoggingProcessInfo(LoggingContextInfo, ta.NamedTuple):
    pid: int

    @classmethod
    def build(cls) -> 'LoggingProcessInfo':
        return cls(
            os.getpid(),
        )


##


@ta.final
class LoggingMultiprocessingInfo(LoggingContextInfo, ta.NamedTuple):
    process_name: str

    @classmethod
    def build(cls) -> ta.Optional['LoggingMultiprocessingInfo']:
        # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L355-L364  # noqa
        if (mp := sys.modules.get('multiprocessing')) is None:
            return None

        return cls(
            mp.current_process().name,
        )


##


@ta.final
class LoggingAsyncioTaskInfo(LoggingContextInfo, ta.NamedTuple):
    name: str

    @classmethod
    def build(cls) -> ta.Optional['LoggingAsyncioTaskInfo']:
        # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L372-L377  # noqa
        if (asyncio := sys.modules.get('asyncio')) is None:
            return None

        try:
            task = asyncio.current_task()
        except Exception:  # noqa
            return None

        return cls(
            task.get_name(),  # Always non-None
        )

# ruff: noqa: UP045
# @omlish-lite
import os.path
import sys
import threading
import typing as ta


##


def logging_context_info(cls):
    return cls


##


@logging_context_info
@ta.final
class LoggingSourceFileInfo(ta.NamedTuple):
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
            file_name=file_name,
            module=module,
        )


##


@logging_context_info
@ta.final
class LoggingThreadInfo(ta.NamedTuple):
    ident: int
    native_id: ta.Optional[int]
    name: str

    @classmethod
    def build(cls) -> 'LoggingThreadInfo':
        return cls(
            ident=threading.get_ident(),
            native_id=threading.get_native_id() if hasattr(threading, 'get_native_id') else None,
            name=threading.current_thread().name,
        )


##


@logging_context_info
@ta.final
class LoggingProcessInfo(ta.NamedTuple):
    pid: int

    @classmethod
    def build(cls) -> 'LoggingProcessInfo':
        return cls(
            pid=os.getpid(),
        )


##


@logging_context_info
@ta.final
class LoggingMultiprocessingInfo(ta.NamedTuple):
    process_name: str

    @classmethod
    def build(cls) -> ta.Optional['LoggingMultiprocessingInfo']:
        # https://github.com/python/cpython/blob/e709361fc87d0d9ab9c58033a0a7f2fef0ad43d2/Lib/logging/__init__.py#L355-L364  # noqa
        if (mp := sys.modules.get('multiprocessing')) is None:
            return None

        return cls(
            process_name=mp.current_process().name,
        )


##


@logging_context_info
@ta.final
class LoggingAsyncioTaskInfo(ta.NamedTuple):
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

        if task is None:
            return None

        return cls(
            name=task.get_name(),  # Always non-None
        )

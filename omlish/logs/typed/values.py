# ruff: noqa: UP007
# @omlish-lite
import logging
import os
import sys
import threading
import time
import typing as ta

from ...logs.infos import LoggingContextInfos
from ...logs.levels import LogLevel
from .types import ABSENT_TYPED_LOGGER_VALUE
from .types import AbsentTypedLoggerValue
from .types import DefaultTypedLoggerValue
from .types import TypedLoggerValue


##


class StandardTypedLoggerValues:
    def __new__(cls, *args, **kwargs):  # noqa
        raise TypeError

    #

    class TimeNs(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> float:
            return time.time()

    class Time(DefaultTypedLoggerValue[float]):
        _default_key = True
        _default_value = TypedLoggerValue.ContextLambda(
            lambda ctx: ctx[StandardTypedLoggerValues.TimeNs].map_absent(
                lambda tv: tv.v / 1e9,
            ),
        )

    #

    class Level(TypedLoggerValue[LogLevel]):
        pass

    class LevelName(DefaultTypedLoggerValue[str]):
        _default_key = 'level'
        _default_value = TypedLoggerValue.ContextLambda(
            lambda ctx: ctx[StandardTypedLoggerValues.Level].map_absent(
                lambda lvl: logging.getLevelName(lvl.v),
            ),
        )

    #

    class Msg(TypedLoggerValue[str]):
        _default_key = True

    #

    class Caller(TypedLoggerValue[LoggingContextInfos.Caller]):
        pass

    #

    class Tid(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> ta.Union[int, AbsentTypedLoggerValue]:
            if hasattr(threading, 'get_native_id'):
                return threading.get_native_id()
            else:
                return ABSENT_TYPED_LOGGER_VALUE

    class ThreadIdent(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> int:
            return threading.get_ident()

    class ThreadName(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> str:
            return threading.current_thread().name

    #

    class Pid(DefaultTypedLoggerValue[int]):
        @classmethod
        def _default_value(cls) -> int:
            return os.getpid()

    class ProcessName(DefaultTypedLoggerValue[str]):
        @classmethod
        def _default_value(cls) -> ta.Union[str, AbsentTypedLoggerValue]:
            if (mp := sys.modules.get('multiprocessing')) is None:
                return ABSENT_TYPED_LOGGER_VALUE

            # Errors may occur if multiprocessing has not finished loading yet - e.g. if a custom import hook causes
            # third-party code to run when multiprocessing calls import. See issue 8200 for an example
            try:
                return mp.current_process().name
            except Exception:  # noqa
                return ABSENT_TYPED_LOGGER_VALUE

    #

    class AsyncioTaskName(DefaultTypedLoggerValue[str]):
        @classmethod
        def _default_value(cls) -> ta.Union[str, AbsentTypedLoggerValue]:
            if (asyncio := sys.modules.get('asyncio')) is None:
                return ABSENT_TYPED_LOGGER_VALUE

            try:
                return asyncio.current_task().get_name()
            except Exception:  # noqa
                return ABSENT_TYPED_LOGGER_VALUE

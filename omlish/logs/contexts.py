# ruff: noqa: UP006 UP007 UP045 UP046
# @omlish-lite
import abc
import sys
import time
import types
import typing as ta

from ..lite.abstract import Abstract
from .callers import LoggingCaller
from .infos import LoggingAsyncioTaskInfo
from .infos import LoggingMultiprocessingInfo
from .infos import LoggingProcessInfo
from .infos import LoggingSourceFileInfo
from .infos import LoggingThreadInfo
from .levels import LogLevel
from .levels import NamedLogLevel
from .times import LoggingTimeFields


LoggingExcInfoTuple = ta.Tuple[ta.Type[BaseException], BaseException, ta.Optional[types.TracebackType]]  # ta.TypeAlias
LoggingExcInfo = ta.Union[BaseException, LoggingExcInfoTuple]  # ta.TypeAlias
LoggingExcInfoArg = ta.Union[LoggingExcInfo, bool, None]  # ta.TypeAlias


##


class LoggingContext(Abstract):
    @property
    @abc.abstractmethod
    def level(self) -> NamedLogLevel:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def time_ns(self) -> int:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def times(self) -> LoggingTimeFields:
        raise NotImplementedError

    #

    @property
    @abc.abstractmethod
    def exc_info(self) -> ta.Optional[LoggingExcInfo]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def exc_info_tuple(self) -> ta.Optional[LoggingExcInfoTuple]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def caller(self) -> ta.Optional[LoggingCaller]:
        raise NotImplementedError

    @abc.abstractmethod
    def source_file(self) -> ta.Optional[LoggingSourceFileInfo]:
        raise NotImplementedError

    #

    @abc.abstractmethod
    def thread(self) -> ta.Optional[LoggingThreadInfo]:
        raise NotImplementedError

    @abc.abstractmethod
    def process(self) -> ta.Optional[LoggingProcessInfo]:
        raise NotImplementedError

    @abc.abstractmethod
    def multiprocessing(self) -> ta.Optional[LoggingMultiprocessingInfo]:
        raise NotImplementedError

    @abc.abstractmethod
    def asyncio_task(self) -> ta.Optional[LoggingAsyncioTaskInfo]:
        raise NotImplementedError


##


class CaptureLoggingContext(LoggingContext, Abstract):
    @abc.abstractmethod
    def capture(self) -> None:
        """Must be cooperatively called only from the expected locations."""

        raise NotImplementedError


@ta.final
class CaptureLoggingContextImpl(CaptureLoggingContext):
    @ta.final
    class NOT_SET:  # noqa
        def __new__(cls, *args, **kwargs):  # noqa
            raise TypeError

    #

    def __init__(
            self,
            level: LogLevel,
            *,
            time_ns: ta.Optional[int] = None,

            exc_info: LoggingExcInfoArg = False,

            caller: ta.Union[LoggingCaller, ta.Type[NOT_SET], None] = NOT_SET,
            stack_offset: int = 0,
            stack_info: bool = False,
    ) -> None:
        self._level: NamedLogLevel = level if level.__class__ is NamedLogLevel else NamedLogLevel(level)  # type: ignore[assignment]  # noqa

        #

        if time_ns is None:
            time_ns = time.time_ns()
        self._time_ns: int = time_ns

        #

        if exc_info is True:
            sys_exc_info = sys.exc_info()
            if sys_exc_info[0] is not None:
                exc_info = sys_exc_info
            else:
                exc_info = None
        elif exc_info is False:
            exc_info = None

        if exc_info is not None:
            self._exc_info: ta.Optional[LoggingExcInfo] = exc_info
            if isinstance(exc_info, BaseException):
                self._exc_info_tuple: ta.Optional[LoggingExcInfoTuple] = (type(exc_info), exc_info, exc_info.__traceback__)  # noqa
            else:
                self._exc_info_tuple = exc_info
        else:
            self._exc_info = None
            self._exc_info_tuple = None

        #

        if caller is not CaptureLoggingContextImpl.NOT_SET:
            self._caller = caller  # type: ignore[assignment]
        else:
            self._stack_offset = stack_offset
            self._stack_info = stack_info

        #

        self._thread = LoggingThreadInfo.build()
        self._process = LoggingProcessInfo.build()
        self._multiprocessing = LoggingMultiprocessingInfo.build()
        self._asyncio_task = LoggingAsyncioTaskInfo.build()

    #

    @property
    def level(self) -> NamedLogLevel:
        return self._level

    #

    @property
    def time_ns(self) -> int:
        return self._time_ns

    _times: LoggingTimeFields

    @property
    def times(self) -> LoggingTimeFields:
        try:
            return self._times
        except AttributeError:
            pass

        times = self._times = LoggingTimeFields.build(self.time_ns)
        return times

    @property
    def exc_info(self) -> ta.Optional[LoggingExcInfo]:
        return self._exc_info

    @property
    def exc_info_tuple(self) -> ta.Optional[LoggingExcInfoTuple]:
        return self._exc_info_tuple

    #

    def inc_stack_offset(self, ofs: int = 1) -> 'LoggingContext':
        if hasattr(self, '_stack_offset'):
            self._stack_offset += ofs
        return self

    _caller: ta.Optional[LoggingCaller]

    def capture(self) -> None:
        """Must be cooperatively called only from the exact configured _stack_offset."""

        try:
            self._caller  # noqa
        except AttributeError:
            pass

        self._caller = LoggingCaller.find(
            self._stack_offset + 1,
            stack_info=self._stack_info,
        )

    def caller(self) -> ta.Optional[LoggingCaller]:
        try:
            return self._caller
        except AttributeError:
            return None

    _source_file: ta.Optional[LoggingSourceFileInfo]

    def source_file(self) -> ta.Optional[LoggingSourceFileInfo]:
        try:
            return self._source_file
        except AttributeError:
            pass

        if (caller := self.caller()) is None:
            return None

        src_file = self._source_file = LoggingSourceFileInfo.build(caller.file_path)
        return src_file

    #

    def thread(self) -> ta.Optional[LoggingThreadInfo]:
        return self._thread

    def process(self) -> ta.Optional[LoggingProcessInfo]:
        return self._process

    def multiprocessing(self) -> ta.Optional[LoggingMultiprocessingInfo]:
        return self._multiprocessing

    def asyncio_task(self) -> ta.Optional[LoggingAsyncioTaskInfo]:
        return self._asyncio_task

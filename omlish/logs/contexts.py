# ruff: noqa: UP006 UP007 UP045 UP046
# @omlish-lite
import sys
import time
import types
import typing as ta

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


@ta.final
class LoggingContext:
    level: NamedLogLevel

    time_ns: int

    exc_info: ta.Optional[LoggingExcInfo] = None
    exc_info_tuple: ta.Optional[LoggingExcInfoTuple] = None

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
        self.level = level if level.__class__ is NamedLogLevel else NamedLogLevel(level)  # type: ignore[assignment]

        #

        if time_ns is None:
            time_ns = time.time_ns()
        self.time_ns: int = time_ns

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
            self.exc_info = exc_info
            if isinstance(exc_info, BaseException):
                self.exc_info_tuple = (type(exc_info), exc_info, exc_info.__traceback__)
            else:
                self.exc_info_tuple = exc_info

        #

        if caller is not LoggingContext.NOT_SET:
            self._caller = caller  # type: ignore[assignment]
        else:
            self._stack_offset = stack_offset
            self._stack_info = stack_info

        #

        self.thread = LoggingThreadInfo.build()
        self.process = LoggingProcessInfo.build()
        self.multiprocessing = LoggingMultiprocessingInfo.build()
        self.asyncio_task = LoggingAsyncioTaskInfo.build()

    #

    _times: LoggingTimeFields

    @property
    def times(self) -> LoggingTimeFields:
        try:
            return self._times
        except AttributeError:
            pass

        times = self._times = LoggingTimeFields.build(self.time_ns)
        return times

    #

    def inc_stack_offset(self, ofs: int = 1) -> 'LoggingContext':
        if hasattr(self, '_stack_offset'):
            self._stack_offset += ofs
        return self

    _caller: ta.Optional[LoggingCaller]

    def build_caller(self) -> ta.Optional[LoggingCaller]:
        """Must be cooperatively called only from the exact configured _stack_offset."""

        try:
            return self._caller
        except AttributeError:
            pass

        caller = self._caller = LoggingCaller.find(
            self._stack_offset + 1,
            stack_info=self._stack_info,
        )
        return caller

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

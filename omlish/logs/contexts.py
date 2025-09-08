# ruff: noqa: UP006 UP007 UP045 UP046
# @omlish-lite
import abc
import time
import typing as ta

from ..lite.abstract import Abstract
from .infos import LoggingContextInfo
from .infos import LoggingContextInfos
from .infos import LoggingExcInfoArg
from .levels import LogLevel


LoggingContextInfoT = ta.TypeVar('LoggingContextInfoT', bound=LoggingContextInfo)


##


class LoggingContext(Abstract):
    @abc.abstractmethod
    def __getitem__(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        raise NotImplementedError


##


class CaptureLoggingContext(LoggingContext, Abstract):
    class AlreadyCapturedError(Exception):
        pass

    class NotCapturedError(Exception):
        pass

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

            caller: ta.Union[LoggingContextInfos.Caller, ta.Type[NOT_SET], None] = NOT_SET,
            stack_offset: int = 0,
            stack_info: bool = False,
    ) -> None:
        # TODO: Name, Msg, Extra

        if time_ns is None:
            time_ns = time.time_ns()

        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {
            LoggingContextInfos.Level: LoggingContextInfos.Level.build(level),
            LoggingContextInfos.Time: LoggingContextInfos.Time.build(time_ns),
            LoggingContextInfos.Exc: LoggingContextInfos.Exc.build(exc_info),
        }

        if caller is not CaptureLoggingContextImpl.NOT_SET:
            self._infos[LoggingContextInfos.Caller] = caller
        else:
            self._stack_offset = stack_offset
            self._stack_info = stack_info

    def __getitem__(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)

    ##

    _stack_offset: int
    _stack_info: bool

    def inc_stack_offset(self, ofs: int = 1) -> 'CaptureLoggingContext':
        if hasattr(self, '_stack_offset'):
            self._stack_offset += ofs
        return self

    _has_captured: bool = False

    def capture(self) -> None:
        if self._has_captured:
            raise CaptureLoggingContextImpl.AlreadyCapturedError
        self._has_captured = True

        if LoggingContextInfos.Caller not in self._infos:
            self._infos[LoggingContextInfos.Caller] = LoggingContextInfos.Caller.build(
                self._stack_offset + 1,
                stack_info=self._stack_info,
            )

        if (caller := self[LoggingContextInfos.Caller]) is not None:
            self._infos[LoggingContextInfos.SourceFile] = LoggingContextInfos.SourceFile.build(caller.file_path)

        self._infos.update({
            LoggingContextInfos.Thread: LoggingContextInfos.Thread.build(),
            LoggingContextInfos.Process: LoggingContextInfos.Process.build(),
            LoggingContextInfos.Multiprocessing: LoggingContextInfos.Multiprocessing.build(),
            LoggingContextInfos.AsyncioTask: LoggingContextInfos.AsyncioTask.build(),
        })

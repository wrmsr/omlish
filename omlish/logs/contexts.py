# ruff: noqa: UP006 UP007 UP045 UP046
# @omlish-lite
import abc
import time
import typing as ta

from ..lite.abstract import Abstract
from .infos import LoggingContextInfo
from .infos import LoggingContextInfos
from .infos import LoggingExcInfoArg
from .infos import LoggingMsgFn
from .levels import LogLevel


LoggingContextInfoT = ta.TypeVar('LoggingContextInfoT', bound=LoggingContextInfo)


##


class LoggingContext(Abstract):
    @abc.abstractmethod
    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        raise NotImplementedError

    @ta.final
    def __getitem__(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self.get_info(ty)

    @ta.final
    def must_get_info(self, ty: ta.Type[LoggingContextInfoT]) -> LoggingContextInfoT:
        if (info := self.get_info(ty)) is None:
            raise TypeError(f'LoggingContextInfo absent: {ty}')
        return info


@ta.final
class SimpleLoggingContext(LoggingContext):
    def __init__(self, *infos: LoggingContextInfo) -> None:
        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {type(i): i for i in infos}

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)


##


class CaptureLoggingContext(LoggingContext, Abstract):
    @abc.abstractmethod
    def set_basic(
            self,
            name: str,

            msg: ta.Union[str, tuple, LoggingMsgFn],
            args: tuple,
    ) -> 'CaptureLoggingContext':
        raise NotImplementedError

    #

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
        if time_ns is None:
            time_ns = time.time_ns()

        # Done early to not trample on sys.exc_info()
        exc = LoggingContextInfos.Exc.build(exc_info)

        self._infos: ta.Dict[ta.Type[LoggingContextInfo], LoggingContextInfo] = {}
        self._set_info(
            LoggingContextInfos.Level.build(level),
            exc,
            LoggingContextInfos.Time.build(time_ns),
        )

        if caller is not CaptureLoggingContextImpl.NOT_SET:
            self._infos[LoggingContextInfos.Caller] = caller
        else:
            self._stack_offset = stack_offset
            self._stack_info = stack_info

    def _set_info(self, *infos: ta.Optional[LoggingContextInfo]) -> 'CaptureLoggingContextImpl':
        for info in infos:
            if info is not None:
                self._infos[type(info)] = info
        return self

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self._infos.get(ty)

    ##

    def set_basic(
            self,
            name: str,

            msg: ta.Union[str, tuple, LoggingMsgFn],
            args: tuple,
    ) -> 'CaptureLoggingContextImpl':
        return self._set_info(
            LoggingContextInfos.Name(name),
            LoggingContextInfos.Msg.build(msg, *args),
        )

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
            self._set_info(LoggingContextInfos.Caller.build(
                self._stack_offset + 1,
                stack_info=self._stack_info,
            ))

        if (caller := self[LoggingContextInfos.Caller]) is not None:
            self._set_info(LoggingContextInfos.SourceFile.build(
                caller.file_path,
            ))

        self._set_info(
            LoggingContextInfos.Thread.build(),
            LoggingContextInfos.Process.build(),
            LoggingContextInfos.Multiprocessing.build(),
            LoggingContextInfos.AsyncioTask.build(),
        )

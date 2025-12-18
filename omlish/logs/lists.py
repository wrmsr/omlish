# ruff: noqa: N802 UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from ..lite.abstract import Abstract
from ..lite.check import check
from .base import AnyLogger
from .base import AsyncLogger
from .base import CaptureLoggingContext
from .base import Logger
from .base import LoggingMsgFn
from .contexts import CaptureLoggingContextImpl
from .infos import LoggingContextInfo
from .infos import LoggingContextInfos
from .levels import LogLevel
from .levels import NamedLogLevel


T = ta.TypeVar('T')

LoggingContextInfoT = ta.TypeVar('LoggingContextInfoT', bound=LoggingContextInfo)


##


@dc.dataclass(frozen=True)
class ListLoggerEntry:
    infos: ta.Mapping[ta.Type[LoggingContextInfo], LoggingContextInfo]

    def get_info(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self.infos.get(ty)

    @ta.final
    def __getitem__(self, ty: ta.Type[LoggingContextInfoT]) -> ta.Optional[LoggingContextInfoT]:
        return self.get_info(ty)

    def must_get_info(self, ty: ta.Type[LoggingContextInfoT]) -> LoggingContextInfoT:
        return check.not_none(self.get_info(ty))


class AnyListLogger(AnyLogger[T], Abstract):
    def __init__(
            self,
            *,
            name: ta.Optional[str] = None,
            level: LogLevel = NamedLogLevel.NOTSET,
    ) -> None:
        super().__init__()

        if name is None:
            name = f'{type(self).__name__}@{id(self):x}'
        self._name = name
        self._level = level

        self._entries: ta.List[ListLoggerEntry] = []

    @property
    def name(self) -> str:
        return self._name

    @property
    def entries(self) -> ta.List[ListLoggerEntry]:
        """Intentionally mutable."""

        return self._entries

    def set_level(self, level: LogLevel) -> None:
        self._level = level

    def get_effective_level(self) -> LogLevel:
        return self._level

    def _add_entry(
            self,
            ctx: CaptureLoggingContextImpl,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
    ) -> None:
        if not self.is_enabled_for(ctx.must_get_info(LoggingContextInfos.Level).level):
            return

        ctx.set_basic(
            name=self._name,

            msg=msg,
            args=args,
        )

        ctx.capture()

        self._entries.append(ListLoggerEntry(ctx.get_infos()))


class ListLogger(AnyListLogger[None], Logger):
    def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        self._add_entry(
            check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
            msg,
            *args,
            **kwargs,
        )


class ListAsyncLogger(AnyListLogger[ta.Awaitable[None]], AsyncLogger):
    async def _log(
            self,
            ctx: CaptureLoggingContext,
            msg: ta.Union[str, tuple, LoggingMsgFn],
            *args: ta.Any,
            **kwargs: ta.Any,
    ) -> None:
        self._add_entry(
            check.isinstance(ctx, CaptureLoggingContextImpl).inc_stack_offset(),
            msg,
            *args,
            **kwargs,
        )

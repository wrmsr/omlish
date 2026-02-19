# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.namespaces import NamespaceClass

from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext


F = ta.TypeVar('F')
T = ta.TypeVar('T')

ChannelPipelineHandlerFn = ta.Callable[['ChannelPipelineHandlerContext', F], T]  # ta.TypeAlias


##


class ChannelPipelineHandlerFns(NamespaceClass):
    @dc.dataclass(frozen=True)
    class NoContext(ta.Generic[F, T]):
        fn: ta.Callable[[F], T]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, obj: F) -> T:
            return self.fn(obj)

    @classmethod
    def no_context(cls, fn: ta.Callable[[F], T]) -> ChannelPipelineHandlerFn[F, T]:
        return cls.NoContext(fn=fn)

    #

    @dc.dataclass(frozen=True)
    class Isinstance:
        ty: ta.Union[type, ta.Tuple[type, ...]]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.ty!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> bool:
            return isinstance(msg, self.ty)

    @classmethod
    def isinstance(cls, ty: ta.Union[type, ta.Tuple[type, ...]]) -> ChannelPipelineHandlerFn[ta.Any, bool]:
        return cls.Isinstance(ty=ty)


##


class FnChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    @classmethod
    def of(
            cls,
            *,
            inbound: ta.Optional[ChannelPipelineHandlerFn[ta.Any, None]] = None,
            outbound: ta.Optional[ChannelPipelineHandlerFn[ta.Any, None]] = None,
    ) -> ChannelPipelineHandler:
        if inbound is not None and outbound is not None:
            return DuplexFnChannelPipelineHandler(inbound=inbound, outbound=outbound)
        elif inbound is not None:
            return InboundFnChannelPipelineHandler(inbound)
        elif outbound is not None:
            return OutboundFnChannelPipelineHandler(outbound)
        else:
            raise ValueError('At least one of inbound or outbound must be specified')


class InboundFnChannelPipelineHandler(FnChannelPipelineHandler):
    def __init__(self, inbound: ChannelPipelineHandlerFn[ta.Any, None]) -> None:
        super().__init__()

        self._inbound = inbound

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}({self._inbound!r})'

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._inbound(ctx, msg)


class OutboundFnChannelPipelineHandler(FnChannelPipelineHandler):
    def __init__(self, outbound: ChannelPipelineHandlerFn[ta.Any, None]) -> None:
        super().__init__()

        self._outbound = outbound

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}({self._outbound!r})'

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._outbound(ctx, msg)


class DuplexFnChannelPipelineHandler(FnChannelPipelineHandler):
    def __init__(
            self,
            *,
            inbound: ChannelPipelineHandlerFn[ta.Any, None],
            outbound: ChannelPipelineHandlerFn[ta.Any, None],
    ) -> None:
        super().__init__()

        self._inbound = inbound
        self._outbound = outbound

    def __repr__(self) -> str:
        return f'{type(self).__name__}@{id(self):x}(inbound={self._inbound!r}, outbound={self._outbound!r})'

    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._inbound(ctx, msg)

    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        self._outbound(ctx, msg)

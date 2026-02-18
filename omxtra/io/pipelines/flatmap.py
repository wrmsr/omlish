# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import functools
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.namespaces import NamespaceClass

from .core import ChannelPipelineDirectionOrDuplex
from .core import ChannelPipelineHandler
from .core import ChannelPipelineHandlerContext


##


FlatMapChannelPipelineHandlerFn = ta.Callable[  # ta.TypeAlias  # omlish-amalg-typing-no-move
    [ChannelPipelineHandlerContext, ta.Any],
    ta.Iterable[ta.Any],
]


class FlatMapChannelPipelineHandlerFns(NamespaceClass):
    @dc.dataclass(frozen=True)
    class Filter:
        pred: ta.Callable[[ChannelPipelineHandlerContext, ta.Any], bool]
        fn: FlatMapChannelPipelineHandlerFn

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.pred(ctx, msg):
                yield from self.fn(ctx, msg)

    @classmethod
    def filter(
            cls,
            pred: ta.Callable[[ChannelPipelineHandlerContext, ta.Any], bool],
            fn: FlatMapChannelPipelineHandlerFn,
    ) -> FlatMapChannelPipelineHandlerFn:
        return cls.Filter(pred, fn)

    #

    @dc.dataclass(frozen=True)
    class Concat:
        fns: ta.Sequence[FlatMapChannelPipelineHandlerFn]

        def __post_init__(self) -> None:
            check.not_empty(self.fns)

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            for fn in self.fns:
                yield from fn(ctx, msg)

    @classmethod
    def concat(cls, *fns: FlatMapChannelPipelineHandlerFn) -> FlatMapChannelPipelineHandlerFn:
        return cls.Concat(fns)

    #

    @dc.dataclass(frozen=True)
    class Compose:
        fns: ta.Sequence[FlatMapChannelPipelineHandlerFn]

        _fn: FlatMapChannelPipelineHandlerFn = dc.field(init=False, repr=False)

        def __post_init__(self) -> None:
            check.not_empty(self.fns)

            def compose(cur, nxt, ctx, msg):
                for x in cur(ctx, msg):
                    yield from nxt(ctx, x)

            xf: ta.Any = lambda ctx, msg: (msg,)  # noqa
            for cf in reversed(self.fns):
                xf = functools.partial(compose, cf, xf)

            object.__setattr__(self, '_fn', xf)

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return self._fn(ctx, msg)

    @classmethod
    def compose(cls, *fns: FlatMapChannelPipelineHandlerFn) -> FlatMapChannelPipelineHandlerFn:
        return cls.Compose(fns)

    #

    @dc.dataclass(frozen=True)
    class Emit:
        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            ctx.emit(msg)
            return (msg,)

    @classmethod
    def emit(cls) -> FlatMapChannelPipelineHandlerFn:
        return cls.Emit()

    #

    @dc.dataclass(frozen=True)
    class Drop:
        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return ()

    @classmethod
    def drop(cls) -> FlatMapChannelPipelineHandlerFn:
        return cls.Drop()


#


class FlatMapChannelPipelineHandler(ChannelPipelineHandler, Abstract):
    def __init__(
            self,
            fn: FlatMapChannelPipelineHandlerFn,
            desc: ta.Optional[str] = None,
    ) -> None:
        super().__init__()

        self._fn = check.callable(fn)
        self._desc = desc

    _fn: FlatMapChannelPipelineHandlerFn

    def __repr__(self) -> str:
        return (
            f'{self.__class__.__name__}@{id(self):x}'
            f'({self._fn!r}{f", {self._desc!r}" if self._desc is not None else ""})'
        )


#


class InboundFlatMapPipelineHandler(FlatMapChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_in(x)


class OutboundFlatMapPipelineHandler(FlatMapChannelPipelineHandler):
    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_out(x)


class DuplexFlatMapPipelineHandler(
    InboundFlatMapPipelineHandler,
    OutboundFlatMapPipelineHandler,
):
    pass


#


class FlatMapChannelPipelineHandlers(NamespaceClass):
    _CLS_BY_DIRECTION: ta.ClassVar[ta.Mapping[ChannelPipelineDirectionOrDuplex, ta.Type[FlatMapChannelPipelineHandler]]] = {  # noqa
        'inbound': InboundFlatMapPipelineHandler,
        'outbound': OutboundFlatMapPipelineHandler,
        'duplex': DuplexFlatMapPipelineHandler,
    }

    @classmethod
    def new(
            cls,
            direction: ChannelPipelineDirectionOrDuplex,
            fn: FlatMapChannelPipelineHandlerFn,
            desc: ta.Optional[str] = None,
            *,
            _default_desc: ta.Optional[str] = None,
    ) -> ChannelPipelineHandler:
        h_cls = cls._CLS_BY_DIRECTION[direction]
        return h_cls(fn, desc if desc is not None else _default_desc)

    #

    @classmethod
    def emit_and_drop(
            cls,
            direction: ChannelPipelineDirectionOrDuplex,
            desc: ta.Optional[str] = None,
    ) -> ChannelPipelineHandler:
        return cls.new(
            direction,
            FlatMapChannelPipelineHandlerFns.compose(
                FlatMapChannelPipelineHandlerFns.emit(),
                FlatMapChannelPipelineHandlerFns.drop(),
            ),
            desc,
            _default_desc='emit_and_drop',
        )

# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import functools
import typing as ta

from omlish.lite.abstract import Abstract
from omlish.lite.check import check
from omlish.lite.namespaces import NamespaceClass

from ..core import ChannelPipelineDirectionOrDuplex
from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineHandlerFn


##


FlatMapChannelPipelineHandlerFn = ChannelPipelineHandlerFn[ta.Any, ta.Iterable[ta.Any]]  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


class FlatMapChannelPipelineHandlerFns(NamespaceClass):
    @dc.dataclass(frozen=True)
    class Filter:
        pred: ChannelPipelineHandlerFn[ta.Any, bool]
        fn: FlatMapChannelPipelineHandlerFn
        else_fn: ta.Optional[FlatMapChannelPipelineHandlerFn] = None

        def __repr__(self) -> str:
            return (
                f'{type(self).__name__}('
                f'{self.pred!r}'
                f', {self.fn!r}, '
                f'{f", else_fn={self.else_fn!r}" if self.else_fn is not None else ""}'
                f')'
            )

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.pred(ctx, msg):
                yield from self.fn(ctx, msg)
            elif (ef := self.else_fn) is not None:
                yield from ef(ctx, msg)
            else:
                yield msg

    @classmethod
    def filter(
            cls,
            pred: ChannelPipelineHandlerFn[ta.Any, bool],
            fn: FlatMapChannelPipelineHandlerFn,
            else_fn: ta.Optional[FlatMapChannelPipelineHandlerFn] = None,
    ) -> FlatMapChannelPipelineHandlerFn:
        return cls.Filter(pred, fn, else_fn)

    #

    @dc.dataclass(frozen=True)
    class Concat:
        fns: ta.Sequence[FlatMapChannelPipelineHandlerFn]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

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

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        _fn: FlatMapChannelPipelineHandlerFn = dc.field(init=False)

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
    class Map:
        fn: ChannelPipelineHandlerFn[ta.Any, ta.Any]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return (self.fn(ctx, msg),)

    @classmethod
    def map(cls, fn: ChannelPipelineHandlerFn[ta.Any, ta.Any]) -> FlatMapChannelPipelineHandlerFn:
        return cls.Map(fn)

    #

    @dc.dataclass(frozen=True)
    class Apply:
        fn: ChannelPipelineHandlerFn[ta.Any, None]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            self.fn(ctx, msg)
            return (msg,)

    @classmethod
    def apply(cls, fn: ChannelPipelineHandlerFn[ta.Any, None]) -> FlatMapChannelPipelineHandlerFn:
        return cls.Apply(fn)

    ##

    @dc.dataclass(frozen=True)
    class FeedOut:
        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            ctx.feed_out(msg)
            return (msg,)

    @classmethod
    def feed_out(cls) -> FlatMapChannelPipelineHandlerFn:
        return cls.FeedOut()

    #

    @dc.dataclass(frozen=True)
    class Drop:
        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

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
    ) -> None:
        super().__init__()

        self._fn = check.callable(fn)

    _fn: FlatMapChannelPipelineHandlerFn

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._fn!r})'


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
    ) -> ChannelPipelineHandler:
        h_cls = cls._CLS_BY_DIRECTION[direction]
        return h_cls(fn)

    #

    @classmethod
    def feed_out_and_drop(
            cls,
            *,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> ChannelPipelineHandler:
        fn = FlatMapChannelPipelineHandlerFns.compose(
            FlatMapChannelPipelineHandlerFns.feed_out(),
            FlatMapChannelPipelineHandlerFns.drop(),
        )

        if filter is not None:
            fn = FlatMapChannelPipelineHandlerFns.filter(filter, fn)

        return cls.new('inbound', fn)

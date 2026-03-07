# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import functools
import typing as ta

from ....lite.abstract import Abstract
from ....lite.check import check
from ....lite.namespaces import NamespaceClass
from ..core import ChannelPipelineDirectionOrDuplex
from ..core import ChannelPipelineHandler
from ..core import ChannelPipelineHandlerContext
from ..core import ChannelPipelineHandlerFn
from ..core import ChannelPipelineMessages
from .fns import ChannelPipelineHandlerFns


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
                f', {self.fn!r}'
                f'{f", else_fn={self.else_fn!r}" if self.else_fn is not None else ""}'
                f')'
            )

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.pred(ctx, msg):
                yield from self.fn(ctx, msg)
            elif (ef := self.else_fn) is not None:
                yield from ef(ctx, msg)  # noqa
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

    @classmethod
    def filter_type(
            cls,
            ty: ta.Union[type, ta.Tuple[type, ...]],
            fn: FlatMapChannelPipelineHandlerFn,
            else_fn: ta.Optional[FlatMapChannelPipelineHandlerFn] = None,
    ) -> FlatMapChannelPipelineHandlerFn:
        return cls.filter(ChannelPipelineHandlerFns.isinstance(ty), fn, else_fn)

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

    #

    @dc.dataclass(frozen=True)
    class Feed:
        direction: ChannelPipelineDirectionOrDuplex

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.direction!r})'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.direction == 'inbound':
                ctx.feed_in(msg)
            elif self.direction == 'outbound':
                ctx.feed_out(msg)
            else:
                raise RuntimeError(f'Unknown direction: {self.direction!r}')
            return (msg,)

    @classmethod
    def feed_in(cls) -> FlatMapChannelPipelineHandlerFn:
        return cls.Feed('inbound')

    @classmethod
    def feed_out(cls) -> FlatMapChannelPipelineHandlerFn:
        return cls.Feed('outbound')

    #

    @dc.dataclass(frozen=True)
    class Inject:
        before: ta.Union[ta.Sequence[ta.Any], ta.Callable[[], ta.Sequence[ta.Any]], None] = None
        after: ta.Union[ta.Sequence[ta.Any], ta.Callable[[], ta.Sequence[ta.Any]], None] = None

        def __repr__(self) -> str:
            return ''.join([
                f'{type(self).__name__}(',
                *', '.join([
                    *([f'before={self.before!r}'] if self.before is not None else []),
                    *([f'after={self.after!r}'] if self.after is not None else []),
                ]),
                ')',
            ])

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            out: ta.List[ta.Any] = []
            if (before := self.before) is not None:
                out.extend(before() if callable(before) else before)  # noqa
            out.append(msg)
            if (after := self.after) is not None:
                out.extend(after() if callable(after) else after)  # noqa
            return out

    @classmethod
    def inject(
            cls,
            *,
            before: ta.Union[ta.Sequence[ta.Any], ta.Callable[[], ta.Sequence[ta.Any]], None] = None,
            after: ta.Union[ta.Sequence[ta.Any], ta.Callable[[], ta.Sequence[ta.Any]], None] = None,
    ) -> FlatMapChannelPipelineHandlerFn:
        return cls.Inject(
            before=before,
            after=after,
        )

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

    @dc.dataclass(frozen=True)
    class Nop:
        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def __call__(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return (msg,)

    @classmethod
    def nop(cls) -> FlatMapChannelPipelineHandlerFn:
        return cls.Nop()


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


class InboundFlatMapChannelPipelineHandler(FlatMapChannelPipelineHandler):
    def inbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_in(x)


class OutboundFlatMapChannelPipelineHandler(FlatMapChannelPipelineHandler):
    def outbound(self, ctx: ChannelPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_out(x)


class DuplexFlatMapChannelPipelineHandler(
    InboundFlatMapChannelPipelineHandler,
    OutboundFlatMapChannelPipelineHandler,
):
    pass


#


class FlatMapChannelPipelineHandlers(NamespaceClass):
    _CLS_BY_DIRECTION: ta.ClassVar[ta.Mapping[ChannelPipelineDirectionOrDuplex, ta.Type[FlatMapChannelPipelineHandler]]] = {  # noqa
        'inbound': InboundFlatMapChannelPipelineHandler,
        'outbound': OutboundFlatMapChannelPipelineHandler,
        'duplex': DuplexFlatMapChannelPipelineHandler,
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

    _NOT_MUST_PROPAGATE: ta.ClassVar[ChannelPipelineHandlerFn[ta.Any, bool]] = ChannelPipelineHandlerFns.not_(
        ChannelPipelineHandlerFns.isinstance(ChannelPipelineMessages.MustPropagate),
    )

    @classmethod
    def _add_drop_filters(
            cls,
            fn: FlatMapChannelPipelineHandlerFn,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> FlatMapChannelPipelineHandlerFn:
        if filter is not None:
            fn = FlatMapChannelPipelineHandlerFns.filter(filter, fn)

        if filter_type is not None:
            fn = FlatMapChannelPipelineHandlerFns.filter_type(filter_type, fn)

        fn = FlatMapChannelPipelineHandlerFns.filter(cls._NOT_MUST_PROPAGATE, fn)

        return fn

    @classmethod
    def drop(
            cls,
            direction: ChannelPipelineDirectionOrDuplex,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> ChannelPipelineHandler:
        return cls.new(
            direction,
            cls._add_drop_filters(
                FlatMapChannelPipelineHandlerFns.drop(),
                filter=filter,
                filter_type=filter_type,
            ),
        )

    @classmethod
    def feed_out_and_drop(
            cls,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[ChannelPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> ChannelPipelineHandler:
        return cls.new(
            'inbound',
            cls._add_drop_filters(
                FlatMapChannelPipelineHandlerFns.compose(
                    FlatMapChannelPipelineHandlerFns.feed_out(),
                    FlatMapChannelPipelineHandlerFns.drop(),
                ),
                filter=filter,
                filter_type=filter_type,
            ),
        )

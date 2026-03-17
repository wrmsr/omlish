# ruff: noqa: UP006 UP007 UP045
# @omlish-lite
import dataclasses as dc
import functools
import typing as ta

from ....lite.abstract import Abstract
from ....lite.check import check
from ....lite.namespaces import NamespaceClass
from ..core import IoPipelineDirectionOrDuplex
from ..core import IoPipelineHandler
from ..core import IoPipelineHandlerContext
from ..core import IoPipelineHandlerFn
from ..core import IoPipelineMessages
from .fns import IoPipelineHandlerFns


##


FlatMapIoPipelineHandlerFn = IoPipelineHandlerFn[ta.Any, ta.Iterable[ta.Any]]  # ta.TypeAlias  # omlish-amalg-typing-no-move  # noqa


class FlatMapIoPipelineHandlerFns(NamespaceClass):
    @dc.dataclass(frozen=True)
    class Filter:
        pred: IoPipelineHandlerFn[ta.Any, bool]
        fn: FlatMapIoPipelineHandlerFn
        else_fn: ta.Optional[FlatMapIoPipelineHandlerFn] = None

        def __repr__(self) -> str:
            return (
                f'{type(self).__name__}('
                f'{self.pred!r}'
                f', {self.fn!r}'
                f'{f", else_fn={self.else_fn!r}" if self.else_fn is not None else ""}'
                f')'
            )

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.pred(ctx, msg):
                yield from self.fn(ctx, msg)
            elif (ef := self.else_fn) is not None:
                yield from ef(ctx, msg)  # noqa
            else:
                yield msg

    @classmethod
    def filter(
            cls,
            pred: IoPipelineHandlerFn[ta.Any, bool],
            fn: FlatMapIoPipelineHandlerFn,
            else_fn: ta.Optional[FlatMapIoPipelineHandlerFn] = None,
    ) -> FlatMapIoPipelineHandlerFn:
        return cls.Filter(pred, fn, else_fn)

    @classmethod
    def filter_type(
            cls,
            ty: ta.Union[type, ta.Tuple[type, ...]],
            fn: FlatMapIoPipelineHandlerFn,
            else_fn: ta.Optional[FlatMapIoPipelineHandlerFn] = None,
    ) -> FlatMapIoPipelineHandlerFn:
        return cls.filter(IoPipelineHandlerFns.isinstance(ty), fn, else_fn)

    #

    @dc.dataclass(frozen=True)
    class Concat:
        fns: ta.Sequence[FlatMapIoPipelineHandlerFn]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        def __post_init__(self) -> None:
            check.not_empty(self.fns)

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            for fn in self.fns:
                yield from fn(ctx, msg)

    @classmethod
    def concat(cls, *fns: FlatMapIoPipelineHandlerFn) -> FlatMapIoPipelineHandlerFn:
        return cls.Concat(fns)

    #

    @dc.dataclass(frozen=True)
    class Compose:
        fns: ta.Sequence[FlatMapIoPipelineHandlerFn]

        def __repr__(self) -> str:
            return f'{type(self).__name__}([{", ".join(map(repr, self.fns))}])'

        _fn: FlatMapIoPipelineHandlerFn = dc.field(init=False)

        def __post_init__(self) -> None:
            check.not_empty(self.fns)

            def compose(cur, nxt, ctx, msg):
                for x in cur(ctx, msg):
                    yield from nxt(ctx, x)

            xf: ta.Any = lambda ctx, msg: (msg,)  # noqa
            for cf in reversed(self.fns):
                xf = functools.partial(compose, cf, xf)

            object.__setattr__(self, '_fn', xf)

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return self._fn(ctx, msg)

    @classmethod
    def compose(cls, *fns: FlatMapIoPipelineHandlerFn) -> FlatMapIoPipelineHandlerFn:
        return cls.Compose(fns)

    #

    @dc.dataclass(frozen=True)
    class Map:
        fn: IoPipelineHandlerFn[ta.Any, ta.Any]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return (self.fn(ctx, msg),)

    @classmethod
    def map(cls, fn: IoPipelineHandlerFn[ta.Any, ta.Any]) -> FlatMapIoPipelineHandlerFn:
        return cls.Map(fn)

    #

    @dc.dataclass(frozen=True)
    class Apply:
        fn: IoPipelineHandlerFn[ta.Any, None]

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.fn!r})'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            self.fn(ctx, msg)
            return (msg,)

    @classmethod
    def apply(cls, fn: IoPipelineHandlerFn[ta.Any, None]) -> FlatMapIoPipelineHandlerFn:
        return cls.Apply(fn)

    #

    @dc.dataclass(frozen=True)
    class Feed:
        direction: IoPipelineDirectionOrDuplex

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.direction!r})'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            if self.direction == 'inbound':
                ctx.feed_in(msg)
            elif self.direction == 'outbound':
                ctx.feed_out(msg)
            else:
                raise RuntimeError(f'Unknown direction: {self.direction!r}')
            return (msg,)

    @classmethod
    def feed_in(cls) -> FlatMapIoPipelineHandlerFn:
        return cls.Feed('inbound')

    @classmethod
    def feed_out(cls) -> FlatMapIoPipelineHandlerFn:
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

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
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
    ) -> FlatMapIoPipelineHandlerFn:
        return cls.Inject(
            before=before,
            after=after,
        )

    #

    @dc.dataclass(frozen=True)
    class Drop:
        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return ()

    @classmethod
    def drop(cls) -> FlatMapIoPipelineHandlerFn:
        return cls.Drop()

    #

    @dc.dataclass(frozen=True)
    class Nop:
        def __repr__(self) -> str:
            return f'{type(self).__name__}()'

        def __call__(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> ta.Iterable[ta.Any]:
            return (msg,)

    @classmethod
    def nop(cls) -> FlatMapIoPipelineHandlerFn:
        return cls.Nop()


#


class FlatMapIoPipelineHandler(IoPipelineHandler, Abstract):
    def __init__(
            self,
            fn: FlatMapIoPipelineHandlerFn,
    ) -> None:
        super().__init__()

        self._fn = check.callable(fn)

    _fn: FlatMapIoPipelineHandlerFn

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}@{id(self):x}({self._fn!r})'


#


class InboundFlatMapIoPipelineHandler(FlatMapIoPipelineHandler):
    def inbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_in(x)


class OutboundFlatMapIoPipelineHandler(FlatMapIoPipelineHandler):
    def outbound(self, ctx: IoPipelineHandlerContext, msg: ta.Any) -> None:
        for x in self._fn(ctx, msg):
            ctx.feed_out(x)


class DuplexFlatMapIoPipelineHandler(
    InboundFlatMapIoPipelineHandler,
    OutboundFlatMapIoPipelineHandler,
):
    pass


#


class FlatMapIoPipelineHandlers(NamespaceClass):
    _CLS_BY_DIRECTION: ta.ClassVar[ta.Mapping[IoPipelineDirectionOrDuplex, ta.Type[FlatMapIoPipelineHandler]]] = {  # noqa
        'inbound': InboundFlatMapIoPipelineHandler,
        'outbound': OutboundFlatMapIoPipelineHandler,
        'duplex': DuplexFlatMapIoPipelineHandler,
    }

    @classmethod
    def new(
            cls,
            direction: IoPipelineDirectionOrDuplex,
            fn: FlatMapIoPipelineHandlerFn,
    ) -> IoPipelineHandler:
        h_cls = cls._CLS_BY_DIRECTION[direction]
        return h_cls(fn)

    #

    _NOT_MUST_PROPAGATE: ta.ClassVar[IoPipelineHandlerFn[ta.Any, bool]] = IoPipelineHandlerFns.not_(
        IoPipelineHandlerFns.isinstance(IoPipelineMessages.MustPropagate),
    )

    @classmethod
    def add_filters(
            cls,
            fn: FlatMapIoPipelineHandlerFn,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[IoPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
            not_must_propagate: bool = False,
    ) -> FlatMapIoPipelineHandlerFn:
        if filter is not None:
            fn = FlatMapIoPipelineHandlerFns.filter(filter, fn)

        if filter_type is not None:
            fn = FlatMapIoPipelineHandlerFns.filter_type(filter_type, fn)

        if not_must_propagate:
            fn = FlatMapIoPipelineHandlerFns.filter(cls._NOT_MUST_PROPAGATE, fn)

        return fn

    #

    @classmethod
    def drop(
            cls,
            direction: IoPipelineDirectionOrDuplex,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[IoPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> IoPipelineHandler:
        return cls.new(
            direction,
            cls.add_filters(
                FlatMapIoPipelineHandlerFns.drop(),
                filter=filter,
                filter_type=filter_type,
                not_must_propagate=True,
            ),
        )

    @classmethod
    def apply_and_drop(
            cls,
            direction: IoPipelineDirectionOrDuplex,
            fn: IoPipelineHandlerFn[ta.Any, None],
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[IoPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> IoPipelineHandler:
        return cls.new(
            direction,
            cls.add_filters(
                FlatMapIoPipelineHandlerFns.compose(
                    FlatMapIoPipelineHandlerFns.apply(fn),
                    FlatMapIoPipelineHandlerFns.drop(),
                ),
                filter=filter,
                filter_type=filter_type,
                not_must_propagate=True,
            ),
        )

    @classmethod
    def feed_out_and_drop(
            cls,
            *,
            filter_type: ta.Optional[ta.Union[type, ta.Tuple[type, ...]]] = None,
            filter: ta.Optional[IoPipelineHandlerFn[ta.Any, bool]] = None,  # noqa
    ) -> IoPipelineHandler:
        return cls.new(
            'inbound',
            cls.add_filters(
                FlatMapIoPipelineHandlerFns.compose(
                    FlatMapIoPipelineHandlerFns.feed_out(),
                    FlatMapIoPipelineHandlerFns.drop(),
                ),
                filter=filter,
                filter_type=filter_type,
                not_must_propagate=True,
            ),
        )

import typing as ta

from omlish import check
from omlish import dispatch
from omlish import lang


C = ta.TypeVar('C')
T = ta.TypeVar('T')


##


class Visitor(ta.Generic[C]):
    def leaf_visit(self, obj: ta.Any, ctx: C) -> None:
        raise TypeError(obj)

    @dispatch.method(installable=True, requires_override=True)
    def visit(self, obj: ta.Any, ctx: C) -> None:
        self.leaf_visit(obj, ctx)

    @staticmethod
    @ta.final
    def register(fn):
        check.callable(fn)
        check.not_isinstance(fn, type)
        check.arg(fn.__name__.startswith('visit_'))
        Visitor.visit.register(fn)  # noqa
        return fn


##


class StrLeafVisitor(Visitor[C]):
    @Visitor.register
    def visit_str(self, obj: str, ctx: C) -> None:
        self.leaf_visit(obj, ctx)


class TupleLeafVisitor(Visitor[C]):
    @Visitor.register
    def visit_tuple(self, obj: tuple, ctx: C) -> None:
        self.leaf_visit(obj, ctx)


#


class IterableVisitor(Visitor[C]):
    @Visitor.register
    def visit_iterable(self, obj: ta.Iterable, ctx: C) -> None:
        for item in obj:
            self.visit(item, ctx)


#


class MappingKeysVisitor(Visitor[C]):
    @Visitor.register
    def visit_mapping(self, obj: ta.Mapping, ctx: C) -> None:
        self.visit(obj.keys(), ctx)


class MappingValuesVisitor(Visitor[C]):
    @Visitor.register
    def visit_mapping(self, obj: ta.Mapping, ctx: C) -> None:
        self.visit(obj.values(), ctx)


class MappingItemsVisitor(Visitor[C]):
    @Visitor.register
    def visit_mapping(self, obj: ta.Mapping, ctx: C) -> None:
        self.visit(obj.items(), ctx)


##


class _FnReducer(
    MappingValuesVisitor[None],
    IterableVisitor[None],
    StrLeafVisitor[None],
    ta.Generic[T],
):
    def __init__(
            self,
            fn: ta.Callable[[T, ta.Any], T],
            init: lang.Maybe[T],
    ) -> None:
        super().__init__()

        self.fn = fn

        if init.present:
            self.v = init.must()

    v: T

    @ta.override
    def leaf_visit(self, obj: ta.Any, ctx: None) -> None:
        try:
            v = self.v
        except AttributeError:
            self.v = obj
        else:
            self.v = self.fn(v, obj)
        return None


class EmptyReduceError(TypeError):
    pass


class _NO_INIT(lang.Marker):  # noqa
    pass


def reduce(
        fn: ta.Callable[[ta.Any, T], T],
        obj: ta.Any,
        init: T | type[_NO_INIT] = _NO_INIT,
) -> T:
    fr = _FnReducer(
        fn,
        lang.just(init) if init is not _NO_INIT else lang.empty(),
    )

    fr.visit(obj, None)

    try:
        return fr.v
    except AttributeError:
        raise EmptyReduceError from None


#


def test_reduce():
    assert reduce(
        lambda acc, x: acc + x,
        {'a': [1, 2, 3], 'b': [4, 5]},
    ) == 15

    assert reduce(
        lambda acc, x: acc + x,
        {'a': [1, 2, 3], 'b': [4, 5]},
        0,
    ) == 15

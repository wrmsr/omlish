import dataclasses as dc
import typing as ta

from omlish import check
from omlish import dispatch


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


@dc.dataclass()
class _FnReducer(
    MappingValuesVisitor[None],
    IterableVisitor[None],
    StrLeafVisitor[None],
    ta.Generic[T],
):
    fn: ta.Callable[[ta.Any, T], T]
    v: T

    @ta.override
    def leaf_visit(self, obj: ta.Any, ctx: None) -> None:
        self.v = self.fn(obj, self.v)
        return None


def reduce(fn: ta.Callable[[ta.Any, T], T], obj: ta.Any, init: T) -> T:
    fr = _FnReducer(fn, init)
    fr.visit(obj, None)
    return fr.v


#


def test_reduce():
    tree = {'a': [1, 2, 3], 'b': [4, 5]}
    assert reduce(lambda acc, x: acc + x, tree, 0) == 15

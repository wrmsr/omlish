import typing as ta

import pytest

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


def test_basic():
    class V0(
        IterableVisitor[None],
        StrLeafVisitor[None],
    ):
        def __init__(self) -> None:
            super().__init__()
            self.l: list = []

        def leaf_visit(self, obj: ta.Any, ctx: C) -> None:
            self.l.append(obj)

        @classmethod
        def run(cls, obj: ta.Any) -> list:
            v = cls()
            v.visit(obj, None)
            return v.l

    assert V0.run('foo') == ['foo']
    assert V0.run(['foo']) == ['foo']
    assert V0.run(['foo', 'bar']) == ['foo', 'bar']
    assert V0.run([['foo'], 'bar', ['baz']]) == ['foo', 'bar', 'baz']
    assert V0.run([[['foo']], 'bar', ['baz']]) == ['foo', 'bar', 'baz']
    assert V0.run(('foo',)) == ['foo']
    assert V0.run((('foo',),)) == ['foo']
    assert V0.run(([('foo',),])) == ['foo']

    #

    class V1(V0):
        def leaf_visit(self, obj: ta.Any, ctx: C) -> None:
            super().leaf_visit(obj, ctx)
            self.l.append('!')

    assert V1.run([['foo'], 'bar', ['baz']]) == ['foo', '!', 'bar', '!', 'baz', '!']

    #

    class V2(V0):
        # Not @registered, does nothing
        def visit_list(self, obj: list, ctx: C) -> None:
            raise RuntimeError

    assert V2.run([['foo'], 'bar', ['baz']]) == ['foo', 'bar', 'baz']

    #

    class V3(V0):
        @Visitor.register
        def visit_list(self, obj: list, ctx: C) -> None:
            return self.visit_iterable(['V3!', *obj], ctx)

    assert V3.run([['foo'], 'bar', ['baz']]) == ['V3!', 'V3!', 'foo', 'bar', 'V3!', 'baz']

    #

    class V4(V3):
        @Visitor.register
        def visit_iterable(self, obj: ta.Iterable, ctx: C) -> None:
            return super().visit_iterable(['V4!', *obj], ctx)

    with pytest.raises(lang.RequiresOverrideError):
        V4.run([['foo'], 'bar', ['baz']])

    #

    class V5(V3):
        @Visitor.register
        @ta.override
        def visit_iterable(self, obj: ta.Iterable, ctx: C) -> None:
            return super().visit_iterable(['V5!', *obj], ctx)

    assert V5.run([['foo'], 'bar', ['baz']]) == ['V5!', 'V3!', 'V5!', 'V3!', 'foo', 'bar', 'V5!', 'V3!', 'baz']

    # #
    #
    # class V6(V3):
    #     @Visitor.register
    #     @ta.override
    #     def visit_iterable(self, obj: ta.Iterable, ctx: C) -> None:
    #         return Visitor.visit(super(), ['V6!', *obj], ctx)
    #
    # assert V6.run([['foo'], 'bar', ['baz']]) == ['V6!', 'V3!', 'V6!', 'V3!', 'foo', 'bar', 'V6!', 'V3!', 'baz']


#


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

    assert reduce(lambda acc, x: acc + x, [1]) == 1
    assert reduce(lambda acc, x: acc + x, [1, 2]) == 3
    assert reduce(lambda acc, x: acc + x, [1], 2) == 3

    with pytest.raises(EmptyReduceError):
        reduce(lambda acc, x: acc + x, [])

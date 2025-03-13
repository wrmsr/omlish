import inspect

from ..params import ArgsParam
from ..params import KwargsParam
from ..params import KwOnlyParam
from ..params import ParamSeparator
from ..params import ParamSpec
from ..params import PosOnlyParam
from ..params import ValueParam


def test_params_simple() -> None:
    def foo(a, b, *c, **kw):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    assert ps == ParamSpec(
        ValueParam('a'),
        ValueParam('b'),
        ArgsParam('c'),
        KwargsParam('kw'),
    )

    assert list(ps.with_seps) == [
        ValueParam('a'),
        ValueParam('b'),
        ArgsParam('c'),
        KwargsParam('kw'),
    ]


def test_params_pos_only() -> None:
    def foo(a, /, b, *c, **kw):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    assert ps == ParamSpec(
        PosOnlyParam('a'),
        ValueParam('b'),
        ArgsParam('c'),
        KwargsParam('kw'),
    )

    assert list(ps.with_seps) == [
        PosOnlyParam('a'),
        ParamSeparator.POS_ONLY,
        ValueParam('b'),
        ArgsParam('c'),
        KwargsParam('kw'),
    ]


def test_params_kw_only() -> None:
    def foo(a, *, b, **kw):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    assert ps == ParamSpec(
        ValueParam('a'),
        KwOnlyParam('b'),
        KwargsParam('kw'),
    )

    assert list(ps.with_seps) == [
        ValueParam('a'),
        ParamSeparator.KW_ONLY,
        KwOnlyParam('b'),
        KwargsParam('kw'),
    ]


def test_params_pos_only_and_kw_only() -> None:
    def foo(a, /, b, *, c, **kw):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    assert ps == ParamSpec(
        PosOnlyParam('a'),
        ValueParam('b'),
        KwOnlyParam('c'),
        KwargsParam('kw'),
    )

    assert list(ps.with_seps) == [
        PosOnlyParam('a'),
        ParamSeparator.POS_ONLY,
        ValueParam('b'),
        ParamSeparator.KW_ONLY,
        KwOnlyParam('c'),
        KwargsParam('kw'),
    ]

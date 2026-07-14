import inspect

from ..params import ArgsParam
from ..params import KwargsParam
from ..params import KwOnlyParam
from ..params import ParamSeparator
from ..params import ParamSpec
from ..params import PosOnlyParam
from ..params import ValParam


def test_params_simple() -> None:
    def foo(a, b, *c, **kw):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    assert ps == ParamSpec(
        ValParam('a'),
        ValParam('b'),
        ArgsParam('c'),
        KwargsParam('kw'),
    )

    assert list(ps.with_seps) == [
        ValParam('a'),
        ValParam('b'),
        ArgsParam('c'),
        KwargsParam('kw'),
    ]


def test_params_pos_only() -> None:
    def foo(a, /, b, *c, **kw):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    assert ps == ParamSpec(
        PosOnlyParam('a'),
        ValParam('b'),
        ArgsParam('c'),
        KwargsParam('kw'),
    )

    assert list(ps.with_seps) == [
        PosOnlyParam('a'),
        ParamSeparator.POS_ONLY,
        ValParam('b'),
        ArgsParam('c'),
        KwargsParam('kw'),
    ]


def test_params_kw_only() -> None:
    def foo(a, *, b, **kw):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    assert ps == ParamSpec(
        ValParam('a'),
        KwOnlyParam('b'),
        KwargsParam('kw'),
    )

    assert list(ps.with_seps) == [
        ValParam('a'),
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
        ValParam('b'),
        KwOnlyParam('c'),
        KwargsParam('kw'),
    )

    assert list(ps.with_seps) == [
        PosOnlyParam('a'),
        ParamSeparator.POS_ONLY,
        ValParam('b'),
        ParamSeparator.KW_ONLY,
        KwOnlyParam('c'),
        KwargsParam('kw'),
    ]


def test_params_trailing_pos_only() -> None:
    def foo(a, b, /):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    # A trailing positional-only run must still emit its '/' separator.
    assert list(ps.with_seps) == [
        PosOnlyParam('a'),
        PosOnlyParam('b'),
        ParamSeparator.POS_ONLY,
    ]


def test_params_var_positional_then_kw_only() -> None:
    def foo(*args, k):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    # *args already forces k to be keyword-only - no bare '*' separator should be inserted after it.
    assert list(ps.with_seps) == [
        ArgsParam('args'),
        KwOnlyParam('k'),
    ]


def test_params_pos_only_then_kw_only_no_args() -> None:
    def foo(a, /, *, b):
        pass

    ps = ParamSpec.of_signature(inspect.signature(foo))

    assert list(ps.with_seps) == [
        PosOnlyParam('a'),
        ParamSeparator.POS_ONLY,
        ParamSeparator.KW_ONLY,
        KwOnlyParam('b'),
    ]

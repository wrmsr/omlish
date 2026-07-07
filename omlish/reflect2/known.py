import collections.abc as cabc
import contextlib
import dataclasses as dc
import typing as ta

from .core.symbols import VarianceKind


##


_KnownBaseArg: ta.TypeAlias = int | str
_KnownBaseSpec: ta.TypeAlias = tuple[str, tuple[_KnownBaseArg, ...]]


@dc.dataclass(frozen=True)
class _Known:
    type: object
    fullname: str

    _: dc.KW_ONLY

    arity: int | None = None
    variances: tuple[VarianceKind, ...] | None = None

    specs: tuple[_KnownBaseSpec, ...] | None = None

    mro_tail: tuple[str, ...] | None = None


##


_KNOWNS: ta.Final[ta.Sequence[_Known]] = [
    # builtins
    # https://github.com/python/mypy/blob/f5163c011078ef66753cdf706b7b2dd14da401ab/mypy/typeshed/stdlib/builtins.pyi

    _Known(
        object,
        'builtins.object',
    ),

    _Known(
        type,
        'builtins.type',
        arity=1,
        variances=(VarianceKind.CO,),
        mro_tail=('builtins.object',),
    ),

    _Known(
        type(None),
        'builtins.None',
        mro_tail=(
            'builtins.object',
        ),
    ),

    _Known(
        bool,
        'builtins.bool',
        mro_tail=(
            'builtins.int',
            'builtins.object',
        ),
    ),

    _Known(
        int,
        'builtins.int',
        mro_tail=('builtins.object',),
    ),

    _Known(
        float,
        'builtins.float',
        mro_tail=('builtins.object',),
    ),

    _Known(
        complex,
        'builtins.complex',
        mro_tail=('builtins.object',),
    ),

    _Known(
        str,
        'builtins.str',
        specs=(
            ('collections.abc.Sequence', ('builtins.str',)),
        ),
        mro_tail=(
            'collections.abc.Sequence',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        bytes,
        'builtins.bytes',
        specs=(
            ('collections.abc.Sequence', ('builtins.int',)),
        ),
        mro_tail=(
            'collections.abc.Sequence',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        list,
        'builtins.list',
        arity=1,
        specs=(
            ('collections.abc.MutableSequence', (0,)),
        ),
        mro_tail=(
            'collections.abc.MutableSequence',
            'collections.abc.Sequence',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        dict,
        'builtins.dict',
        arity=2,
        specs=(
            ('collections.abc.MutableMapping', (0, 1)),
        ),
        mro_tail=(
            'collections.abc.MutableMapping',
            'collections.abc.Mapping',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        tuple,
        'builtins.tuple',
        arity=1,
        variances=(VarianceKind.CO,),
        specs=(
            ('collections.abc.Sequence', (0,)),
        ),
        mro_tail=(
            'collections.abc.Sequence',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        set,
        'builtins.set',
        arity=1,
        specs=(
            ('collections.abc.MutableSet', (0,)),
        ),
        mro_tail=(
            'collections.abc.MutableSet',
            'collections.abc.Set',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        frozenset,
        'builtins.frozenset',
        arity=1,
        variances=(VarianceKind.CO,),
        specs=(
            ('collections.abc.Set', (0,)),
        ),
        mro_tail=(
            'collections.abc.Set',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    # collections.abc
    # https://github.com/python/mypy/blob/f5163c011078ef66753cdf706b7b2dd14da401ab/mypy/typeshed/stdlib/collections/__init__.pyi

    _Known(
        cabc.Iterable,
        'collections.abc.Iterable',
        arity=1,
        variances=(VarianceKind.CO,),
        mro_tail=('builtins.object',),
    ),

    _Known(
        cabc.Iterator,
        'collections.abc.Iterator',
        arity=1,
        variances=(VarianceKind.CO,),
        mro_tail=('builtins.object',),
    ),

    _Known(
        cabc.AsyncIterable,
        'collections.abc.AsyncIterable',
        arity=1,
        variances=(VarianceKind.CO,),
        mro_tail=('builtins.object',),
    ),

    _Known(
        cabc.AsyncIterator,
        'collections.abc.AsyncIterator',
        arity=1,
        variances=(VarianceKind.CO,),
        mro_tail=('builtins.object',),
    ),

    _Known(
        cabc.Sequence,
        'collections.abc.Sequence',
        arity=1,
        variances=(VarianceKind.CO,),
        specs=(
            ('collections.abc.Iterable', (0,)),
        ),
        mro_tail=(
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        cabc.MutableSequence,
        'collections.abc.MutableSequence',
        arity=1,
        specs=(
            ('collections.abc.Sequence', (0,)),
        ),
        mro_tail=(
            'collections.abc.Sequence',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        cabc.Mapping,
        'collections.abc.Mapping',
        arity=2,
        variances=(VarianceKind.CO, VarianceKind.CO),
        specs=(
            ('collections.abc.Iterable', (0,)),
        ),
        mro_tail=(
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        cabc.MutableMapping,
        'collections.abc.MutableMapping',
        arity=2,
        specs=(
            ('collections.abc.Mapping', (0, 1)),
        ),
        mro_tail=(
            'collections.abc.Mapping',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        cabc.Set,
        'collections.abc.Set',
        arity=1,
        variances=(VarianceKind.CO,),
        specs=(
            ('collections.abc.Iterable', (0,)),
        ),
        mro_tail=(
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        cabc.MutableSet,
        'collections.abc.MutableSet',
        arity=1,
        specs=(
            ('collections.abc.Set', (0,)),
        ),
        mro_tail=(
            'collections.abc.Set',
            'collections.abc.Iterable',
            'builtins.object',
        ),
    ),

    _Known(
        cabc.Callable,
        'collections.abc.Callable',
        arity=1,
        variances=(VarianceKind.CO,),
        mro_tail=('builtins.object',),
    ),

    _Known(
        cabc.Awaitable,
        'collections.abc.Awaitable',
        arity=1,
        variances=(VarianceKind.CO,),
        mro_tail=('builtins.object',),
    ),

    # contextlib
    # https://github.com/python/mypy/blob/f5163c011078ef66753cdf706b7b2dd14da401ab/mypy/typeshed/stdlib/contextlib.pyi

    _Known(
        contextlib.AbstractContextManager,
        'contextlib.AbstractContextManager',
        arity=2,
        variances=(VarianceKind.CO, VarianceKind.CO),
        mro_tail=('builtins.object',),
    ),

    _Known(
        contextlib.AbstractAsyncContextManager,
        'contextlib.AbstractAsyncContextManager',
        arity=2,
        variances=(VarianceKind.CO, VarianceKind.CO),
        mro_tail=('builtins.object',),
    ),

    # typing
    # https://github.com/python/mypy/blob/f5163c011078ef66753cdf706b7b2dd14da401ab/mypy/typeshed/stdlib/typing.pyi
    # https://github.com/python/mypy/blob/f5163c011078ef66753cdf706b7b2dd14da401ab/mypy/typeshed/stdlib/typing_extensions.pyi

    _Known(
        ta.Generic,
        'typing.Generic',
    ),
]


##


_KNOWN_FULLNAMES_BY_TYPE: ta.Final[ta.Mapping[object, str]] = {
    k.type: k.fullname
    for k in _KNOWNS
}

_KNOWN_GENERIC_ARITIES: ta.Final[ta.Mapping[str, int]] = {
    k.fullname: k.arity
    for k in _KNOWNS
    if k.arity is not None
}

_KNOWN_GENERIC_VARIANCES: ta.Final[ta.Mapping[str, tuple[VarianceKind, ...]]] = {
    k.fullname: k.variances
    for k in _KNOWNS
    if k.variances is not None
}

_KNOWN_BASE_SPECS: ta.Final[ta.Mapping[str, tuple[_KnownBaseSpec, ...]]] = {
    k.fullname: k.specs
    for k in _KNOWNS
    if k.specs is not None
}

_KNOWN_MRO_TAILS: ta.Final[ta.Mapping[str, tuple[str, ...]]] = {
    k.fullname: k.mro_tail
    for k in _KNOWNS
    if k.mro_tail is not None
}

import collections.abc as cabc
import typing as ta

from .core.symbols import VarianceKind


##


_KNOWN_FULLNAMES_BY_TYPE: ta.Final[ta.Mapping[object, str]] = {
    object: 'builtins.object',
    type: 'builtins.type',
    type(None): 'builtins.None',
    bool: 'builtins.bool',
    int: 'builtins.int',
    float: 'builtins.float',
    complex: 'builtins.complex',
    str: 'builtins.str',
    bytes: 'builtins.bytes',
    list: 'builtins.list',
    dict: 'builtins.dict',
    tuple: 'builtins.tuple',
    set: 'builtins.set',
    frozenset: 'builtins.frozenset',

    cabc.Iterable: 'collections.abc.Iterable',
    cabc.Iterator: 'collections.abc.Iterator',
    cabc.Sequence: 'collections.abc.Sequence',
    cabc.MutableSequence: 'collections.abc.MutableSequence',
    cabc.Mapping: 'collections.abc.Mapping',
    cabc.MutableMapping: 'collections.abc.MutableMapping',
    cabc.Set: 'collections.abc.Set',
    cabc.MutableSet: 'collections.abc.MutableSet',
    cabc.Callable: 'collections.abc.Callable',
    cabc.Awaitable: 'collections.abc.Awaitable',

    ta.Generic: 'typing.Generic',
}

_KNOWN_GENERIC_ARITIES: ta.Final[ta.Mapping[str, int]] = {
    'builtins.type': 1,
    'builtins.list': 1,
    'builtins.dict': 2,
    'builtins.tuple': 1,
    'builtins.set': 1,
    'builtins.frozenset': 1,

    'collections.abc.Iterable': 1,
    'collections.abc.Iterator': 1,
    'collections.abc.Sequence': 1,
    'collections.abc.MutableSequence': 1,
    'collections.abc.Mapping': 2,
    'collections.abc.MutableMapping': 2,
    'collections.abc.Set': 1,
    'collections.abc.MutableSet': 1,
    'collections.abc.Callable': 1,
    'collections.abc.Awaitable': 1,
}

_KNOWN_GENERIC_VARIANCES: ta.Final[ta.Mapping[str, tuple[VarianceKind, ...]]] = {
    'builtins.type': (VarianceKind.CO,),
    'builtins.tuple': (VarianceKind.CO,),
    'builtins.frozenset': (VarianceKind.CO,),

    'collections.abc.Iterable': (VarianceKind.CO,),
    'collections.abc.Iterator': (VarianceKind.CO,),
    'collections.abc.Sequence': (VarianceKind.CO,),
    'collections.abc.Mapping': (VarianceKind.CO, VarianceKind.CO),
    'collections.abc.Set': (VarianceKind.CO,),
    'collections.abc.Callable': (VarianceKind.CO,),
    'collections.abc.Awaitable': (VarianceKind.CO,),
}


_KnownBaseArg: ta.TypeAlias = int | str
_KnownBaseSpec: ta.TypeAlias = tuple[str, tuple[_KnownBaseArg, ...]]

_KNOWN_BASE_SPECS: ta.Final[ta.Mapping[str, tuple[_KnownBaseSpec, ...]]] = {
    'builtins.str': (
        ('collections.abc.Sequence', ('builtins.str',)),
    ),
    'builtins.bytes': (
        ('collections.abc.Sequence', ('builtins.int',)),
    ),
    'builtins.list': (
        ('collections.abc.MutableSequence', (0,)),
    ),
    'builtins.tuple': (
        ('collections.abc.Sequence', (0,)),
    ),
    'builtins.dict': (
        ('collections.abc.MutableMapping', (0, 1)),
    ),
    'builtins.set': (
        ('collections.abc.MutableSet', (0,)),
    ),
    'builtins.frozenset': (
        ('collections.abc.Set', (0,)),
    ),

    'collections.abc.MutableSequence': (
        ('collections.abc.Sequence', (0,)),
    ),
    'collections.abc.Sequence': (
        ('collections.abc.Iterable', (0,)),
    ),
    'collections.abc.MutableMapping': (
        ('collections.abc.Mapping', (0, 1)),
    ),
    'collections.abc.Mapping': (
        ('collections.abc.Iterable', (0,)),
    ),
    'collections.abc.MutableSet': (
        ('collections.abc.Set', (0,)),
    ),
    'collections.abc.Set': (
        ('collections.abc.Iterable', (0,)),
    ),
}

_KNOWN_MRO_TAILS: ta.Final[ta.Mapping[str, tuple[str, ...]]] = {
    'builtins.type': (
        'builtins.object',
    ),
    'builtins.None': (
        'builtins.object',
    ),
    'builtins.bool': (
        'builtins.int',
        'builtins.object',
    ),
    'builtins.int': (
        'builtins.object',
    ),
    'builtins.float': (
        'builtins.object',
    ),
    'builtins.complex': (
        'builtins.object',
    ),
    'builtins.list': (
        'collections.abc.MutableSequence',
        'collections.abc.Sequence',
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'builtins.str': (
        'collections.abc.Sequence',
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'builtins.bytes': (
        'collections.abc.Sequence',
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'builtins.tuple': (
        'collections.abc.Sequence',
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'builtins.dict': (
        'collections.abc.MutableMapping',
        'collections.abc.Mapping',
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'builtins.set': (
        'collections.abc.MutableSet',
        'collections.abc.Set',
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'builtins.frozenset': (
        'collections.abc.Set',
        'collections.abc.Iterable',
        'builtins.object',
    ),

    'collections.abc.MutableSequence': (
        'collections.abc.Sequence',
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'collections.abc.Sequence': (
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'collections.abc.MutableMapping': (
        'collections.abc.Mapping',
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'collections.abc.Mapping': (
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'collections.abc.MutableSet': (
        'collections.abc.Set',
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'collections.abc.Set': (
        'collections.abc.Iterable',
        'builtins.object',
    ),
    'collections.abc.Iterable': (
        'builtins.object',
    ),
}

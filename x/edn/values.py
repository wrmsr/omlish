import dataclasses as dc
import typing as ta


##


@dc.dataclass(frozen=True)
class Nil:
    pass


NIL = Nil()


@dc.dataclass(frozen=True)
class Char:
    value: str


@dc.dataclass(frozen=True)
class Symbol:
    name: str
    namespace: str | None = None


@dc.dataclass(frozen=True)
class List:
    values: ta.Sequence['Value']


@dc.dataclass(frozen=True)
class Vector:
    values: ta.Sequence['Value']


@dc.dataclass(frozen=True)
class Set:
    values: ta.Sequence['Value']


@dc.dataclass(frozen=True)
class Map:
    entries: ta.Sequence[ta.Tuple['Value', 'Value']]


@dc.dataclass(frozen=True)
class Tagged:
    tag: Symbol
    value: 'Value'


##


PRIMITIVE_VALUE_TYPES: tuple[type, ...] = (
    bool,
    int,
    float,
    str,
)

PrimitiveValue: ta.TypeAlias = ta.Union[  # noqa
    bool,
    int,
    float,
    str,
]


SCALAR_VALUE_TYPES: tuple[type, ...] = (
    *PRIMITIVE_VALUE_TYPES,
    Nil,
    Char,
    Symbol,
)

ScalarValue: ta.TypeAlias = ta.Union[  # noqa
    PrimitiveValue,
    Nil,
    Char,
    Symbol,
]


VALUE_TYPES: tuple[type, ...] = (
    *SCALAR_VALUE_TYPES,
    List,
    Vector,
    Map,
    Set,
    Tagged,
)

Value: ta.TypeAlias = ta.Union[  # noqa
    ScalarValue,
    List,
    Vector,
    Map,
    Set,
    Tagged,
]

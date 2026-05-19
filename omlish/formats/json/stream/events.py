import typing as ta

from .... import lang
from .tokens import SCALAR_VALUE_TYPES
from .tokens import ScalarValue


##


class BeginObject(lang.Marker):
    pass


class Key(ta.NamedTuple):
    key: str


class EndObject(lang.Marker):
    pass


class BeginArray(lang.Marker):
    pass


class EndArray(lang.Marker):
    pass


Event: ta.TypeAlias = ta.Union[  # noqa
    type[BeginObject],
    Key,
    type[EndObject],

    type[BeginArray],
    type[EndArray],

    ScalarValue,
]


class Events(lang.Namespace):
    BeginObject = BeginObject
    Key = Key
    EndObject = EndObject

    BeginArray = BeginArray
    EndArray = EndArray


##


def yield_events(obj: ta.Any) -> ta.Iterator[Event]:
    if isinstance(obj, SCALAR_VALUE_TYPES):
        yield obj  # type: ignore

    elif isinstance(obj, ta.Mapping):
        yield BeginObject
        for k, v in obj.items():
            yield Key(k)
            yield from yield_events(v)
        yield EndObject

    elif isinstance(obj, ta.Sequence):
        yield BeginArray
        for v in obj:
            yield from yield_events(v)
        yield EndArray

    else:
        raise TypeError(obj)

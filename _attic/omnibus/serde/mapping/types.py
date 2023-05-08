import abc
import enum
import typing as ta

from ... import defs
from ... import lang
from ... import reflect as rfl


T = ta.TypeVar('T')


PRIMITIVE_TYPES_TUPLE = (
    type(None),
    bool,
    float,
    int,
    str,
)

Primitive = ta.Union[PRIMITIVE_TYPES_TUPLE]

PRIMITIVE_TYPES: ta.AbstractSet[type] = frozenset(PRIMITIVE_TYPES_TUPLE)


MappingKey = ta.Union[int, str]


Serializable = ta.Union[
    Primitive,
    enum.Enum,
    ta.Optional['Serializable'],
    ta.Sequence['Serializable'],
    ta.AbstractSet['Serializable'],
    ta.Mapping[MappingKey, 'Serializable'],
]

Serialized = ta.Union[
    Primitive,
    ta.Optional['Serialized'],
    ta.List['Serialized'],
    ta.Dict[str, 'Serialized'],
]


Serializer = ta.Callable[[T],  Serialized]
Deserializer = ta.Callable[[Serialized], T]


class Serde(lang.Abstract, ta.Generic[T]):

    @property
    def handles_polymorphism(self) -> bool:
        return False

    @abc.abstractmethod
    def serialize(self, obj: T) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def deserialize(self, ser: ta.Any) -> T:
        raise NotImplementedError


class FnSerde(Serde, lang.Final):

    def __init__(self, ser: Serializer, des: Deserializer) -> None:
        super().__init__()

        self._ser = self.serialize = ser
        self._des = self.deserialize = des

    def serialize(self, obj: T) -> ta.Any:
        return self._ser(obj)

    def deserialize(self, ser: ta.Any) -> T:
        return self._des(ser)


SerdeGen = ta.Callable[[rfl.Spec], ta.Optional[Serde]]


class InstanceSerdeGen(lang.Abstract):

    @abc.abstractmethod
    def match(self, spec: rfl.Spec) -> bool:
        raise NotImplementedError

    class Instance(Serde[T], lang.Abstract):

        def __init__(self, spec: rfl.Spec) -> None:
            super().__init__()

            self._spec = spec

    def __call__(self, spec: rfl.Spec) -> ta.Optional[Instance]:
        if self.match(spec):
            return self.Instance(spec)
        else:
            return None


class DeserializationException(Exception):

    def __init__(self, *args, spec: ta.Any, ser: Serialized) -> None:
        super().__init__(*args)

        self.spec = spec
        self.ser = ser

    defs.basic('args', 'spec', 'ser')

    def __str__(self) -> str:
        return repr(self)

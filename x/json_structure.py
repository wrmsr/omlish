"""
TODO:
 - detect shared structures of object field values when used as a dict - heuristic?
 - add 'Value.all', optional
"""
import abc
import dataclasses as dc
import json
import typing as ta

from omlish import lang


ValueT = ta.TypeVar('ValueT', bound='Value')


@dc.dataclass()
class Value(lang.Abstract):
    count: int = 1

    def merge(self, other: 'Value') -> 'Value':
        if isinstance(other, type(self)):
            self.update(other)
            return self
        else:
            return Union(values={
                type(self): self,
                type(other): other,
            })

    @ta.final
    def update(self, other: ta.Self) -> None:
        self.count += 1
        self._update(other)

    @abc.abstractmethod
    def _update(self, other: ta.Self) -> None:
        raise NotImplementedError


@dc.dataclass()
class Null(Value):
    def _update(self, other: ta.Self) -> None:
        pass


@dc.dataclass()
class Bool(Value):
    def _update(self, other: ta.Self) -> None:
        pass


@dc.dataclass()
class Int(Value):
    min: int = 0
    max: int = 0

    def _update(self, other: 'Int') -> None:
        self.min = min(self.min, other.min)
        self.max = max(self.max, other.max)


@dc.dataclass()
class Float(Value):
    min: float = 0.
    max: float = 0.

    def _update(self, other: 'Float') -> None:
        self.min = min(self.min, other.min)
        self.max = max(self.max, other.max)


@dc.dataclass()
class String(Value):
    min_len: int = 0
    max_len: int = 0

    def _update(self, other: 'String') -> None:
        self.min_len = min(self.min_len, other.min_len)
        self.max_len = max(self.max_len, other.max_len)


@dc.dataclass()
class Union(Value):
    values: dict[type[Value], Value] = dc.field(default_factory=dict)

    def __iter__(self) -> ta.Iterator[Value]:
        return iter(self.values.values())

    def __getitem__(self, cls: type[ValueT]) -> ValueT:
        return self.values[cls]  # type: ignore

    def merge(self, other: Value) -> Value:
        if isinstance(other, Union):
            self.merge(other)
        else:
            self._update_one(other)
        return self

    def _update(self, other: 'Union') -> None:
        for v in other:
            self._update_one(v)

    def _update_one(self, v: Value) -> None:
        try:
            e = self[type(v)]
        except KeyError:
            self.values[type(v)] = v
        else:
            e.update(v)


@dc.dataclass()
class Array(Value):
    item: Value | None = None
    min_len: int = 0
    max_len: int = 0

    def _update(self, other: 'Array') -> None:
        if self.item is None:
            self.item = other.item
        elif other.item is not None:
            self.item = self.item.merge(other.item)
        self.min_len = min(self.min_len, other.min_len)
        self.max_len = max(self.max_len, other.max_len)


@dc.dataclass()
class Object(Value):
    fields: dict[str, Value] = dc.field(default_factory=dict)

    def _update(self, other: ta.Self) -> None:
        for k, v in other.fields.items():
            try:
                e = self.fields[k]
            except KeyError:
                self.fields[k] = v
            else:
                self.fields[k] = e.merge(v)


def analyze_value(v: ta.Any) -> Value:
    if v is None:
        return Null()

    elif isinstance(v, bool):
        return Bool()

    elif isinstance(v, int):
        return Int(min=v, max=v)

    elif isinstance(v, float):
        return Float(min=v, max=v)

    elif isinstance(v, str):
        return String(min_len=len(v), max_len=len(v))

    elif isinstance(v, ta.Mapping):
        o = Object()
        for k, v in v.items():
            o.fields[k] = analyze_value(v)
        return o

    elif isinstance(v, ta.Sequence):
        a = Array(min_len=len(v), max_len=len(v))
        for i, e in enumerate(v):
            n = analyze_value(e)
            if not i:
                a.item = n
            else:
                a.item = a.item.merge(n)
        return a

    else:
        raise TypeError(v)


# Example Usage
json_data = """
{
    "name": "John Doe",
    "age": 30,
    "isActive": true,
    "emails": ["john@example.com", "doe@example.com"],
    "address": {
        "street": "123 Main St",
        "city": "Anytown",
        "zip": 12345
    },
    "children": [
        {
            "name": "Jane Doe",
            "age": 5
        },
        {
            "name": "Joe Doe",
            "age": 8
        }
    ],
    "hobbies": []
}
"""

data = json.loads(json_data)
structure = analyze_value(data)
print("Inferred JSON Structure:")
print(structure)

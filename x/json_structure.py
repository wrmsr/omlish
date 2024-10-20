import abc
import dataclasses as dc
import json
import typing as ta


ValueT = ta.TypeVar('ValueT', bound='Value')


@dc.dataclass()
class Value(abc.ABC):
    count: int

    @ta.final
    def merge(self, other: 'Value') -> 'Value':
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, other: ta.Self) -> None:
        raise NotImplementedError


@dc.dataclass()
class Int(Value):
    min: int
    max: int

    def update(self, other: 'Int') -> None:
        self.min = min(self.min, other.min)
        self.max = max(self.max, other.max)


@dc.dataclass()
class Float(Value):
    min: float
    max: float

    def update(self, other: 'Float') -> None:
        self.min = min(self.min, other.min)
        self.max = max(self.max, other.max)


@dc.dataclass()
class String(Value):
    min_len: int
    max_len: int

    def update(self, other: 'String') -> None:
        self.min_len = min(self.min_len, other.min_len)
        self.max_len = max(self.max_len, other.max_len)


@dc.dataclass()
class Union(Value):
    values: dict[type[Value], Value]

    def __iter__(self) -> ta.Iterator[Value]:
        return iter(self.values.values())

    def __getitem__(self, cls: type[ValueT]) -> ValueT:
        return self.values[cls]  # type: ignore

    def update(self, other: 'Union') -> None:
        for v in other:
            try:
                e = self[type(v)]
            except KeyError:
                self.values[type(v)] = c
            else:
                e.update(v)


@dc.dataclass()
class Array(Value):
    item_type: Value
    min_len: int
    max_len: int


@dc.dataclass()
class Object(Value):
    properties: ta.Mapping[str, Value]


def infer_structure(data, depth=0):
    if isinstance(data, dict):
        # Object detected
        structure = {}
        for key, value in data.items():
            structure[key] = infer_structure(value, depth + 1)
        return {'type': 'object', 'properties': structure}
    elif isinstance(data, list):
        # Array detected
        if len(data) > 0:
            # Analyze the first item in the array to infer its structure
            item_structure = infer_structure(data[0], depth + 1)
            return {'type': 'array', 'items': item_structure}
        else:
            return {'type': 'array', 'items': 'unknown'}  # Empty array
    else:
        # Base data types
        if isinstance(data, str):
            return 'string'
        elif isinstance(data, int):
            return 'integer'
        elif isinstance(data, float):
            return 'float'
        elif isinstance(data, bool):
            return 'boolean'
        elif data is None:
            return 'null'
        else:
            return 'unknown'


def print_structure(structure, depth=0):
    """
    Pretty prints the inferred JSON structure.
    """
    indent = '  ' * depth
    if isinstance(structure, dict):
        if 'type' in structure:
            print(f"{indent}Type: {structure['type']}")
            if structure['type'] == 'object' and 'properties' in structure:
                print(f"{indent}Properties:")
                for key, value in structure['properties'].items():
                    print(f"{indent}  - {key}:")
                    print_structure(value, depth + 2)
            elif structure['type'] == 'array' and 'items' in structure:
                print(f"{indent}Items:")
                print_structure(structure['items'], depth + 1)
        else:
            for key, value in structure.items():
                print(f"{indent}{key}:")
                print_structure(value, depth + 1)
    else:
        print(f"{indent}{structure}")


# Example Usage
json_data = '''
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
'''

data = json.loads(json_data)
structure = infer_structure(data)
print("Inferred JSON Structure:")
print_structure(structure)

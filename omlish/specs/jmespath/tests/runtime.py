import abc
import dataclasses as dc
import enum
import json
import typing as ta

from omlish import check
from omlish import lang

from ..ast import Node


T = ta.TypeVar('T')


class ValueType(enum.Enum):
    NUMBER = enum.auto()
    STRING = enum.auto()
    BOOLEAN = enum.auto()
    ARRAY = enum.auto()
    OBJECT = enum.auto()
    NULL = enum.auto()


class Arg(lang.Abstract, lang.Sealed, ta.Generic[T]):
    @abc.abstractmethod
    def value(self) -> T:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class ValueArg(Arg[T], lang.Final):
    value: T


@dc.dataclass(frozen=True)
class NodeArg(Arg[Node], lang.Final):
    value: Node


class Runtime(lang.Abstract, ta.Generic[T]):
    @abc.abstractmethod
    def is_truthy(self, obj: T) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def get_type(self, obj: T) -> ValueType:
        raise NotImplementedError

    def is_null(self, obj: T) -> bool:
        return self.get_type(obj) == ValueType.NULL

    @abc.abstractmethod
    def create_null(self) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def compare(self, op: n.Compare.Op, left: T, right: T) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def create_array(self, items: ta.Iterable[T]) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def create_object(self, fields: ta.Mapping[str, T]) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def to_iterable(self, obj: T) -> ta.Iterable[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def invoke_function(self, name: str, args: ta.Iterable[Arg]) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def create_bool(self, value: bool) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def get_property(self, obj: T, field: str) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def parse_str(self, s: str) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def create_str(self, val: str) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def get_num_var(self, num: int) -> T:
        raise NotImplementedError

    @abc.abstractmethod
    def get_name_var(self, name: str) -> T:
        raise NotImplementedError


class RuntimeImpl(Runtime[ta.Any]):

    def is_truthy(self, obj: ta.Any) -> bool:
        ty = self.get_type(obj)
        if ty == ValueType.NULL:
            return False
        elif ty == ValueType.NUMBER:
            return True
        elif ty == ValueType.STRING:
            return bool(obj)
        elif ty == ValueType.BOOLEAN:
            return obj
        elif ty == ValueType.ARRAY:
            return bool(obj)
        elif ty == ValueType.OBJECT:
            return bool(obj)
        else:
            raise TypeError(obj)

    def get_type(self, obj: ta.Any) -> ValueType:
        if obj is None:
            return ValueType.NULL
        elif isinstance(obj, (int, float)):
            return ValueType.NUMBER
        elif isinstance(obj, str):
            return ValueType.STRING
        elif isinstance(obj, bool):
            return ValueType.BOOLEAN
        elif isinstance(obj, list):
            return ValueType.ARRAY
        elif isinstance(obj, dict):
            return ValueType.OBJECT
        else:
            raise TypeError(obj)

    def create_null(self) -> None:
        return None

    def compare(self, op: n.Compare.Op, left: ta.Any, right: ta.Any) -> int:
        lty = self.get_type(left)
        rty = self.get_type(right)
        if lty == rty:
            if lty == ValueType.NULL:
                return 0
            elif lty == ValueType.BOOLEAN or lty == ValueType.NUMBER or lty == ValueType.STRING:
                return lang.cmp(left, right)
            elif lty == ValueType.ARRAY:
                raise NotImplementedError
            elif lty == ValueType.OBJECT:
                raise NotImplementedError
            else:
                raise TypeError(left, right)
        else:
            return -1

    def create_array(self, items: ta.Iterable[ta.Any]) -> list:
        return list(items)

    def create_object(self, fields: ta.Mapping[str, ta.Any]) -> dict:
        return dict(fields)

    def to_iterable(self, obj: ta.Any) -> list:
        if isinstance(obj, list):
            return list(obj)
        elif isinstance(obj, dict):
            return list(obj.values())
        else:
            return []

    def invoke_function(self, name: str, args: ta.Iterable[Arg]) -> ta.Any:
        if name == 'sum':
            return sum(check.isinstance(check.single(args), ValueArg).value)
        raise NotImplementedError

    def create_bool(self, value: bool) -> bool:
        return bool(value)

    def get_property(self, obj: ta.Any, field: str) -> ta.Any:
        if isinstance(obj, dict):
            return obj.get(field)
        else:
            return None

    def parse_str(self, s: str) -> ta.Any:
        try:
            return json.loads(s)
        except Exception as e:  # noqa
            raise

    def create_str(self, val: str) -> str:
        return str(val)

    def get_num_var(self, num: int) -> ta.Any:
        raise NotImplementedError

    def get_name_var(self, name: str) -> ta.Any:
        raise NotImplementedError

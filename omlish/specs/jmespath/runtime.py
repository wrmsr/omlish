import abc
import numbers
import operator
import typing as ta

from ... import lang
from .ast import ArithmeticOperator
from .ast import ComparatorName
from .ast import UnaryArithmeticOperator


JmespathType: ta.TypeAlias = ta.Literal[
    'boolean',
    'array',
    'object',
    'null',
    'string',
    'number',
    'expref',
]


##


def _equals(x: ta.Any, y: ta.Any) -> bool:
    if _is_special_number_case(x, y):
        return False
    else:
        return x == y


def _is_special_number_case(x: ta.Any, y: ta.Any) -> bool | None:
    if _is_actual_number(x) and x in (0, 1):
        return isinstance(y, bool)

    elif _is_actual_number(y) and y in (0, 1):
        return isinstance(x, bool)

    else:
        return None


def _is_actual_number(x: ta.Any) -> bool:
    if isinstance(x, bool):
        return False
    return isinstance(x, numbers.Number)


def _is_comparable(x: ta.Any) -> bool:
    return _is_actual_number(x) or isinstance(x, str)


##


class Runtime(lang.Abstract):
    @abc.abstractmethod
    def type_of(self, value: ta.Any) -> JmespathType | ta.Literal['unknown']:
        raise NotImplementedError

    @abc.abstractmethod
    def is_false(self, value: ta.Any) -> bool:
        raise NotImplementedError

    def is_true(self, value: ta.Any) -> bool:
        return not self.is_false(value)

    def is_null(self, value: ta.Any) -> bool:
        return self.type_of(value) == 'null'

    @abc.abstractmethod
    def is_zero_number(self, value: ta.Any) -> bool:
        raise NotImplementedError

    @abc.abstractmethod
    def make_null(self) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def make_bool(self, value: bool) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def get_field(self, value: ta.Any, name: str) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def get_index(self, value: ta.Any, index: int) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def slice(self, value: ta.Any, start: int | None, end: int | None, step: int | None) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def iter_array(self, value: ta.Any) -> ta.Iterable[ta.Any] | None:
        raise NotImplementedError

    @abc.abstractmethod
    def iter_object_values(self, value: ta.Any) -> ta.Iterable[ta.Any] | None:
        raise NotImplementedError

    @abc.abstractmethod
    def iter_object_items(self, value: ta.Any) -> ta.Iterable[tuple[str, ta.Any]] | None:
        raise NotImplementedError

    @abc.abstractmethod
    def make_array(self, values: ta.Iterable[ta.Any]) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def make_object(self, values: ta.Mapping[str, ta.Any]) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def compare(self, op: ComparatorName, left: ta.Any, right: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def arithmetic_unary(self, op: UnaryArithmeticOperator, value: ta.Any) -> ta.Any:
        raise NotImplementedError

    @abc.abstractmethod
    def arithmetic(self, op: ArithmeticOperator, left: ta.Any, right: ta.Any) -> ta.Any:
        raise NotImplementedError

    def to_python(self, value: ta.Any) -> ta.Any:
        return value


##


class PythonRuntime(Runtime):
    _COMPARATOR_FUNC: ta.Mapping[ComparatorName, ta.Callable[[ta.Any, ta.Any], ta.Any]] = {
        'eq': _equals,
        'ne': lambda x, y: not _equals(x, y),
        'lt': operator.lt,
        'gt': operator.gt,
        'lte': operator.le,
        'gte': operator.ge,
    }

    _ARITHMETIC_FUNC: ta.Mapping[ArithmeticOperator, ta.Callable[[ta.Any, ta.Any], ta.Any]] = {
        'div': operator.floordiv,
        'divide': operator.truediv,
        'minus': operator.sub,
        'modulo': operator.mod,
        'multiply': operator.mul,
        'plus': operator.add,
    }

    _ARITHMETIC_UNARY_FUNC: ta.Mapping[UnaryArithmeticOperator, ta.Callable[[ta.Any], ta.Any]] = {
        'minus': operator.neg,
        'plus': lambda x: x,
    }

    def __init__(self, dict_cls: type | None = None) -> None:
        super().__init__()

        self._dict_cls = dict_cls or dict

    def type_of(self, value: ta.Any) -> JmespathType | ta.Literal['unknown']:
        if isinstance(value, bool):
            return 'boolean'
        elif isinstance(value, list):
            return 'array'
        elif isinstance(value, dict):
            return 'object'
        elif value is None:
            return 'null'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, (float, int)):
            return 'number'
        elif type(value).__name__ == '_Expression':
            return 'expref'
        else:
            return 'unknown'

    def is_false(self, value: ta.Any) -> bool:
        return (
            value == '' or  # noqa
            value == [] or
            value == {} or
            value is None or
            value is False
        )

    def is_zero_number(self, value: ta.Any) -> bool:
        return _is_actual_number(value) and value == 0

    def make_null(self) -> None:
        return None

    def make_bool(self, value: bool) -> bool:
        return value

    def get_field(self, value: ta.Any, name: str) -> ta.Any:
        try:
            return value.get(name)
        except AttributeError:
            return None

    def get_index(self, value: ta.Any, index: int) -> ta.Any:
        if not isinstance(value, list):
            return None

        try:
            return value[index]
        except IndexError:
            return None

    def slice(self, value: ta.Any, start: int | None, end: int | None, step: int | None) -> ta.Any:
        if isinstance(value, str):
            return value[start:end:step]

        if not isinstance(value, list):
            return None

        return value[slice(start, end, step)]

    def iter_array(self, value: ta.Any) -> ta.Iterable[ta.Any] | None:
        if not isinstance(value, list):
            return None
        return value

    def iter_object_values(self, value: ta.Any) -> ta.Iterable[ta.Any] | None:
        try:
            return value.values()
        except AttributeError:
            return None

    def iter_object_items(self, value: ta.Any) -> ta.Iterable[tuple[str, ta.Any]] | None:
        try:
            return value.items()
        except AttributeError:
            return None

    def make_array(self, values: ta.Iterable[ta.Any]) -> list[ta.Any]:
        return list(values)

    def make_object(self, values: ta.Mapping[str, ta.Any]) -> ta.Any:
        obj = self._dict_cls()
        obj.update(values)
        return obj

    def compare(self, op: ComparatorName, left: ta.Any, right: ta.Any) -> ta.Any:
        comparator_func = self._COMPARATOR_FUNC[op]
        if op in ('eq', 'ne'):
            return comparator_func(left, right)

        if not (_is_comparable(left) and _is_comparable(right)):
            return None
        return comparator_func(left, right)

    def arithmetic_unary(self, op: UnaryArithmeticOperator, value: ta.Any) -> ta.Any:
        return self._ARITHMETIC_UNARY_FUNC[op](value)

    def arithmetic(self, op: ArithmeticOperator, left: ta.Any, right: ta.Any) -> ta.Any:
        return self._ARITHMETIC_FUNC[op](left, right)

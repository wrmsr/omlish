"""
Funcs:
 - Abs
 - Avg
 - Contains
 - Ceil
 - EndsWith
 - Floor
 - Join
 - Keys
 - Length
 - Map
 - Max
 - MaxBy
 - Merge
 - Min
 - MinBy
 - NotNull
 - Reverse
 - Sort
 - SortBy
 - StartsWith
 - Sum
 - ToArray
 - ToString
 - ToNumber
 - Type
 - Values
"""
import json
import typing as ta

from . import nodes as n
from .. import check
from .. import dataclasses as dc
from .. import dispatch
from .. import lang


T = ta.TypeVar('T')


class ValueType(lang.AutoEnum):
    NUMBER = ...
    STRING = ...
    BOOLEAN = ...
    ARRAY = ...
    OBJECT = ...
    NULL = ...


class Arg(ta.Generic[T], lang.Sealed, lang.Interface):
    def value(self) -> T: ...


class ValueArg(dc.Pure, Arg[T]):
    value: T


class NodeArg(dc.Pure, Arg[n.Node]):
    value: n.Node


class Runtime(ta.Generic[T], lang.Interface):

    def is_truthy(self, obj: T) -> bool: ...

    def get_type(self, obj: T) -> ValueType: ...

    def is_null(self, obj: T) -> bool:
        return self.get_type(obj) == ValueType.NULL

    def create_null(self) -> T: ...

    def compare(self, op: n.Compare.Op, left: T, right: T) -> T: ...

    def create_array(self, items: ta.Iterable[T]) -> T: ...

    def create_object(self, fields: ta.Mapping[str, T]) -> T: ...

    def to_iterable(self, obj: T) -> ta.Iterable[T]: ...

    def invoke_function(self, name: str, args: ta.Iterable[Arg]) -> T: ...

    def create_bool(self, value: bool) -> T: ...

    def get_property(self, obj: T, field: str) -> T: ...

    def parse_str(self, s: str) -> T: ...

    def create_str(self, val: str) -> T: ...

    def get_num_var(self, num: int) -> T: ...

    def get_name_var(self, name: str) -> T: ...


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


class Evaluator(ta.Generic[T], dispatch.Class):

    def __init__(self, runtime: Runtime[T]) -> None:
        super().__init__()

        self._runtime = runtime

    __call__ = dispatch.property()

    def __call__(self, node: n.Node, obj: T) -> T:  # type: ignore  # noqa
        raise TypeError(node)

    def __call__(self, node: n.And, obj: T) -> T:  # type: ignore  # noqa
        left = self(node.left, obj)
        if self._runtime.is_truthy(left):
            return self(node.right, obj)
        else:
            return left

    def __call__(self, node: n.Compare, obj: T) -> T:  # type: ignore  # noqa
        left = self(node.left, obj)
        right = self(node.right, obj)
        return self._runtime.compare(node.op, left, right)

    def __call__(self, node: n.CreateArray, obj: T) -> T:  # type: ignore  # noqa
        if self._runtime.is_null(obj):
            return obj
        else:
            return self._runtime.create_array([self(child, obj) for child in node.items])

    def __call__(self, node: n.CreateObject, obj: T) -> T:  # type: ignore  # noqa
        if self._runtime.is_null(obj):
            return obj
        else:
            return self._runtime.create_object({field: self(child, obj) for field, child in node.fields.items()})

    def __call__(self, node: n.Current, obj: T) -> T:  # type: ignore  # noqa
        return obj

    def __call__(self, node: n.ExpressionRef, obj: T) -> T:  # type: ignore  # noqa
        return self(node.expr, obj)

    def __call__(self, node: n.FlattenArray, obj: T) -> T:  # type: ignore  # noqa
        if self._runtime.get_type(obj) == ValueType.ARRAY:
            lst = []
            for item in self._runtime.to_iterable(obj):
                if self._runtime.get_type(item) == ValueType.ARRAY:
                    lst.extend(self._runtime.to_iterable(item))
                else:
                    lst.append(item)
            return lst
        else:
            return self._runtime.create_null()

    def __call__(self, node: n.FlattenObject, obj: T) -> T:  # type: ignore  # noqa
        if self._runtime.get_type(obj) == ValueType.OBJECT:
            return self._runtime.create_array(self._runtime.to_iterable(obj))
        else:
            return self._runtime.create_null()

    def __call__(self, node: n.FunctionCall, obj: T) -> T:  # type: ignore  # noqa
        args = []
        for arg in node.args:
            if isinstance(arg, n.ExpressionRef):
                args.append(NodeArg(arg))
            else:
                args.append(ValueArg(self(arg, obj)))
        return self._runtime.invoke_function(node.name, args)

    def __call__(self, node: n.Index, obj: T) -> T:  # noqa
        if self._runtime.get_type(obj) == ValueType.ARRAY:
            items = self._runtime.to_iterable(obj)
            i = node.value
            if i < 0:
                i = len(items) + 1
            if 0 <= i < len(items):
                return items[i]
        return self._runtime.create_null()

    def __call__(self, node: n.JsonLiteral, obj: T) -> T:  # type: ignore  # noqa
        return self._runtime.parse_str(node.text)

    def __call__(self, node: n.Negate, obj: T) -> T:  # type: ignore  # noqa
        return self._runtime.create_bool(self._runtime.is_truthy(self(node.item, obj)))

    def __call__(self, node: n.Or, obj: T) -> T:  # type: ignore  # noqa
        left = self(node.left, obj)
        if self._runtime.is_truthy(left):
            return left
        else:
            return self(node.right, obj)

    def __call__(self, node: n.Project, obj: T) -> T:  # type: ignore  # noqa
        if self._runtime.get_type(obj) == ValueType.ARRAY:
            items = [
                oitem
                for iitem in self._runtime.to_iterable(obj)
                for oitem in [self(node.child, iitem)]
                if not self._runtime.is_null(oitem)
            ]
            return self._runtime.create_array(items)
        else:
            return self._runtime.create_null()

    def __call__(self, node: n.Property, obj: T) -> T:  # type: ignore  # noqa
        return self._runtime.get_property(obj, node.name)

    def __call__(self, node: n.Selection, obj: T) -> T:  # type: ignore  # noqa
        if self._runtime.get_type(obj) == ValueType.ARRAY:
            items = [
                item
                for item in self._runtime.to_iterable(obj)
                if self._runtime.is_truthy(node.child, item)
            ]
            return self._runtime.create_array(items)
        else:
            return self._runtime.create_null()

    def __call__(self, node: n.Sequence, obj: T) -> T:  # type: ignore  # noqa
        for child in node.items:
            obj = self(child, obj)
        return obj

    def __call__(self, node: n.Slice, obj: T) -> T:  # type: ignore  # noqa
        items = self._runtime.to_iterable(obj)
        step = node.step or 1
        rounding = (step + 1) if (step < 0) else (step - 1)
        limit = -1 if (step < 0) else 0
        start = node.start or limit
        stop = node.stop or (-2**32 if step < 0 else 2**32)
        begin = max(len(items) + start, 0) if (start < 0) else min(start, len(items) + limit)
        end = max(len(items) + stop, limit) if (stop < 0) else min(stop, len(items))
        steps = max(0, (end - begin + rounding) // step)
        lst = []
        i = 0
        offset = begin
        while i < steps:
            lst.append(items[offset])
            offset += step
        return self._runtime.create_array(lst)

    def __call__(self, node: n.String, obj: T) -> T:  # type: ignore  # noqa
        return self._runtime.create_str(node.value)

    def __call__(self, node: n.Parameter, obj: T) -> T:  # type: ignore  # noqa
        if isinstance(node.target, n.Parameter.NameTarget):
            return self._runtime.get_name_var(node.target.value)
        elif isinstance(node.target, n.Parameter.NumberTarget):
            return self._runtime.get_num_var(node.target.value)
        else:
            raise TypeError(node.target)

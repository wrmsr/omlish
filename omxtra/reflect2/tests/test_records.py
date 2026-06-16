# ruff: noqa: F821 PLC0132 SLF001
import collections.abc as cabc
import dataclasses as dc
import typing as ta

import pytest

from ..core import types
from ..core.strconv import type_str
from ..core.typekeys import structural_type_key
from ..core.typekeys import type_key
from ..errors import ReflectionError
from ..queries import get_runtime_type_shape
from ..records import RUNTIME_RECORD_KIND_DATACLASS
from ..records import RUNTIME_RECORD_KIND_NAMEDTUPLE
from ..records import inspect_record
from ..records import inspect_record_or_none
from ..reflect import RuntimeTypeReflector
from ..universe import RuntimeTypeUniverse


def _make_reflector() -> RuntimeTypeReflector:
    return RuntimeTypeReflector(RuntimeTypeUniverse(dynamic_type_name_suffix='counter'))


def test_inspect_record_normalizes_dataclass_fields() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = _make_reflector()

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    inspection = inspect_record(Box[int], reflector)  # type: ignore

    assert inspection.kind == RUNTIME_RECORD_KIND_DATACLASS
    assert inspection.origin is Box
    assert [field.name for field in inspection.fields] == ['value']
    assert type_str(inspection.fields_by_name['value'].typ) == 'builtins.int'
    assert inspection.fields_by_name['value'].type_key == type_key(reflector.reflect_type(int))
    assert inspection.fields_by_name['value'].structural_type_key == reflector.structural_type_key(
        reflector.reflect_type(int),
    )
    assert inspection.fields_by_name['value'].annotation is int


def test_inspect_record_normalizes_namedtuple_fields() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = _make_reflector()

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: list[t_var]  # type: ignore

    inspection = inspect_record(Box[str], reflector)  # type: ignore

    assert inspection.kind == RUNTIME_RECORD_KIND_NAMEDTUPLE
    assert inspection.origin is Box
    assert [field.name for field in inspection.fields] == ['value']
    assert type_str(inspection.fields_by_name['value'].typ) == 'builtins.list[builtins.str]'
    assert inspection.fields_by_name['value'].type_key == type_key(reflector.reflect_type(list[str]))
    assert inspection.fields_by_name['value'].structural_type_key == reflector.structural_type_key(
        reflector.reflect_type(list[str]),
    )
    assert inspection.fields_by_name['value'].annotation == list[str]


def test_inspect_record_treats_callable_fields_as_data_fields() -> None:
    @dc.dataclass
    class HasCallback:
        callback: ta.Callable[[int], str]

        def method(self, value: int) -> str:
            return str(value)

    inspection = inspect_record(HasCallback, _make_reflector())

    assert [field.name for field in inspection.fields] == ['callback']
    assert 'method' not in inspection.fields_by_name
    assert isinstance(inspection.fields_by_name['callback'].typ, types.CallableType)
    assert ta.get_origin(inspection.fields_by_name['callback'].annotation) is cabc.Callable


def test_inspect_record_preserves_literal_new_type_annotation_and_exposes_effective_shape() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    @dc.dataclass
    class Config:
        mode: ta.Any

    Config.__annotations__['mode'] = mode

    reflector = _make_reflector()
    inspection = inspect_record(Config, reflector)
    field = inspection.fields_by_name['mode']
    shape = get_runtime_type_shape(field.typ, reflector)

    assert field.annotation is mode
    assert shape.new_type is not None
    assert shape.new_type.obj is mode
    assert shape.literal_value_type is not None
    assert shape.literal_value_type.values == ('a', 'b')


def test_inspect_record_preserves_generic_namedtuple_literal_new_type_shape() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    reflector = _make_reflector()
    inspection = inspect_record(Box[mode], reflector)  # type: ignore
    field = inspection.fields_by_name['value']
    shape = get_runtime_type_shape(field.typ, reflector)

    assert inspection.kind == RUNTIME_RECORD_KIND_NAMEDTUPLE
    assert field.annotation is mode
    assert field.type_key == type_key(reflector.reflect_type(mode))
    assert shape.new_type is not None
    assert shape.new_type.obj is mode
    assert shape.literal_value_type is not None
    assert shape.literal_value_type.values == ('a', 'b')


def test_inspect_record_exposes_structural_field_key_for_alias_field() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    @dc.dataclass
    class Config:
        modes: mode_list  # type: ignore

    reflector = _make_reflector()
    field = inspect_record(Config, reflector).fields_by_name['modes']

    assert field.type_key != field.structural_type_key
    assert field.structural_type_key == reflector.structural_type_key(reflector.reflect_type(list[mode]))  # noqa


def test_inspect_record_exposes_structural_field_key_for_recursive_alias_field() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore

    @dc.dataclass
    class Config:
        node: alias  # type: ignore

    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )
    field = inspect_record(Config, reflector).fields_by_name['node']
    unrolled = reflector.reflect_type(int | list[alias])  # type: ignore

    assert field.annotation is alias
    assert field.structural_type_key == structural_type_key(unrolled)


def test_inspect_record_cache_is_per_reflector() -> None:
    @dc.dataclass
    class Item:
        value: int

    left_reflector = _make_reflector()
    right_reflector = _make_reflector()

    left = inspect_record(Item, left_reflector)

    assert inspect_record(Item, left_reflector) is left
    assert inspect_record(Item, right_reflector) is not left


def test_inspect_record_or_none_returns_none_for_unsupported_class() -> None:
    class Plain:
        value: int

    assert inspect_record_or_none(Plain, _make_reflector()) is None


def test_inspect_record_raises_for_unsupported_class() -> None:
    class Plain:
        value: int

    with pytest.raises(ReflectionError, match='record source'):
        inspect_record(Plain, _make_reflector())

# ruff: noqa: F821 PLC0132 SLF001
import typing as ta

import pytest

from ...core import types
from ...core.strconv import type_str
from ...core.typekeys import structural_type_key
from ...core.typekeys import type_key
from ...errors import ReflectionError
from ...reflect import TypeReflector
from ...universe import TypeUniverse
from ..namedtuples import inspect_namedtuple
from ..namedtuples import is_namedtuple
from ..namedtuples import reflect_namedtuple_field_annotations
from ..namedtuples import reflect_namedtuple_field_structural_type_keys
from ..namedtuples import reflect_namedtuple_field_type_keys
from ..namedtuples import reflect_namedtuple_field_types
from ..namedtuples import reflect_namedtuple_fields
from ..queries import get_runtime_type_shape


def _make_reflector() -> TypeReflector:
    return TypeReflector(TypeUniverse(dynamic_type_name_suffix='counter'))


def test_is_namedtuple_accepts_typing_namedtuple_class() -> None:
    class Point(ta.NamedTuple):
        x: int
        y: str

    assert is_namedtuple(Point)


def test_is_namedtuple_rejects_plain_tuple_subclass() -> None:
    class Plain(tuple):  # noqa
        pass

    assert not is_namedtuple(Plain)


def test_inspect_namedtuple_exposes_ordered_fields_and_annotations() -> None:
    class Point(ta.NamedTuple):
        x: int
        y: str

    inspection = inspect_namedtuple(Point, _make_reflector())

    assert inspection.origin is Point
    assert [field.name for field in inspection.fields] == ['x', 'y']
    assert [*inspection.fields_by_name] == ['x', 'y']
    assert [*inspection.field_types] == ['x', 'y']
    assert [*inspection.field_type_keys] == ['x', 'y']
    assert inspection.field_annotations == {'x': int, 'y': str}
    assert [type_str(field.replaced_type) for field in inspection.fields] == ['builtins.int', 'builtins.str']


def test_reflect_namedtuple_fields_replaces_type_var_for_parameterized_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore
        values: list[t_var]  # type: ignore

    fields = reflect_namedtuple_fields(Box[int], _make_reflector())  # type: ignore

    assert [field.name for field in fields] == ['value', 'values']
    assert isinstance(fields[0].raw_type, types.TypeVarType)
    assert [type_str(field.replaced_type) for field in fields] == [
        'builtins.int',
        'builtins.list[builtins.int]',
    ]


def test_reflect_namedtuple_fields_replaces_type_var_tuple_for_parameterized_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[*ts_var]):  # type: ignore
        values: tuple[*ts_var]  # type: ignore

    reflector = _make_reflector()
    [field] = reflect_namedtuple_fields(Box[int, str], reflector)  # type: ignore

    assert field.name == 'values'
    assert type_str(field.raw_type) == 'tuple[Unpack[Ts]]'
    assert type_str(field.replaced_type) == 'tuple[builtins.int, builtins.str]'
    assert reflector.to_runtime_annotation(field.replaced_type) == tuple[int, str]
    assert reflect_namedtuple_field_annotations(Box[int, str], reflector) == {'values': tuple[int, str]}  # type: ignore


def test_reflect_namedtuple_fields_replaces_type_var_tuple_with_fixed_edges() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var, *ts_var, u_var]):  # type: ignore
        values: tuple[t_var, *ts_var, u_var]  # type: ignore

    inspection = inspect_namedtuple(Box[int, str, bool, bytes], _make_reflector())  # type: ignore
    field = inspection.fields_by_name['values']

    assert type_str(field.raw_type) == 'tuple[T, Unpack[Ts], U]'
    assert type_str(field.replaced_type) == 'tuple[builtins.int, builtins.str, builtins.bool, builtins.bytes]'
    assert inspection.field_annotations == {'values': tuple[int, str, bool, bytes]}


def test_reflect_namedtuple_field_with_variadic_alias_expands_and_can_preserve_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[*ts_var]):  # type: ignore
        values: alias[*ts_var]  # type: ignore

    reflector = _make_reflector()
    inspection = inspect_namedtuple(Box[int, str], reflector)  # type: ignore
    field = inspection.fields_by_name['values']

    assert type_str(field.replaced_type) == f'{__name__}.Alias[tuple[builtins.int, builtins.str]]'
    assert inspection.field_annotations == {'values': tuple[int, str]}
    assert reflector.to_runtime_annotation(
        field.replaced_type,
        type_alias_policy='preserve',
    ) == alias[int, str]


def test_reflect_namedtuple_field_types_accepts_parameterized_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Pair(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        left: t_var  # type: ignore
        right: tuple[t_var, str]  # type: ignore

    field_types = reflect_namedtuple_field_types(Pair[int], _make_reflector())  # type: ignore

    assert [*field_types] == ['left', 'right']
    assert type_str(field_types['left']) == 'builtins.int'
    assert type_str(field_types['right']) == 'tuple[builtins.int, builtins.str]'


def test_reflect_namedtuple_field_annotations_returns_runtime_annotations() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: list[t_var]  # type: ignore

    assert reflect_namedtuple_field_annotations(Box[str], _make_reflector()) == {'value': list[str]}  # type: ignore


def test_reflect_namedtuple_field_type_keys_returns_replaced_type_keys() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = _make_reflector()

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: list[t_var]  # type: ignore

    field_keys = reflect_namedtuple_field_type_keys(Box[str], reflector)  # type: ignore

    assert field_keys == {'value': type_key(reflector.reflect_type(list[str]))}


def test_generic_namedtuple_replaces_field_with_literal_new_type() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    reflector = _make_reflector()
    inspection = inspect_namedtuple(Box[mode], reflector)  # type: ignore
    field = inspection.fields_by_name['value']
    shape = get_runtime_type_shape(field.replaced_type, reflector)

    assert isinstance(field.raw_type, types.TypeVarType)
    assert inspection.field_annotations == {'value': mode}
    assert reflect_namedtuple_field_annotations(Box[mode], reflector) == {'value': mode}  # type: ignore
    assert shape.new_type is not None
    assert shape.new_type.obj is mode
    assert shape.literal_value_type is not None
    assert shape.literal_value_type.values == ('a', 'b')


def test_generic_namedtuple_literal_new_type_field_keys_preserve_new_type_identity() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    reflector = _make_reflector()
    mode_fields = inspect_namedtuple(Box[mode], reflector).field_type_keys  # type: ignore
    other_fields = inspect_namedtuple(Box[other_mode], reflector).field_type_keys  # type: ignore

    assert mode_fields['value'] != other_fields['value']
    assert mode_fields['value'] == type_key(reflector.reflect_type(mode))
    assert other_fields['value'] == type_key(reflector.reflect_type(other_mode))


def test_namedtuple_alias_field_structural_type_key_matches_expanded_type() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    class Config(ta.NamedTuple):
        modes: mode_list  # type: ignore

    reflector = _make_reflector()
    inspection = inspect_namedtuple(Config, reflector)

    assert inspection.field_type_keys['modes'] != inspection.field_structural_type_keys['modes']
    assert inspection.field_structural_type_keys['modes'] == reflector.structural_type_key(
        reflector.reflect_type(list[mode]),  # noqa
    )
    assert reflect_namedtuple_field_structural_type_keys(Config, reflector) == inspection.field_structural_type_keys


def test_namedtuple_recursive_alias_field_structural_type_key_matches_unrolled_type() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore

    class Config(ta.NamedTuple):
        node: alias  # type: ignore

    reflector = TypeReflector(
        TypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )
    inspection = inspect_namedtuple(Config, reflector)
    unrolled = reflector.reflect_type(int | list[alias])  # type: ignore

    assert inspection.field_annotations == {'node': alias}
    assert inspection.field_structural_type_keys['node'] == structural_type_key(unrolled)


def test_inspect_namedtuple_cache_is_per_reflector() -> None:
    class Item(ta.NamedTuple):
        value: int

    left_reflector = _make_reflector()
    right_reflector = _make_reflector()

    left = inspect_namedtuple(Item, left_reflector)

    assert inspect_namedtuple(Item, left_reflector) is left
    assert inspect_namedtuple(Item, right_reflector) is not left


def test_inspect_namedtuple_rejects_non_namedtuple() -> None:
    class Plain(tuple):  # noqa
        pass

    with pytest.raises(ReflectionError, match='namedtuple source'):
        inspect_namedtuple(Plain, _make_reflector())


def test_inspect_namedtuple_fails_closed_for_missing_annotation() -> None:
    class Point(ta.NamedTuple):
        x: int

    del Point.__annotations__['x']

    with pytest.raises(ReflectionError, match='Missing namedtuple field annotation'):
        inspect_namedtuple(Point, _make_reflector())

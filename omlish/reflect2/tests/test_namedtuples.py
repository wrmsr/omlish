# ruff: noqa: F821 PLC0132 SLF001
import typing as ta

import pytest

from ..api import Api
from ..core import types
from ..core.strconv import type_str
from ..core.typekeys import type_key
from ..errors import ReflectionError
from ..namedtuples import is_namedtuple


def make_api(**kwargs: ta.Any) -> Api:
    return Api(
        dynamic_type_name_suffix='counter',
        **kwargs,
    )


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

    api = make_api()
    inspection = api.inspect_namedtuple(Point)

    assert inspection.origin is Point
    assert [field.name for field in inspection.fields] == ['x', 'y']
    assert [*inspection.fields_by_name] == ['x', 'y']
    assert [type_str(field.replaced_type) for field in inspection.fields] == ['builtins.int', 'builtins.str']


def test_reflect_namedtuple_fields_replaces_type_var_for_parameterized_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore
        values: list[t_var]  # type: ignore

    api = make_api()
    fields = api.inspect_namedtuple(Box[int]).fields  # type: ignore

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

    api = make_api()
    [field] = api.inspect_namedtuple(Box[int, str]).fields  # type: ignore

    assert field.name == 'values'
    assert type_str(field.raw_type) == 'tuple[Unpack[Ts]]'
    assert type_str(field.replaced_type) == 'tuple[builtins.int, builtins.str]'
    assert api.to_runtime_annotation(field.replaced_type) == tuple[int, str]


def test_reflect_namedtuple_fields_replaces_type_var_tuple_with_fixed_edges() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var, *ts_var, u_var]):  # type: ignore
        values: tuple[t_var, *ts_var, u_var]  # type: ignore

    api = make_api()
    inspection = api.inspect_namedtuple(Box[int, str, bool, bytes])  # type: ignore
    field = inspection.fields_by_name['values']

    assert type_str(field.raw_type) == 'tuple[T, Unpack[Ts], U]'
    assert type_str(field.replaced_type) == 'tuple[builtins.int, builtins.str, builtins.bool, builtins.bytes]'


def test_reflect_namedtuple_field_with_variadic_alias_expands_and_can_preserve_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[*ts_var]):  # type: ignore
        values: alias[*ts_var]  # type: ignore

    api = make_api()
    inspection = api.inspect_namedtuple(Box[int, str])  # type: ignore
    field = inspection.fields_by_name['values']

    assert type_str(field.replaced_type) == f'{__name__}.Alias[tuple[builtins.int, builtins.str]]'
    assert api.to_runtime_annotation(
        field.replaced_type,
        type_alias_policy='preserve',
    ) == alias[int, str]


def test_reflect_namedtuple_field_types_accepts_parameterized_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Pair(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        left: t_var  # type: ignore
        right: tuple[t_var, str]  # type: ignore

    api = make_api()
    fields = api.inspect_namedtuple(Pair[int]).fields_by_name  # type: ignore

    assert [*fields] == ['left', 'right']
    assert type_str(fields['left'].replaced_type) == 'builtins.int'
    assert type_str(fields['right'].replaced_type) == 'tuple[builtins.int, builtins.str]'


def test_reflect_namedtuple_field_annotations_returns_runtime_annotations() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: list[t_var]  # type: ignore

    api = make_api()
    assert api.to_runtime_annotation(api.inspect_namedtuple(Box[str]).fields[0].replaced_type) == list[str]  # type: ignore  # noqa


def test_generic_namedtuple_replaces_field_with_literal_new_type() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    api = make_api()
    inspection = api.inspect_namedtuple(Box[mode])  # type: ignore
    field = inspection.fields_by_name['value']
    # shape = get_runtime_type_shape(field.replaced_type, reflector)

    assert isinstance(field.raw_type, types.TypeVarType)
    assert api.to_runtime_annotation(field.replaced_type) == mode
    # assert shape.new_type is not None
    # assert shape.new_type.obj is mode
    # assert shape.literal_value_type is not None
    # assert shape.literal_value_type.values == ('a', 'b')


def test_generic_namedtuple_literal_new_type_field_keys_preserve_new_type_identity() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore

    class Box(ta.NamedTuple, ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    api = make_api()
    [mode_field] = api.inspect_namedtuple(Box[mode]).fields  # type: ignore
    [other_field] = api.inspect_namedtuple(Box[other_mode]).fields  # type: ignore

    mode_key = type_key(mode_field.replaced_type)
    other_key = type_key(other_field.replaced_type)

    assert mode_key != other_key
    assert mode_key == type_key(api.reflect_type(mode))
    assert other_key == type_key(api.reflect_type(other_mode))


def test_namedtuple_alias_field_structural_type_key_matches_expanded_type() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    class Config(ta.NamedTuple):
        modes: mode_list  # type: ignore

    api = make_api()
    inspection = api.inspect_namedtuple(Config)

    assert type_key(inspection.fields_by_name['modes'].replaced_type) != \
           type_key(inspection.fields_by_name['modes'].replaced_type, 'structural')
    assert type_key(inspection.fields_by_name['modes'].replaced_type, 'structural') == \
           type_key(api.reflect_type(list[mode]), 'structural')  # noqa


def test_namedtuple_recursive_alias_field_structural_type_key_matches_unrolled_type() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore

    class Config(ta.NamedTuple):
        node: alias  # type: ignore

    api = make_api(
        forward_ref_resolver=lambda frr: {'Node': alias}[frr.name],
    )
    inspection = api.inspect_namedtuple(Config)
    [field] = inspection.fields
    unrolled = api.reflect_type(int | list[alias])  # type: ignore

    assert api.to_runtime_annotation(field.replaced_type) == alias
    assert type_key(field.replaced_type, 'structural') == type_key(unrolled, 'structural')


def test_inspect_namedtuple_rejects_non_namedtuple() -> None:
    class Plain(tuple):  # noqa
        pass

    api = make_api()
    with pytest.raises(ReflectionError, match='namedtuple source'):
        api.inspect_namedtuple(Plain)


def test_inspect_namedtuple_fails_closed_for_missing_annotation() -> None:
    class Point(ta.NamedTuple):
        x: int

    del Point.__annotations__['x']

    api = make_api()
    with pytest.raises(ReflectionError, match='Missing namedtuple field annotation'):
        api.inspect_namedtuple(Point)

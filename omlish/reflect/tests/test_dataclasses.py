# ruff: noqa: F821 PLC0132 SLF001
# ruff: noqa: PYI059
import dataclasses as dc
import typing as ta

import pytest

from ..annotations import to_runtime_annotation
from ..core import types
from ..core.strconv import type_str
from ..core.typekeys import TypeKey
from ..core.typekeys import type_key
from ..dataclasses import DataclassField
from ..dataclasses import inspect_dataclass
from ..errors import ReflectionError
from ..errors import UnreflectableTypeError
from ..errors import UnsupportedTypeOperationError
from .helpers import make_mirror


def field_runtime_annotations(fields: ta.Iterable[DataclassField]) -> dict[str, ta.Any]:
    return {
        field.name: to_runtime_annotation(field.replaced_type)
        for field in fields
    }


def field_type_keys(
        fields: ta.Iterable[DataclassField],
        *,
        policy: ta.Any = 'default',
) -> dict[str, TypeKey]:
    return {
        field.name: type_key(field.replaced_type, policy)
        for field in fields
    }


def test_reflect_dataclass_fields_replaces_inherited_type_var() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        v: t_var  # type: ignore

    @dc.dataclass
    class IntBox(Box[int]):  # type: ignore
        pass

    mirror = make_mirror()
    [field] = inspect_dataclass(IntBox, mirror=mirror).fields

    assert field.name == 'v'
    assert field.owner is Box
    assert isinstance(field.raw_type, types.TypeVarType)
    assert type_str(field.replaced_type) == 'builtins.int'


def test_reflect_dataclass_fields_replaces_inherited_type_var_tuple() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[*ts_var]):  # type: ignore
        values: tuple[*ts_var]  # type: ignore

    @dc.dataclass
    class IntStrBox(Box[int, str]):  # type: ignore
        pass

    mirror = make_mirror()
    [field] = inspect_dataclass(IntStrBox, mirror=mirror).fields

    assert field.name == 'values'
    assert field.owner is Box
    assert type_str(field.raw_type) == 'tuple[Unpack[Ts]]'
    assert type_str(field.replaced_type) == 'tuple[builtins.int, builtins.str]'
    assert to_runtime_annotation(field.replaced_type) == tuple[int, str]
    assert field_runtime_annotations([field]) == {'values': tuple[int, str]}


def test_reflect_dataclass_fields_replaces_inherited_type_var_tuple_with_fixed_edges() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var, *ts_var, u_var]):  # type: ignore
        values: tuple[t_var, *ts_var, u_var]  # type: ignore

    @dc.dataclass
    class MixedBox(Box[int, str, bool, bytes]):  # type: ignore
        pass

    mirror = make_mirror()
    inspection = inspect_dataclass(MixedBox, mirror=mirror)
    field = inspection.fields_by_name['values']

    assert type_str(field.raw_type) == 'tuple[T, Unpack[Ts], U]'
    assert type_str(field.replaced_type) == 'tuple[builtins.int, builtins.str, builtins.bool, builtins.bytes]'
    assert field_runtime_annotations([field]) == {'values': tuple[int, str, bool, bytes]}


def test_reflect_dataclass_field_with_variadic_alias_expands_and_can_preserve_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[*ts_var]):  # type: ignore
        values: alias[*ts_var]  # type: ignore

    @dc.dataclass
    class IntStrBox(Box[int, str]):  # type: ignore
        pass

    mirror = make_mirror()
    inspection = inspect_dataclass(IntStrBox, mirror=mirror)
    field = inspection.fields_by_name['values']

    assert type_str(field.replaced_type) == f'{__name__}.Alias[tuple[builtins.int, builtins.str]]'
    assert field_runtime_annotations([field]) == {'values': tuple[int, str]}
    assert to_runtime_annotation(
        field.replaced_type,
        type_alias_policy='preserve',
    ) == alias[int, str]


def test_reflect_dataclass_field_types_accepts_parameterized_dataclass_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        v: t_var  # type: ignore

    mirror = make_mirror()
    inspection = inspect_dataclass(Box[str], mirror=mirror)  # type: ignore

    assert type_str(inspection.fields_by_name['v'].replaced_type) == 'builtins.str'


def test_inspect_dataclass_exposes_ordered_fields_and_maps() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore

    @dc.dataclass
    class Base(ta.Generic[t_var]):  # type: ignore
        first: t_var  # type: ignore
        second: str

    @dc.dataclass
    class Child(ta.Generic[u_var], Base[int]):  # type: ignore
        third: list[u_var]  # type: ignore

    mirror = make_mirror()
    inspection = inspect_dataclass(Child[str], mirror=mirror)  # type: ignore

    assert inspection.origin is Child
    assert [field.name for field in inspection.fields] == ['first', 'second', 'third']
    assert [*inspection.fields_by_name] == ['first', 'second', 'third']


def test_reflect_dataclass_field_annotations_returns_replaced_runtime_annotations() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        v: t_var  # type: ignore

    mirror = make_mirror()
    di = inspect_dataclass(Box[int], mirror=mirror)  # type: ignore
    assert field_runtime_annotations(di.fields) == {'v': int}


# def test_dataclass_literal_new_type_field_preserves_annotation_and_exposes_effective_shape() -> None:
#     mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
#
#     @dc.dataclass
#     class Config:
#         mode: ta.Any
#
#     Config.__annotations__['mode'] = mode
#
#     mirror = make_mirror()
#     inspection = api.inspect_dataclass(Config)
#     field_type = inspection.fields_by_name['mode'].replaced_type
#     shape = get_runtime_type_shape(field_type)
#
#     assert inspection.field_annotations == {'mode': mode}
#     assert reflect_dataclass_field_annotations(Config) == {'mode': mode}
#     assert shape.new_type is not None
#     assert shape.new_type.obj is mode
#     assert shape.literal_value_type is not None
#     assert shape.literal_value_type.values == ('a', 'b')


def test_inspect_dataclass_excludes_classvar_and_initvar_pseudo_fields() -> None:
    @dc.dataclass
    class Item:
        shared: ta.ClassVar[int] = 1
        init_only: dc.InitVar[str] = 'x'
        value: int = 2

    mirror = make_mirror()
    inspection = inspect_dataclass(Item, mirror=mirror)

    assert [field.name for field in inspection.fields] == ['value']
    assert field_runtime_annotations(inspection.fields) == {'value': int}


def test_reflect_dataclass_fields_replaces_each_generic_layer() -> None:
    a_var = ta.TypeVar('A')  # type: ignore
    b_var = ta.TypeVar('B')  # type: ignore
    x_var = ta.TypeVar('X')  # type: ignore
    y_var = ta.TypeVar('Y')  # type: ignore

    @dc.dataclass
    class Base(ta.Generic[a_var, b_var]):  # type: ignore
        left: a_var  # type: ignore
        right: b_var  # type: ignore

    @dc.dataclass
    class Middle(ta.Generic[x_var], Base[list[x_var], str]):  # type: ignore
        middle: x_var  # type: ignore

    @dc.dataclass
    class Child(ta.Generic[y_var], Middle[dict[str, y_var]]):  # type: ignore
        child: y_var  # type: ignore

    mirror = make_mirror()
    fields = inspect_dataclass(Child[int], mirror=mirror).fields  # type: ignore

    assert [
        (
            field.name,
            field.owner.__name__,
            type_str(field.replaced_type),
        )
        for field in fields
    ] == [
        ('left', 'Base', 'builtins.list[builtins.dict[builtins.str, builtins.int]]'),
        ('right', 'Base', 'builtins.str'),
        ('middle', 'Middle', 'builtins.dict[builtins.str, builtins.int]'),
        ('child', 'Child', 'builtins.int'),
    ]


# def test_generic_dataclass_replaces_inherited_field_with_literal_new_type() -> None:
#     t_var = ta.TypeVar('T')  # type: ignore
#     mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
#
#     @dc.dataclass
#     class Box(ta.Generic[t_var]):  # type: ignore
#         value: t_var  # type: ignore
#
#     @dc.dataclass
#     class ModeBox(Box[mode]):  # type: ignore
#         pass
#
#     dr = make_dataclass_inspector()
#     inspection = inspect_dataclass(ModeBox)
#     field = inspection.fields_by_name['value']
#     shape = get_runtime_type_shape(field.replaced_type)
#
#     assert field.owner is Box
#     assert isinstance(field.raw_type, types.TypeVarType)
#     assert inspection.field_annotations == {'value': mode}
#     assert reflect_dataclass_field_annotations(ModeBox) == {'value': mode}
#     assert shape.new_type is not None
#     assert shape.new_type.obj is mode
#     assert shape.literal_value_type is not None
#     assert shape.literal_value_type.values == ('a', 'b')


def test_generic_dataclass_literal_newtype_field_keys_preserve_new_type_identity() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    mirror = make_mirror()
    mode_fields = field_type_keys(inspect_dataclass(Box[mode], mirror=mirror).fields)  # type: ignore
    other_fields = field_type_keys(inspect_dataclass(Box[other_mode], mirror=mirror).fields)  # type: ignore

    assert mode_fields['value'] != other_fields['value']
    assert mode_fields['value'] == type_key(mirror.reflect_type(mode))
    assert other_fields['value'] == type_key(mirror.reflect_type(other_mode))


# def test_dataclass_field_with_new_type_literal_alias_expands_to_collection_shape() -> None:
#     mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
#     mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore
#
#     @dc.dataclass
#     class Config:
#         modes: mode_list  # type: ignore
#
#     dr = make_dataclass_inspector()
#     inspection = inspect_dataclass(Config)
#     field = inspection.fields_by_name['modes']
#     collection_shape = get_runtime_collection_shape(field.replaced_type)
#
#     assert inspection.field_annotations == {'modes': list[mode]}  # noqa
#     assert reflect_dataclass_field_annotations(Config) == {'modes': list[mode]}  # noqa
#     assert type_str(field.replaced_type).endswith('.ModeList')
#     assert inspection.field_type_keys['modes'] != inspection.field_structural_type_keys['modes']
#     assert inspection.field_structural_type_keys['modes'] == mirror.structural_type_key(
#         mirror.reflect_type(list[mode]),  # noqa
#     )
#     assert reflect_dataclass_field_structural_type_keys(Config) == inspection.field_structural_type_keys
#     assert collection_shape.sequence_item is not None
#     item_shape = get_runtime_type_shape(collection_shape.sequence_item)
#     assert item_shape.new_type is not None
#     assert item_shape.new_type.obj is mode
#     assert item_shape.literal_value_type is not None
#     assert item_shape.literal_value_type.values == ('a', 'b')
#     assert type_key(field.replaced_type) != type_key(mirror.reflect_type(list[ta.Literal['a', 'b']]))


# def test_dataclass_field_with_annotated_new_type_alias_has_nominal_and_structural_views() -> None:
#     mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
#     mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore
#
#     @dc.dataclass
#     class Config:
#         modes: ta.Annotated[mode_list, 'cfg']  # type: ignore
#
#     dr = make_dataclass_inspector()
#     field = inspect_dataclass(Config).fields_by_name['modes']
#     expanded = mirror.reflect_type(ta.Annotated[list[mode], 'cfg'])  # noqa
#     shape = get_runtime_type_shape(field.replaced_type)
#
#     assert shape.annotated is not None
#     assert shape.annotated.metadata == ('cfg',)
#     assert shape.alias is not None
#     assert shape.alias.obj is mode_list
#     assert type_key(field.replaced_type) != type_key(expanded)
#     assert is_structurally_equivalent(field.replaced_type, expanded)
#     assert is_structural_subtype(field.replaced_type, expanded)
#     assert mirror.to_runtime_annotation(field.replaced_type) == ta.Annotated[list[mode], 'cfg']  # noqa
#     assert mirror.to_runtime_annotation(
#         field.replaced_type,
#         type_alias_policy='preserve',
#     ) == ta.Annotated[mode_list, 'cfg']


# def test_dataclass_recursive_alias_field_structural_key_matches_unrolled_field_type() -> None:
#     alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
#
#     @dc.dataclass
#     class Config:
#         node: alias  # type: ignore
#
#     dr = make_dataclass_inspector()
#     mirror = Mirror(
#         TypeUniverse(),
#         forward_ref_resolver={'Node': alias}.__getitem__,
#     )
#     field = inspect_dataclass(Config).fields_by_name['node']
#     unrolled = mirror.reflect_type(int | list[alias])  # type: ignore
#     wrapper = mirror.reflect_type(tuple[int | list[alias]])  # type: ignore
#     alias_wrapper = mirror.reflect_type(tuple[alias])  # type: ignore
#
#     assert inspect_dataclass(Config).field_annotations == {'node': alias}
#     assert structural_type_key(field.replaced_type) == structural_type_key(unrolled)
#     assert structural_type_key(alias_wrapper) == structural_type_key(wrapper)
#     assert inspect_dataclass(Config).field_structural_type_keys['node'] == structural_type_key(unrolled)


# def test_generic_dataclass_recursive_alias_field_structural_key_survives_substitution() -> None:
#     t_var = ta.TypeVar('T')  # type: ignore
#     alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
#
#     @dc.dataclass
#     class Box(ta.Generic[t_var]):  # type: ignore
#         value: t_var  # type: ignore
#
#     @dc.dataclass
#     class NodeBox(Box[alias]):  # type: ignore
#         pass
#
#     dr = make_dataclass_inspector()
#     mirror = Mirror(
#         TypeUniverse(dynamic_type_name_suffix='counter'),
#         forward_ref_resolver={'Node': alias}.__getitem__,
#     )
#     inspection = inspect_dataclass(NodeBox)
#     field = inspection.fields_by_name['value']
#     unrolled = mirror.reflect_type(int | list[alias])  # type: ignore
#     double_unrolled = mirror.reflect_type(int | list[int | list[alias]])  # type: ignore
#     entries = reflect_mro_entries(NodeBox)
#     box_entry = next(entry for entry in entries if entry.info is mirror.universe.get_type_info(Box))
#
#     assert field.owner is Box
#     assert isinstance(field.raw_type, types.TypeVarType)
#     assert structural_type_key(field.replaced_type) == structural_type_key(box_entry.args[0])
#     assert inspection.field_annotations == {'value': alias}
#     assert inspection.field_structural_type_keys['value'] == structural_type_key(unrolled)
#     assert inspection.field_structural_type_keys['value'] == structural_type_key(double_unrolled)
#     assert mirror.structural_type_key(box_entry.args[0]) == structural_type_key(unrolled)


# def test_dataclass_field_with_generic_new_type_literal_alias_expands_to_collection_shape() -> None:
#     t_var = ta.TypeVar('T')  # type: ignore
#     mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
#     box_alias = ta.TypeAliasType('BoxAlias', list[t_var], type_params=(t_var,))  # type: ignore
#
#     @dc.dataclass
#     class Config:
#         modes: box_alias[mode]  # type: ignore
#
#     dr = make_dataclass_inspector()
#     inspection = inspect_dataclass(Config)
#     field = inspection.fields_by_name['modes']
#     collection_shape = get_runtime_collection_shape(field.replaced_type)
#
#     assert inspection.field_annotations == {'modes': list[mode]}  # noqa
#     assert reflect_dataclass_field_annotations(Config) == {'modes': list[mode]}  # noqa
#     assert collection_shape.sequence_item is not None
#     item_shape = get_runtime_type_shape(collection_shape.sequence_item)
#     assert item_shape.new_type is not None
#     assert item_shape.new_type.obj is mode
#     assert item_shape.literal_value_type is not None
#     assert item_shape.literal_value_type.values == ('a', 'b')


def test_reflect_dataclass_fields_uses_overriding_field_owner() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Base(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    @dc.dataclass
    class Child(Base[int]):  # type: ignore
        value: str

    mirror = make_mirror()
    [field] = inspect_dataclass(Child, mirror=mirror).fields

    assert field.owner is Child
    assert type_str(field.raw_type) == 'builtins.str'
    assert type_str(field.replaced_type) == 'builtins.str'


def test_reflect_dataclass_fields_rejects_non_dataclass() -> None:
    class NotDataclass:
        pass

    mirror = make_mirror()
    with pytest.raises(ReflectionError, match='dataclass source'):
        inspect_dataclass(NotDataclass, mirror=mirror)


def test_reflect_dataclass_fields_fails_closed_for_unmappable_owner() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Base(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    @dc.dataclass
    class Child(Base[int]):  # type: ignore
        pass

    mirror = make_mirror()
    child_type = mirror.reflect_type(Child)
    base_type = mirror.reflect_type(Base)
    assert isinstance(child_type, types.Instance)
    assert isinstance(base_type, types.Instance)
    child_type.type._mro = (child_type.type, base_type.type)
    child_type.type._bases = ()

    with pytest.raises(UnsupportedTypeOperationError):
        inspect_dataclass(Child, mirror=mirror)


def test_inspect_dataclass_fails_closed_for_unreflectable_alias_annotation() -> None:
    bad_alias = ta.TypeAliasType('BadAlias', ta.TypeIs[int])  # type: ignore

    @dc.dataclass
    class Config:
        value: bad_alias  # type: ignore

    mirror = make_mirror()
    with pytest.raises(UnreflectableTypeError, match='TypeIs'):
        inspect_dataclass(Config, mirror=mirror)

    # assert ('dataclass', Config) not in api.dataclasses._inspection_cache


def test_reflect_dataclass_field_annotations_emit_replaced_runtime_annotations() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: list[t_var]  # type: ignore

    @dc.dataclass
    class IntBox(Box[int]):  # type: ignore
        pass

    mirror = make_mirror()
    di = inspect_dataclass(IntBox, mirror=mirror)
    annotations = field_runtime_annotations(di.fields)

    assert annotations == {'value': list[int]}

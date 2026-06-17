# ruff: noqa: F821 PLC0132 SLF001
# ruff: noqa: PYI059
import dataclasses as dc
import typing as ta

import pytest

from ...core import types
from ...core.strconv import type_str
from ...core.subtypes import is_structural_subtype
from ...core.subtypes import is_structurally_equivalent
from ...core.typekeys import structural_type_key
from ...core.typekeys import type_key
from ...errors import ReflectionError
from ...errors import UnreflectableTypeError
from ...errors import UnsupportedTypeOperationError
from ...reflect import TypeReflector
from ...universe import TypeUniverse
from ..dataclasses import inspect_dataclass
from ..dataclasses import reflect_dataclass_field_annotations
from ..dataclasses import reflect_dataclass_field_structural_type_keys
from ..dataclasses import reflect_dataclass_field_type_keys
from ..dataclasses import reflect_dataclass_field_types
from ..dataclasses import reflect_dataclass_fields
from ..ops import reflect_mro_entries
from ..queries import get_runtime_collection_shape
from ..queries import get_runtime_type_shape


def _make_reflector() -> TypeReflector:
    return TypeReflector(TypeUniverse(dynamic_type_name_suffix='counter'))


def test_reflect_dataclass_fields_replaces_inherited_type_var() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        v: t_var  # type: ignore

    @dc.dataclass
    class IntBox(Box[int]):  # type: ignore
        pass

    [field] = reflect_dataclass_fields(IntBox, _make_reflector())

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

    reflector = _make_reflector()
    [field] = reflect_dataclass_fields(IntStrBox, reflector)

    assert field.name == 'values'
    assert field.owner is Box
    assert type_str(field.raw_type) == 'tuple[Unpack[Ts]]'
    assert type_str(field.replaced_type) == 'tuple[builtins.int, builtins.str]'
    assert reflector.to_runtime_annotation(field.replaced_type) == tuple[int, str]
    assert reflect_dataclass_field_annotations(IntStrBox, reflector) == {'values': tuple[int, str]}


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

    inspection = inspect_dataclass(MixedBox, _make_reflector())
    field = inspection.fields_by_name['values']

    assert type_str(field.raw_type) == 'tuple[T, Unpack[Ts], U]'
    assert type_str(field.replaced_type) == 'tuple[builtins.int, builtins.str, builtins.bool, builtins.bytes]'
    assert inspection.field_annotations == {'values': tuple[int, str, bool, bytes]}


def test_reflect_dataclass_field_with_variadic_alias_expands_and_can_preserve_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[*ts_var]):  # type: ignore
        values: alias[*ts_var]  # type: ignore

    @dc.dataclass
    class IntStrBox(Box[int, str]):  # type: ignore
        pass

    reflector = _make_reflector()
    inspection = inspect_dataclass(IntStrBox, reflector)
    field = inspection.fields_by_name['values']

    assert type_str(field.replaced_type) == f'{__name__}.Alias[tuple[builtins.int, builtins.str]]'
    assert inspection.field_annotations == {'values': tuple[int, str]}
    assert reflector.to_runtime_annotation(
        field.replaced_type,
        type_alias_policy='preserve',
    ) == alias[int, str]


def test_reflect_dataclass_field_types_accepts_parameterized_dataclass_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        v: t_var  # type: ignore

    field_types = reflect_dataclass_field_types(Box[str], _make_reflector())  # type: ignore

    assert [*field_types] == ['v']
    assert type_str(field_types['v']) == 'builtins.str'


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

    inspection = inspect_dataclass(Child[str], _make_reflector())  # type: ignore

    assert inspection.origin is Child
    assert [field.name for field in inspection.fields] == ['first', 'second', 'third']
    assert [*inspection.fields_by_name] == ['first', 'second', 'third']
    assert [*inspection.field_types] == ['first', 'second', 'third']
    assert [*inspection.field_type_keys] == ['first', 'second', 'third']
    assert [*inspection.field_annotations] == ['first', 'second', 'third']
    assert type_str(inspection.fields_by_name['first'].replaced_type) == 'builtins.int'
    assert type_str(inspection.fields_by_name['third'].replaced_type) == 'builtins.list[builtins.str]'
    assert inspection.field_annotations == {
        'first': int,
        'second': str,
        'third': list[str],
    }


def test_reflect_dataclass_field_type_keys_returns_replaced_type_keys() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    reflector = _make_reflector()

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        v: t_var  # type: ignore

    field_keys = reflect_dataclass_field_type_keys(Box[int], reflector)  # type: ignore

    assert field_keys == {'v': type_key(reflector.reflect_type(int))}


def test_reflect_dataclass_field_annotations_returns_replaced_runtime_annotations() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        v: t_var  # type: ignore

    assert reflect_dataclass_field_annotations(Box[int], _make_reflector()) == {'v': int}  # type: ignore


def test_dataclass_literal_new_type_field_preserves_annotation_and_exposes_effective_shape() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    @dc.dataclass
    class Config:
        mode: ta.Any

    Config.__annotations__['mode'] = mode

    reflector = _make_reflector()
    inspection = inspect_dataclass(Config, reflector)
    field_type = inspection.field_types['mode']
    shape = get_runtime_type_shape(field_type, reflector)

    assert inspection.field_annotations == {'mode': mode}
    assert reflect_dataclass_field_annotations(Config, reflector) == {'mode': mode}
    assert shape.new_type is not None
    assert shape.new_type.obj is mode
    assert shape.literal_value_type is not None
    assert shape.literal_value_type.values == ('a', 'b')


def test_inspect_dataclass_cache_is_per_reflector() -> None:
    @dc.dataclass
    class Item:
        value: int

    left_reflector = _make_reflector()
    right_reflector = _make_reflector()

    left = inspect_dataclass(Item, left_reflector)

    assert inspect_dataclass(Item, left_reflector) is left
    assert inspect_dataclass(Item, right_reflector) is not left


def test_inspect_dataclass_excludes_classvar_and_initvar_pseudo_fields() -> None:
    @dc.dataclass
    class Item:
        shared: ta.ClassVar[int] = 1
        init_only: dc.InitVar[str] = 'x'
        value: int = 2

    inspection = inspect_dataclass(Item, _make_reflector())

    assert [field.name for field in inspection.fields] == ['value']
    assert inspection.field_annotations == {'value': int}


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

    fields = reflect_dataclass_fields(Child[int], _make_reflector())  # type: ignore

    assert [(field.name, field.owner.__name__, type_str(field.replaced_type)) for field in fields] == [
        ('left', 'Base', 'builtins.list[builtins.dict[builtins.str, builtins.int]]'),
        ('right', 'Base', 'builtins.str'),
        ('middle', 'Middle', 'builtins.dict[builtins.str, builtins.int]'),
        ('child', 'Child', 'builtins.int'),
    ]


def test_generic_dataclass_replaces_inherited_field_with_literal_new_type() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    @dc.dataclass
    class ModeBox(Box[mode]):  # type: ignore
        pass

    reflector = _make_reflector()
    inspection = inspect_dataclass(ModeBox, reflector)
    field = inspection.fields_by_name['value']
    shape = get_runtime_type_shape(field.replaced_type, reflector)

    assert field.owner is Box
    assert isinstance(field.raw_type, types.TypeVarType)
    assert inspection.field_annotations == {'value': mode}
    assert reflect_dataclass_field_annotations(ModeBox, reflector) == {'value': mode}
    assert shape.new_type is not None
    assert shape.new_type.obj is mode
    assert shape.literal_value_type is not None
    assert shape.literal_value_type.values == ('a', 'b')


def test_generic_dataclass_literal_new_type_field_keys_preserve_new_type_identity() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    reflector = _make_reflector()
    mode_fields = inspect_dataclass(Box[mode], reflector).field_type_keys  # type: ignore
    other_fields = inspect_dataclass(Box[other_mode], reflector).field_type_keys  # type: ignore

    assert mode_fields['value'] != other_fields['value']
    assert mode_fields['value'] == type_key(reflector.reflect_type(mode))
    assert other_fields['value'] == type_key(reflector.reflect_type(other_mode))


def test_dataclass_field_with_new_type_literal_alias_expands_to_collection_shape() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    @dc.dataclass
    class Config:
        modes: mode_list  # type: ignore

    reflector = _make_reflector()
    inspection = inspect_dataclass(Config, reflector)
    field = inspection.fields_by_name['modes']
    collection_shape = get_runtime_collection_shape(field.replaced_type, reflector)

    assert inspection.field_annotations == {'modes': list[mode]}  # noqa
    assert reflect_dataclass_field_annotations(Config, reflector) == {'modes': list[mode]}  # noqa
    assert type_str(field.replaced_type).endswith('.ModeList')
    assert inspection.field_type_keys['modes'] != inspection.field_structural_type_keys['modes']
    assert inspection.field_structural_type_keys['modes'] == reflector.structural_type_key(
        reflector.reflect_type(list[mode]),  # noqa
    )
    assert reflect_dataclass_field_structural_type_keys(Config, reflector) == inspection.field_structural_type_keys
    assert collection_shape.sequence_item is not None
    item_shape = get_runtime_type_shape(collection_shape.sequence_item, reflector)
    assert item_shape.new_type is not None
    assert item_shape.new_type.obj is mode
    assert item_shape.literal_value_type is not None
    assert item_shape.literal_value_type.values == ('a', 'b')
    assert type_key(field.replaced_type) != type_key(reflector.reflect_type(list[ta.Literal['a', 'b']]))


def test_dataclass_field_with_annotated_new_type_alias_has_nominal_and_structural_views() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    @dc.dataclass
    class Config:
        modes: ta.Annotated[mode_list, 'cfg']  # type: ignore

    reflector = _make_reflector()
    field = inspect_dataclass(Config, reflector).fields_by_name['modes']
    expanded = reflector.reflect_type(ta.Annotated[list[mode], 'cfg'])  # noqa
    shape = get_runtime_type_shape(field.replaced_type, reflector)

    assert shape.annotated is not None
    assert shape.annotated.metadata == ('cfg',)
    assert shape.alias is not None
    assert shape.alias.obj is mode_list
    assert type_key(field.replaced_type) != type_key(expanded)
    assert is_structurally_equivalent(field.replaced_type, expanded)
    assert is_structural_subtype(field.replaced_type, expanded)
    assert reflector.to_runtime_annotation(field.replaced_type) == ta.Annotated[list[mode], 'cfg']  # noqa
    assert reflector.to_runtime_annotation(
        field.replaced_type,
        type_alias_policy='preserve',
    ) == ta.Annotated[mode_list, 'cfg']


def test_dataclass_recursive_alias_field_structural_key_matches_unrolled_field_type() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore

    @dc.dataclass
    class Config:
        node: alias  # type: ignore

    reflector = TypeReflector(
        TypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )
    field = inspect_dataclass(Config, reflector).fields_by_name['node']
    unrolled = reflector.reflect_type(int | list[alias])  # type: ignore
    wrapper = reflector.reflect_type(tuple[int | list[alias]])  # type: ignore
    alias_wrapper = reflector.reflect_type(tuple[alias])  # type: ignore

    assert inspect_dataclass(Config, reflector).field_annotations == {'node': alias}
    assert structural_type_key(field.replaced_type) == structural_type_key(unrolled)
    assert structural_type_key(alias_wrapper) == structural_type_key(wrapper)
    assert inspect_dataclass(Config, reflector).field_structural_type_keys['node'] == structural_type_key(unrolled)


def test_generic_dataclass_recursive_alias_field_structural_key_survives_substitution() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    @dc.dataclass
    class NodeBox(Box[alias]):  # type: ignore
        pass

    reflector = TypeReflector(
        TypeUniverse(dynamic_type_name_suffix='counter'),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )
    inspection = inspect_dataclass(NodeBox, reflector)
    field = inspection.fields_by_name['value']
    unrolled = reflector.reflect_type(int | list[alias])  # type: ignore
    double_unrolled = reflector.reflect_type(int | list[int | list[alias]])  # type: ignore
    entries = reflect_mro_entries(NodeBox, reflector)
    box_entry = next(entry for entry in entries if entry.info is reflector.universe.get_type_info(Box))

    assert field.owner is Box
    assert isinstance(field.raw_type, types.TypeVarType)
    assert structural_type_key(field.replaced_type) == structural_type_key(box_entry.args[0])
    assert inspection.field_annotations == {'value': alias}
    assert inspection.field_structural_type_keys['value'] == structural_type_key(unrolled)
    assert inspection.field_structural_type_keys['value'] == structural_type_key(double_unrolled)
    assert reflector.structural_type_key(box_entry.args[0]) == structural_type_key(unrolled)


def test_dataclass_field_with_generic_new_type_literal_alias_expands_to_collection_shape() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    box_alias = ta.TypeAliasType('BoxAlias', list[t_var], type_params=(t_var,))  # type: ignore

    @dc.dataclass
    class Config:
        modes: box_alias[mode]  # type: ignore

    reflector = _make_reflector()
    inspection = inspect_dataclass(Config, reflector)
    field = inspection.fields_by_name['modes']
    collection_shape = get_runtime_collection_shape(field.replaced_type, reflector)

    assert inspection.field_annotations == {'modes': list[mode]}  # noqa
    assert reflect_dataclass_field_annotations(Config, reflector) == {'modes': list[mode]}  # noqa
    assert collection_shape.sequence_item is not None
    item_shape = get_runtime_type_shape(collection_shape.sequence_item, reflector)
    assert item_shape.new_type is not None
    assert item_shape.new_type.obj is mode
    assert item_shape.literal_value_type is not None
    assert item_shape.literal_value_type.values == ('a', 'b')


def test_reflect_dataclass_fields_uses_overriding_field_owner() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Base(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    @dc.dataclass
    class Child(Base[int]):  # type: ignore
        value: str

    [field] = reflect_dataclass_fields(Child, _make_reflector())

    assert field.owner is Child
    assert type_str(field.raw_type) == 'builtins.str'
    assert type_str(field.replaced_type) == 'builtins.str'


def test_reflect_dataclass_fields_rejects_non_dataclass() -> None:
    class NotDataclass:
        pass

    with pytest.raises(ReflectionError, match='dataclass source'):
        reflect_dataclass_fields(NotDataclass, _make_reflector())


def test_reflect_dataclass_fields_fails_closed_for_unmappable_owner() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Base(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    @dc.dataclass
    class Child(Base[int]):  # type: ignore
        pass

    reflector = _make_reflector()
    child_type = reflector.reflect_type(Child)
    base_type = reflector.reflect_type(Base)
    assert isinstance(child_type, types.Instance)
    assert isinstance(base_type, types.Instance)
    child_type.type._mro = (child_type.type, base_type.type)
    child_type.type._bases = ()

    with pytest.raises(UnsupportedTypeOperationError):
        reflect_dataclass_fields(Child, reflector)


def test_inspect_dataclass_fails_closed_for_unreflectable_alias_annotation() -> None:
    bad_alias = ta.TypeAliasType('BadAlias', ta.TypeIs[int])  # type: ignore

    @dc.dataclass
    class Config:
        value: bad_alias  # type: ignore

    reflector = _make_reflector()

    with pytest.raises(UnreflectableTypeError, match='TypeIs'):
        inspect_dataclass(Config, reflector)

    assert ('dataclass', Config) not in reflector._inspection_cache


def test_reflect_dataclass_field_annotations_emit_replaced_runtime_annotations() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: list[t_var]  # type: ignore

    @dc.dataclass
    class IntBox(Box[int]):  # type: ignore
        pass

    annotations = reflect_dataclass_field_annotations(IntBox, _make_reflector())

    assert annotations == {'value': list[int]}

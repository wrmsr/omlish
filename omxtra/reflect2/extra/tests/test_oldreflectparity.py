# ruff: noqa: F821 PLC0132 SLF001
import collections.abc as cabc
import dataclasses as dc
import typing as ta

from ...core.strconv import type_str
from ...reflect import RuntimeTypeReflector
from ...universe import RuntimeTypeUniverse
from ..dataclasses import inspect_dataclass
from ..ops import reflect_literal_values
from ..ops import reflect_type_key
from ..queries import get_runtime_collection_shape
from ..queries import get_runtime_type_shape
from ..queries import reflect_effective_mapping_base_args
from ..queries import reflect_literal_value_type
from ..queries import reflect_optional_item
from ..queries import reflect_runtime_collection_shape
from ..queries import reflect_runtime_dispatch
from ..queries import reflect_runtime_mapping_shape
from ..queries import reflect_runtime_type_keys
from ..queries import reflect_runtime_type_shape
from ..queries import reflect_runtime_unaliased_type_key
from ..records import RUNTIME_RECORD_KIND_DATACLASS
from ..records import inspect_record
from ..views import get_runtime_type_view
from ..views import reflect_runtime_type_view


def _make_reflector(
        *,
        aliases: ta.Mapping[str, object] | None = None,
) -> RuntimeTypeReflector:
    return RuntimeTypeReflector(
        RuntimeTypeUniverse(dynamic_type_name_suffix='counter'),
        forward_ref_resolver=None if aliases is None else aliases.__getitem__,
    )


def test_old_reflect_parity_for_optional_literal_and_new_type_facts() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    reflector = _make_reflector()

    optional_item = reflect_optional_item(int | None, reflector)
    literal_info = reflect_literal_value_type(ta.Literal['a', 'b'], reflector)
    mode_shape = reflect_runtime_type_shape(mode, reflector)
    mode_dispatch = reflect_runtime_dispatch(mode, reflector)

    assert optional_item is not None
    assert type_str(optional_item) == 'builtins.int'
    assert literal_info is not None
    assert literal_info.value_type is str
    assert literal_info.values == ('a', 'b')
    assert reflect_literal_values(ta.Literal['a', 'b'], reflector) == ['a', 'b']

    assert mode_shape.new_type is not None
    assert mode_shape.new_type.obj is mode
    assert mode_shape.new_type.runtime_supertype == ta.Literal['a', 'b']
    assert mode_shape.literal_value_type is not None
    assert mode_shape.literal_value_type.values == ('a', 'b')
    assert mode_dispatch.runtime_class is None
    assert mode_dispatch.type_shape.literal_value_type == mode_shape.literal_value_type

    assert reflect_type_key(mode, reflector) != reflect_type_key(ta.Literal['a', 'b'], reflector)
    assert reflect_runtime_unaliased_type_key(mode, reflector) == reflect_type_key(mode, reflector)


def test_old_reflect_parity_for_nested_collection_dispatch_facts() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    reflector = _make_reflector()

    list_shape = reflect_runtime_collection_shape(list[mode], reflector)  # noqa
    mapping_shape = reflect_runtime_mapping_shape(ta.Mapping[str, list[mode]], reflector)  # noqa
    dispatch = reflect_runtime_dispatch(ta.Mapping[str, list[mode]], reflector)  # noqa
    view = reflect_runtime_type_view(ta.Mapping[str, list[mode]], reflector)  # noqa
    base_args = reflect_effective_mapping_base_args(
        ta.Mapping[str, list[mode]],  # noqa
        cabc.Mapping,
        reflector,
    )

    assert list_shape.sequence_item is not None
    list_item_shape = reflect_runtime_type_shape(mode, reflector)
    assert list_shape.sequence_item is list_item_shape.original
    assert list_item_shape.new_type is not None
    assert list_item_shape.new_type.obj is mode
    assert list_item_shape.literal_value_type is not None
    assert list_item_shape.literal_value_type.values == ('a', 'b')

    assert mapping_shape is not None
    assert type_str(mapping_shape.key.effective) == 'builtins.str'
    value_shape = get_runtime_collection_shape(mapping_shape.value.effective, reflector)
    assert value_shape.sequence_item is not None
    assert reflector.type_key(value_shape.sequence_item) == reflect_type_key(mode, reflector)

    assert dispatch.runtime_class is cabc.Mapping
    assert dispatch.collection_shape.mapping is not None
    assert view.mapping is not None
    assert view.dispatch.runtime_class is cabc.Mapping
    assert view.collection.mapping is not None
    assert view.keys.nominal == reflect_type_key(ta.Mapping[str, list[mode]], reflector)  # noqa
    assert base_args is not None
    assert [type_str(arg) for arg in base_args] == [
        'builtins.str',
        f'builtins.list[{mode.__module__}.{mode.__qualname__}]',
    ]


def test_old_reflect_parity_for_generic_dataclass_record_facts() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    @dc.dataclass
    class Box(ta.Generic[t_var]):  # type: ignore
        value: t_var  # type: ignore

    @dc.dataclass
    class ModeBox(Box[mode]):  # type: ignore
        pass

    reflector = _make_reflector()
    dataclass_inspection = inspect_dataclass(ModeBox, reflector)
    record = inspect_record(ModeBox, reflector)

    field = dataclass_inspection.fields_by_name['value']
    field_shape = reflect_runtime_type_shape(mode, reflector)

    assert field.owner is Box
    assert dataclass_inspection.field_annotations == {'value': mode}
    assert reflector.type_key(field.replaced_type) == reflect_type_key(mode, reflector)
    replaced_shape = get_runtime_type_shape(field.replaced_type, reflector)
    assert replaced_shape.new_type is not None
    assert replaced_shape.new_type.obj is mode
    assert replaced_shape.literal_value_type == field_shape.literal_value_type

    assert record.kind == RUNTIME_RECORD_KIND_DATACLASS
    assert record.fields_by_name['value'].annotation is mode
    assert record.fields_by_name['value'].type_key == reflect_type_key(mode, reflector)
    assert record.fields_by_name['value'].structural_type_key == reflector.structural_type_key(field.replaced_type)


def test_old_reflect_parity_for_recursive_alias_container_cache_facts() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    node_list = ta.TypeAliasType('NodeList', list[alias])  # type: ignore
    reflector = _make_reflector(aliases={'Node': alias})

    alias_keys = reflect_runtime_type_keys(alias, reflector)
    list_keys = reflect_runtime_type_keys(node_list, reflector)
    unrolled_node = reflector.reflect_type(int | list[alias])  # type: ignore
    unrolled_list = reflector.reflect_type(list[int | list[alias]])  # type: ignore
    collection_shape = reflect_runtime_collection_shape(node_list, reflector)
    view = reflect_runtime_type_view(node_list, reflector)
    item_view = get_runtime_type_view(collection_shape.sequence_item, reflector)  # type: ignore

    assert alias_keys.nominal == reflect_type_key(alias, reflector)
    assert alias_keys.structural == reflector.structural_type_key(unrolled_node)
    assert list_keys.nominal != reflect_type_key(list[alias], reflector)  # type: ignore
    assert list_keys.structural == reflector.structural_type_key(unrolled_list)

    assert collection_shape.sequence_item is not None
    assert view.collection.sequence_item is not None
    assert view.keys == list_keys
    assert type_str(collection_shape.sequence_item).endswith('.Node')
    assert type_str(view.collection.sequence_item).endswith('.Node')
    assert reflector.structural_type_key(collection_shape.sequence_item) == alias_keys.structural
    assert item_view.keys.structural == alias_keys.structural

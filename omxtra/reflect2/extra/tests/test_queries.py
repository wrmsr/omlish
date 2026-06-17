# ruff: noqa: F821 PLC0132 SLF001
import collections.abc as cabc
import enum
import typing as ta

import pytest

from ...core import types
from ...core.strconv import type_str
from ...core.typekeys import type_key
from ...errors import ReflectionError
from ...reflect import TypeReflector
from ...universe import TypeUniverse
from ..ops import reflect_type_key
from ..queries import destructure_literal_union
from ..queries import destructure_primitive_union
from ..queries import get_annotated
from ..queries import get_effective_instance_base_args
from ..queries import get_effective_mapping_base_args
from ..queries import get_effective_single_base_arg
from ..queries import get_instance_base_args
from ..queries import get_literal_value_type
from ..queries import get_mapping_base_args
from ..queries import get_optional_item
from ..queries import get_runtime_class
from ..queries import get_runtime_collection_shape
from ..queries import get_runtime_dispatch
from ..queries import get_runtime_literal_value_type
from ..queries import get_runtime_mapping_shape
from ..queries import get_runtime_new_type
from ..queries import get_runtime_new_type_info
from ..queries import get_runtime_new_type_supertype
from ..queries import get_runtime_type_keys
from ..queries import get_runtime_type_shape
from ..queries import get_single_base_arg
from ..queries import is_instance_of_runtime_base
from ..queries import is_optional_type
from ..queries import reflect_annotated
from ..queries import reflect_effective_instance_base_args
from ..queries import reflect_effective_mapping_base_args
from ..queries import reflect_effective_single_base_arg
from ..queries import reflect_is_instance_of_runtime_base
from ..queries import reflect_literal_union
from ..queries import reflect_literal_value_type
from ..queries import reflect_mapping_base_args
from ..queries import reflect_optional_item
from ..queries import reflect_primitive_union
from ..queries import reflect_runtime_collection_shape
from ..queries import reflect_runtime_dispatch
from ..queries import reflect_runtime_effective_type_key
from ..queries import reflect_runtime_literal_value_type
from ..queries import reflect_runtime_mapping_shape
from ..queries import reflect_runtime_new_type_info
from ..queries import reflect_runtime_new_type_supertype
from ..queries import reflect_runtime_type_alias
from ..queries import reflect_runtime_type_keys
from ..queries import reflect_runtime_type_shape
from ..queries import reflect_runtime_unaliased_type_key
from ..queries import reflect_single_base_arg
from ..queries import reflect_strip_annotated
from ..queries import require_runtime_class
from ..queries import require_runtime_new_type_info
from ..queries import strip_annotated


def _make_reflector() -> TypeReflector:
    return TypeReflector(TypeUniverse())


def test_runtime_class_queries_recover_instance_class() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(list[int])

    assert get_runtime_class(typ, reflector.universe) is list
    assert require_runtime_class(typ, reflector.universe) is list
    assert get_runtime_class(reflector.reflect_type(int | str), reflector.universe) is None


def test_require_runtime_class_raises_for_non_instance() -> None:
    reflector = _make_reflector()

    with pytest.raises(ReflectionError, match='Runtime class'):
        require_runtime_class(reflector.reflect_type(int | str), reflector.universe)


def test_runtime_new_type_queries_recover_identity_and_supertype() -> None:
    reflector = _make_reflector()
    user_id = ta.NewType('UserId', int)  # type: ignore
    typ = reflector.reflect_type(user_id)

    info = get_runtime_new_type_info(typ, reflector)

    assert info is not None
    assert info.obj is user_id
    assert info.runtime_supertype is int
    assert type_str(info.supertype) == 'builtins.int'
    assert get_runtime_new_type(typ, reflector.universe) is user_id
    assert type_str(get_runtime_new_type_supertype(typ, reflector)) == 'builtins.int'  # type: ignore
    assert require_runtime_new_type_info(typ, reflector) == info
    assert reflect_runtime_new_type_info(user_id, reflector) == info
    assert type_str(reflect_runtime_new_type_supertype(user_id, reflector)) == 'builtins.int'  # type: ignore


def test_runtime_new_type_queries_reject_non_new_type() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(int)

    assert get_runtime_new_type(typ, reflector.universe) is None
    assert get_runtime_new_type_info(typ, reflector) is None
    assert get_runtime_new_type_supertype(typ, reflector) is None
    assert reflect_runtime_new_type_info(int, reflector) is None
    assert reflect_runtime_new_type_supertype(int, reflector) is None

    with pytest.raises(ReflectionError, match='Runtime NewType'):
        require_runtime_new_type_info(typ, reflector)


def test_runtime_new_type_keys_preserve_distinct_identity() -> None:
    reflector = _make_reflector()
    user_id = ta.NewType('UserId', int)  # type: ignore
    account_id = ta.NewType('AccountId', int)  # type: ignore
    user_type = reflector.reflect_type(user_id)
    account_type = reflector.reflect_type(account_id)
    int_type = reflector.reflect_type(int)

    assert type_key(user_type) != type_key(account_type)
    assert type_key(user_type) != type_key(int_type)
    assert reflector.to_runtime_annotation(user_type) is user_id
    assert reflector.to_runtime_annotation(account_type) is account_id


def test_runtime_new_type_keys_distinguish_same_literal_supertype() -> None:
    reflector = _make_reflector()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore
    mode_type = reflector.reflect_type(mode)
    other_mode_type = reflector.reflect_type(other_mode)
    supertype = reflector.reflect_type(ta.Literal['a', 'b'])

    assert type_key(mode_type) != type_key(other_mode_type)
    assert type_key(mode_type) != type_key(supertype)


def test_annotated_query_extracts_item_and_metadata() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(ta.Annotated[int, 'cfg'])

    annotated = get_annotated(typ)

    assert annotated is not None
    assert type_str(annotated.item) == 'builtins.int'
    assert annotated.metadata == ('cfg',)
    assert strip_annotated(typ) is annotated.item


def test_annotated_query_flattens_nested_metadata_in_order() -> None:
    reflector = _make_reflector()
    typ = types.AnnotatedType(
        types.AnnotatedType(reflector.reflect_type(int), ('inner',)),
        ('outer',),
    )

    annotated = get_annotated(typ)

    assert annotated is not None
    assert type_str(annotated.item) == 'builtins.int'
    assert annotated.metadata == ('outer', 'inner')


def test_annotated_query_returns_none_and_strip_passthrough_for_plain_type() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(int)

    assert get_annotated(typ) is None
    assert strip_annotated(typ) is typ
    assert reflect_annotated(int, reflector) is None
    assert reflect_strip_annotated(int, reflector) is typ


def test_reflect_annotated_query_handles_runtime_annotated_type() -> None:
    reflector = _make_reflector()

    annotated = reflect_annotated(ta.Annotated[int, 'cfg', {'x': 1}], reflector)

    assert annotated is not None
    assert type_str(annotated.item) == 'builtins.int'
    assert annotated.metadata == ('cfg', {'x': 1})
    assert type_str(reflect_strip_annotated(ta.Annotated[int, 'cfg'], reflector)) == 'builtins.int'


def test_runtime_type_shape_preserves_original_and_strips_annotated_new_type() -> None:
    reflector = _make_reflector()
    user_id = ta.NewType('UserId', int)  # type: ignore
    typ = reflector.reflect_type(ta.Annotated[user_id, 'id-field'])

    shape = get_runtime_type_shape(typ, reflector)

    assert shape.original is typ
    assert shape.annotated is not None
    assert shape.annotated.metadata == ('id-field',)
    assert type_str(shape.unannotated).endswith('.UserId')
    assert shape.new_type is not None
    assert shape.new_type.obj is user_id
    assert shape.new_type.runtime_supertype is int
    assert type_str(shape.effective) == 'builtins.int'
    assert shape.optional_item is None
    assert shape.literal_value_type is None
    assert shape.literal_union is None


def test_runtime_type_shape_keeps_literal_new_type_identity_and_effective_literal_shape() -> None:
    reflector = _make_reflector()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    shape = reflect_runtime_type_shape(mode, reflector)

    assert shape.new_type is not None
    assert shape.new_type.obj is mode
    assert shape.new_type.runtime_supertype == ta.Literal['a', 'b']
    assert shape.literal_value_type is not None
    assert shape.literal_value_type.value_type is str
    assert shape.literal_value_type.values == ('a', 'b')
    assert reflector.to_runtime_annotation(shape.original) is mode


def test_runtime_type_shape_keeps_none_literal_new_type_identity_and_effective_literal_shape() -> None:
    reflector = _make_reflector()
    maybe_mode = ta.NewType('MaybeMode', ta.Literal[None, 'x'])  # type: ignore

    shape = reflect_runtime_type_shape(maybe_mode, reflector)

    assert shape.new_type is not None
    assert shape.new_type.obj is maybe_mode
    assert shape.new_type.runtime_supertype == ta.Literal[None, 'x']
    assert shape.literal_value_type is None
    assert shape.literal_union is None
    assert shape.optional_item is None
    assert reflector.to_runtime_annotation(shape.original) is maybe_mode


def test_runtime_type_shape_detects_annotated_optional_after_stripping_metadata() -> None:
    reflector = _make_reflector()

    shape = reflect_runtime_type_shape(ta.Annotated[int | None, 'optional'], reflector)

    assert shape.annotated is not None
    assert shape.annotated.metadata == ('optional',)
    assert shape.optional_item is not None
    assert type_str(shape.optional_item) == 'builtins.int'
    assert shape.effective is shape.unannotated


def test_runtime_type_shape_detects_annotated_literal_union_after_stripping_metadata() -> None:
    reflector = _make_reflector()

    shape = reflect_runtime_type_shape(ta.Annotated[ta.Literal['a', 'b'], 'tag'], reflector)

    assert shape.annotated is not None
    assert shape.literal_value_type is not None
    assert shape.literal_value_type.value_type is str
    assert shape.literal_value_type.values == ('a', 'b')
    assert shape.literal_union is None


def test_runtime_type_shape_keeps_new_type_inside_collections_as_argument_shape() -> None:
    reflector = _make_reflector()
    user_id = ta.NewType('UserId', int)  # type: ignore

    shape = reflect_runtime_type_shape(list[user_id], reflector)

    assert type_str(shape.effective).startswith('builtins.list[')
    assert shape.new_type is None
    assert shape.annotated is None
    assert shape.optional_item is None


def test_runtime_type_shape_preserves_alias_identity_and_exposes_expanded_unaliased_type() -> None:
    reflector = _make_reflector()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    shape = reflect_runtime_type_shape(mode_list, reflector)
    alias = reflect_runtime_type_alias(mode_list, reflector)

    assert shape.alias is not None
    assert shape.alias.obj is mode_list
    assert alias == shape.alias
    assert shape.unaliased is shape.alias.target
    assert type_str(shape.unaliased).endswith('.Mode]')
    assert type_str(shape.effective).endswith('.Mode]')
    assert reflect_type_key(mode_list, reflector) != reflect_runtime_unaliased_type_key(mode_list, reflector)
    assert reflect_runtime_unaliased_type_key(mode_list, reflector) == reflect_type_key(list[mode], reflector)  # noqa
    assert reflect_runtime_effective_type_key(mode_list, reflector) == reflect_runtime_unaliased_type_key(
        mode_list,
        reflector,
    )


def test_runtime_type_keys_expose_nominal_structural_effective_and_alpha_structural_views() -> None:
    reflector = _make_reflector()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    keys = reflect_runtime_type_keys(mode_list, reflector)
    typ = reflector.reflect_type(mode_list)

    assert keys == get_runtime_type_keys(typ, reflector)
    assert keys.nominal == reflector.type_key(typ)
    assert keys.nominal != reflect_type_key(list[mode], reflector)  # noqa
    assert keys.structural == reflector.structural_type_key(reflector.reflect_type(list[mode]))  # noqa
    assert keys.effective == reflect_type_key(list[mode], reflector)  # noqa
    assert keys.alpha_structural == reflector.alpha_structural_type_key(reflector.reflect_type(list[mode]))  # noqa


def test_runtime_type_keys_preserve_new_type_identity_except_effective_key() -> None:
    reflector = _make_reflector()
    user_id = ta.NewType('UserId', int)  # type: ignore

    keys = reflect_runtime_type_keys(user_id, reflector)

    assert keys.nominal == reflector.type_key(reflector.reflect_type(user_id))
    assert keys.structural == reflector.structural_type_key(reflector.reflect_type(user_id))
    assert keys.nominal != reflect_type_key(int, reflector)
    assert keys.structural != reflector.structural_type_key(reflector.reflect_type(int))
    assert reflect_runtime_unaliased_type_key(user_id, reflector) == keys.nominal
    assert reflect_runtime_effective_type_key(user_id, reflector) == keys.nominal
    assert keys.effective == reflect_type_key(int, reflector)


def test_runtime_type_keys_distinguish_unaliased_from_effective_for_alias_to_new_type() -> None:
    reflector = _make_reflector()
    user_id = ta.NewType('UserId', int)  # type: ignore
    user_alias = ta.TypeAliasType('UserAlias', user_id)  # type: ignore

    keys = reflect_runtime_type_keys(user_alias, reflector)

    assert keys.nominal == reflect_type_key(user_alias, reflector)
    assert reflect_runtime_unaliased_type_key(user_alias, reflector) == reflect_type_key(user_id, reflector)
    assert reflect_runtime_effective_type_key(user_alias, reflector) == reflect_type_key(user_id, reflector)
    assert keys.effective == reflect_type_key(int, reflector)


def test_runtime_type_keys_strip_annotated_for_structural_and_effective_keys() -> None:
    reflector = _make_reflector()

    keys = reflect_runtime_type_keys(ta.Annotated[int, 'cfg'], reflector)

    assert keys.nominal != reflect_type_key(int, reflector)
    assert keys.structural == reflector.structural_type_key(reflector.reflect_type(int))
    assert keys.effective == reflect_type_key(int, reflector)
    assert keys.alpha_structural == reflector.alpha_structural_type_key(reflector.reflect_type(int))


def test_runtime_type_keys_recursive_alias_structural_key_matches_unrolling() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    reflector = TypeReflector(
        TypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )

    keys = reflect_runtime_type_keys(alias, reflector)
    unrolled = reflector.reflect_type(int | list[alias])  # type: ignore

    assert keys.nominal == reflect_type_key(alias, reflector)
    assert keys.structural == reflector.structural_type_key(unrolled)
    assert keys.effective == reflect_runtime_effective_type_key(alias, reflector)
    assert keys.alpha_structural == reflector.alpha_structural_type_key(unrolled)


def test_runtime_type_keys_recursive_alias_inside_container_alias_matches_expanded_container() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    node_list = ta.TypeAliasType('NodeList', list[alias])  # type: ignore
    reflector = TypeReflector(
        TypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )

    keys = reflect_runtime_type_keys(node_list, reflector)
    expanded = reflector.reflect_type(list[alias])  # type: ignore
    unrolled = reflector.reflect_type(list[int | list[alias]])  # type: ignore

    assert keys.nominal != reflect_type_key(list[alias], reflector)  # type: ignore
    assert keys.structural == reflector.structural_type_key(expanded)
    assert keys.structural == reflector.structural_type_key(unrolled)
    assert keys.alpha_structural == reflector.alpha_structural_type_key(unrolled)


def test_get_instance_base_args_maps_collection_base() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(dict[str, int])

    args = get_instance_base_args(typ, cabc.Mapping, reflector)

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.str', 'builtins.int']


def test_get_instance_base_args_returns_none_for_non_instance() -> None:
    reflector = _make_reflector()

    assert get_instance_base_args(reflector.reflect_type(int | str), cabc.Mapping, reflector) is None


def test_get_instance_base_args_rejects_non_instance_base() -> None:
    reflector = _make_reflector()

    with pytest.raises(ReflectionError, match='base target'):
        get_instance_base_args(reflector.reflect_type(list[int]), int | str, reflector)


def test_is_instance_of_runtime_base_checks_mapped_base_presence() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(list[int])

    assert is_instance_of_runtime_base(typ, cabc.Sequence, reflector)
    assert reflect_is_instance_of_runtime_base(list[int], cabc.Iterable, reflector)
    assert not reflect_is_instance_of_runtime_base(dict[str, int], cabc.Sequence, reflector)


def test_single_base_arg_extracts_iterable_element_type() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(list[int])

    item = get_single_base_arg(typ, cabc.Iterable, reflector)

    assert item is not None
    assert type_str(item) == 'builtins.int'
    assert type_str(
        reflect_single_base_arg(tuple[str, ...], cabc.Sequence, reflector),  # type: ignore
    ) == 'builtins.str'


def test_single_base_arg_returns_none_for_missing_base() -> None:
    reflector = _make_reflector()

    assert reflect_single_base_arg(dict[str, int], cabc.Sequence, reflector) is None


def test_single_base_arg_rejects_wrong_arity_base() -> None:
    reflector = _make_reflector()

    with pytest.raises(ReflectionError, match='Expected one base argument'):
        reflect_single_base_arg(dict[str, int], cabc.Mapping, reflector)


def test_mapping_base_args_extracts_key_and_value_types() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(dict[str, int])

    mapping_args = get_mapping_base_args(typ, cabc.Mapping, reflector)

    assert mapping_args is not None
    assert [type_str(arg) for arg in mapping_args] == ['builtins.str', 'builtins.int']
    assert [
        type_str(arg)
        for arg in reflect_mapping_base_args(dict[str, int], cabc.MutableMapping, reflector)  # type: ignore
    ] == [
        'builtins.str',
        'builtins.int',
    ]


def test_mapping_base_args_returns_none_for_missing_base() -> None:
    reflector = _make_reflector()

    assert reflect_mapping_base_args(list[int], cabc.Mapping, reflector) is None


def test_mapping_base_args_rejects_wrong_arity_base() -> None:
    reflector = _make_reflector()

    with pytest.raises(ReflectionError, match='Expected two mapping base arguments'):
        reflect_mapping_base_args(list[int], cabc.Iterable, reflector)


def test_effective_base_arg_queries_strip_annotated_before_base_lookup() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(ta.Annotated[list[int], 'items'])

    args = get_effective_instance_base_args(typ, cabc.Sequence, reflector)

    assert args is not None
    assert [type_str(arg) for arg in args] == ['builtins.int']
    assert type_str(get_effective_single_base_arg(typ, cabc.Iterable, reflector)) == 'builtins.int'  # type: ignore
    assert [
        type_str(arg)
        for arg in reflect_effective_instance_base_args(ta.Annotated[list[int], 'items'], cabc.Sequence, reflector)  # type: ignore  # noqa
    ] == ['builtins.int']
    assert type_str(
        reflect_effective_single_base_arg(ta.Annotated[list[int], 'items'], cabc.Iterable, reflector),  # type: ignore
    ) == 'builtins.int'


def test_effective_mapping_base_arg_queries_unwrap_top_level_new_type_supertype() -> None:
    reflector = _make_reflector()
    str_int_map = ta.NewType('StrIntMap', dict[str, int])  # type: ignore
    typ = reflector.reflect_type(str_int_map)

    mapping_args = get_effective_mapping_base_args(typ, cabc.Mapping, reflector)

    assert mapping_args is not None
    assert [type_str(arg) for arg in mapping_args] == ['builtins.str', 'builtins.int']
    assert [
        type_str(arg)
        for arg in reflect_effective_mapping_base_args(str_int_map, cabc.Mapping, reflector)  # type: ignore
    ] == ['builtins.str', 'builtins.int']


def test_runtime_collection_shape_summarizes_common_collection_views() -> None:
    reflector = _make_reflector()

    shape = reflect_runtime_collection_shape(dict[str, int], reflector)

    assert shape.type_shape.effective is shape.type_shape.unannotated
    assert shape.iterable_item is not None
    assert type_str(shape.iterable_item) == 'builtins.str'
    assert shape.sequence_item is None
    assert shape.set_item is None
    assert shape.mapping is not None
    assert [type_str(arg) for arg in shape.mapping] == ['builtins.str', 'builtins.int']


def test_runtime_collection_shape_exposes_recursive_alias_sequence_item_and_structural_key() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    node_list = ta.TypeAliasType('NodeList', list[alias])  # type: ignore
    reflector = TypeReflector(
        TypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )

    direct_shape = reflect_runtime_collection_shape(list[alias], reflector)  # type: ignore
    alias_shape = reflect_runtime_collection_shape(node_list, reflector)
    unrolled = reflector.reflect_type(list[int | list[alias]])  # type: ignore

    assert direct_shape.sequence_item is not None
    assert alias_shape.sequence_item is not None
    assert type_str(direct_shape.sequence_item).endswith('.Node')
    assert type_str(alias_shape.sequence_item).endswith('.Node')
    assert reflector.structural_type_key(alias_shape.type_shape.original) == reflector.structural_type_key(unrolled)
    assert reflector.structural_type_key(alias_shape.type_shape.effective) == reflector.structural_type_key(unrolled)
    assert reflector.structural_type_key(alias_shape.sequence_item) == reflector.structural_type_key(
        direct_shape.sequence_item,
    )


def test_runtime_collection_shape_exposes_recursive_alias_mapping_value_and_structural_key() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    node_map = ta.TypeAliasType('NodeMap', ta.Mapping[str, alias])  # type: ignore
    reflector = TypeReflector(
        TypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )

    direct_shape = reflect_runtime_collection_shape(ta.Mapping[str, alias], reflector)  # type: ignore
    alias_shape = reflect_runtime_collection_shape(node_map, reflector)
    mapping_shape = reflect_runtime_mapping_shape(node_map, reflector)
    unrolled = reflector.reflect_type(ta.Mapping[str, int | list[alias]])  # type: ignore
    base_args = reflect_effective_mapping_base_args(node_map, cabc.Mapping, reflector)

    assert direct_shape.mapping is not None
    assert alias_shape.mapping is not None
    assert mapping_shape is not None
    assert base_args is not None
    assert type_str(alias_shape.mapping[0]) == 'builtins.str'
    assert type_str(alias_shape.mapping[1]).endswith('.Node')
    assert [type_str(arg) for arg in base_args] == [
        'builtins.str',
        type_str(alias_shape.mapping[1]),
    ]
    assert reflector.structural_type_key(alias_shape.type_shape.original) == reflector.structural_type_key(unrolled)
    assert reflector.structural_type_key(alias_shape.type_shape.effective) == reflector.structural_type_key(unrolled)
    assert reflector.structural_type_key(mapping_shape.value.original) == reflector.structural_type_key(
        direct_shape.mapping[1],
    )


def test_runtime_collection_shape_uses_effective_type_for_annotated_new_type() -> None:
    reflector = _make_reflector()
    user_ids = ta.NewType('UserIds', list[int])  # type: ignore
    typ = reflector.reflect_type(ta.Annotated[user_ids, 'field'])

    shape = get_runtime_collection_shape(typ, reflector)

    assert shape.type_shape.annotated is not None
    assert shape.type_shape.new_type is not None
    assert type_str(shape.type_shape.effective) == 'builtins.list[builtins.int]'
    assert type_str(shape.iterable_item) == 'builtins.int'  # type: ignore
    assert type_str(shape.sequence_item) == 'builtins.int'  # type: ignore
    assert shape.set_item is None
    assert shape.mapping is None


def test_runtime_collection_shape_expands_new_type_literal_alias_item() -> None:
    reflector = _make_reflector()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    shape = reflect_runtime_collection_shape(mode_list, reflector)

    assert shape.sequence_item is not None
    item_shape = get_runtime_type_shape(shape.sequence_item, reflector)
    assert item_shape.new_type is not None
    assert item_shape.new_type.obj is mode
    assert item_shape.literal_value_type is not None
    assert item_shape.literal_value_type.values == ('a', 'b')
    assert reflect_type_key(mode_list, reflector) != reflect_type_key(list[ta.Literal['a', 'b']], reflector)


def test_runtime_collection_shape_expands_generic_new_type_literal_alias_item() -> None:
    reflector = _make_reflector()
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    other_mode = ta.NewType('OtherMode', ta.Literal['a', 'b'])  # type: ignore
    box_alias = ta.TypeAliasType('BoxAlias', list[t_var], type_params=(t_var,))  # type: ignore

    shape = reflect_runtime_collection_shape(box_alias[mode], reflector)

    assert shape.sequence_item is not None
    item_shape = get_runtime_type_shape(shape.sequence_item, reflector)
    assert item_shape.new_type is not None
    assert item_shape.new_type.obj is mode
    assert item_shape.literal_value_type is not None
    assert item_shape.literal_value_type.values == ('a', 'b')
    assert reflect_type_key(box_alias[mode], reflector) != reflect_type_key(
        box_alias[other_mode],
        reflector,
    )
    assert reflect_type_key(box_alias[mode], reflector) != reflect_type_key(
        box_alias[ta.Literal['a', 'b']],
        reflector,
    )


def test_runtime_mapping_shape_summarizes_nested_new_type_literal_collection() -> None:
    reflector = _make_reflector()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    mapping_shape = reflect_runtime_mapping_shape(ta.Mapping[str, list[mode]], reflector)  # noqa

    assert mapping_shape is not None
    assert type_str(mapping_shape.key.effective) == 'builtins.str'
    value_collection = get_runtime_collection_shape(mapping_shape.value.effective, reflector)
    assert value_collection.sequence_item is not None
    item_shape = get_runtime_type_shape(value_collection.sequence_item, reflector)
    assert item_shape.new_type is not None
    assert item_shape.new_type.obj is mode
    assert item_shape.literal_value_type is not None
    assert item_shape.literal_value_type.values == ('a', 'b')


def test_runtime_dispatch_summarizes_nested_mapping_collection() -> None:
    reflector = _make_reflector()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    dispatch = reflect_runtime_dispatch(ta.Mapping[str, list[mode]], reflector)  # noqa

    assert dispatch.runtime_class is cabc.Mapping
    assert dispatch.collection_shape.mapping is not None
    key_type, value_type = dispatch.collection_shape.mapping
    assert type_str(key_type) == 'builtins.str'
    value_collection = get_runtime_collection_shape(value_type, reflector)
    assert value_collection.sequence_item is not None
    item_shape = get_runtime_type_shape(value_collection.sequence_item, reflector)
    assert item_shape.new_type is not None
    assert item_shape.new_type.obj is mode
    assert item_shape.literal_value_type is not None
    assert item_shape.literal_value_type.values == ('a', 'b')


def test_runtime_mapping_shape_returns_none_for_non_mapping() -> None:
    reflector = _make_reflector()

    assert reflect_runtime_mapping_shape(list[int], reflector) is None
    assert get_runtime_mapping_shape(reflector.reflect_type(int), reflector) is None


def test_runtime_collection_shape_returns_none_fields_for_non_collection() -> None:
    reflector = _make_reflector()

    shape = reflect_runtime_collection_shape(int, reflector)

    assert type_str(shape.type_shape.effective) == 'builtins.int'
    assert shape.iterable_item is None
    assert shape.sequence_item is None
    assert shape.set_item is None
    assert shape.mapping is None


def test_runtime_dispatch_summarizes_plain_collection_class_and_args() -> None:
    reflector = _make_reflector()

    dispatch = reflect_runtime_dispatch(dict[str, int], reflector)

    assert dispatch.type_shape.effective is dispatch.collection_shape.type_shape.effective
    assert dispatch.runtime_class is dict
    assert not dispatch.is_any
    assert not dispatch.is_none
    assert dispatch.collection_shape.mapping is not None
    assert [type_str(arg) for arg in dispatch.collection_shape.mapping] == ['builtins.str', 'builtins.int']


def test_runtime_dispatch_summarizes_optional_literal_and_primitive_unions() -> None:
    reflector = _make_reflector()

    optional = reflect_runtime_dispatch(int | None, reflector)
    assert optional.type_shape.optional_item is not None
    assert type_str(optional.type_shape.optional_item) == 'builtins.int'
    assert optional.runtime_class is None

    literal = reflect_runtime_dispatch(ta.Literal['red', 'blue'], reflector)
    assert literal.type_shape.literal_value_type is not None
    assert literal.type_shape.literal_value_type.values == ('red', 'blue')
    assert literal.runtime_class is None

    primitive_union = reflect_runtime_dispatch(int | str, reflector)
    assert primitive_union.type_shape.primitive_union is not None
    assert primitive_union.type_shape.primitive_union.primitives == (int, str)
    assert primitive_union.runtime_class is None


def test_runtime_dispatch_summarizes_bytes_and_float_literals() -> None:
    reflector = _make_reflector()

    bytes_dispatch = reflect_runtime_dispatch(ta.Literal[b'red', b'blue'], reflector)
    assert bytes_dispatch.type_shape.literal_value_type is not None
    assert bytes_dispatch.type_shape.literal_value_type.value_type is bytes
    assert bytes_dispatch.type_shape.literal_value_type.values == (b'red', b'blue')
    assert bytes_dispatch.type_shape.literal_union is None
    assert bytes_dispatch.runtime_class is None

    float_dispatch = reflect_runtime_dispatch(ta.Literal[1.5, 2.5], reflector)
    assert float_dispatch.type_shape.literal_value_type is not None
    assert float_dispatch.type_shape.literal_value_type.value_type is float
    assert float_dispatch.type_shape.literal_value_type.values == (1.5, 2.5)
    assert float_dispatch.type_shape.literal_union is None
    assert float_dispatch.runtime_class is None

    none_dispatch = reflect_runtime_dispatch(ta.Literal[None], reflector)
    assert none_dispatch.type_shape.literal_value_type is not None
    assert none_dispatch.type_shape.literal_value_type.value_type is type(None)
    assert none_dispatch.type_shape.literal_value_type.values == (None,)
    assert none_dispatch.type_shape.optional_item is None
    assert none_dispatch.runtime_class is None


def test_runtime_dispatch_literal_type_keys_are_cache_stable() -> None:
    reflector = _make_reflector()

    bytes_effective = reflect_runtime_dispatch(ta.Literal[b'red', b'blue'], reflector).type_shape.effective
    float_effective = reflect_runtime_dispatch(ta.Literal[1.5, 2.5], reflector).type_shape.effective
    none_effective = reflect_runtime_dispatch(ta.Literal[None], reflector).type_shape.effective

    bytes_key = reflector.type_key(bytes_effective)
    float_key = reflector.type_key(float_effective)
    none_key = reflector.type_key(none_effective)

    assert reflector.type_key(bytes_effective) is bytes_key
    assert reflector.type_key(float_effective) is float_key
    assert reflector.type_key(none_effective) is none_key
    assert bytes_key == (
        "U[L[bytes:b'blue',I['builtins.bytes']],L[bytes:b'red',I['builtins.bytes']]]"
    )
    assert float_key == (  # type: ignore
        'U[OU[$0]]',
        frozenset({
            ("L[$0,I['builtins.float']]", 1.5),
            ("L[$0,I['builtins.float']]", 2.5),
        }),
    )
    assert none_key == "L[None:,I['builtins.None']]"


def test_runtime_dispatch_effective_type_key_matches_direct_reflection() -> None:
    reflector = _make_reflector()

    for form in [
        ta.Optional[int],  # noqa
        ta.Literal['x', b'y', None],
        ta.Literal[1.5, 2.5],
    ]:
        dispatch = reflect_runtime_dispatch(form, reflector)

        assert reflector.type_key(dispatch.type_shape.effective) == reflect_type_key(form, reflector)


def test_runtime_dispatch_keeps_new_type_identity_but_dispatches_on_effective_supertype() -> None:
    reflector = _make_reflector()
    user_ids = ta.NewType('UserIds', list[int])  # type: ignore

    dispatch = reflect_runtime_dispatch(ta.Annotated[user_ids, 'field'], reflector)

    assert dispatch.type_shape.annotated is not None
    assert dispatch.type_shape.new_type is not None
    assert dispatch.type_shape.new_type.obj is user_ids
    assert dispatch.runtime_class is list
    assert type_str(dispatch.collection_shape.sequence_item) == 'builtins.int'  # type: ignore


def test_runtime_dispatch_keeps_literal_new_type_identity_but_dispatches_on_effective_literal() -> None:
    reflector = _make_reflector()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    maybe_mode = ta.NewType('MaybeMode', ta.Literal[None, 'x'])  # type: ignore

    mode_dispatch = reflect_runtime_dispatch(mode, reflector)
    mode_type = reflector.reflect_type(mode)
    assert mode_dispatch.type_shape.new_type is not None
    assert mode_dispatch.type_shape.new_type.obj is mode
    assert mode_dispatch.type_shape.original is mode_type
    assert mode_dispatch.type_shape.literal_value_type is not None
    assert mode_dispatch.type_shape.literal_value_type.values == ('a', 'b')
    assert mode_dispatch.runtime_class is None
    assert reflector.reflect_type(mode) is mode_type
    assert reflector.type_key(mode_type) is reflector.type_key(mode_type)
    assert reflector.type_key(mode_dispatch.type_shape.original) is reflector.type_key(mode_type)

    maybe_dispatch = reflect_runtime_dispatch(maybe_mode, reflector)
    assert maybe_dispatch.type_shape.new_type is not None
    assert maybe_dispatch.type_shape.new_type.obj is maybe_mode
    assert maybe_dispatch.type_shape.effective is maybe_dispatch.collection_shape.type_shape.effective
    assert maybe_dispatch.runtime_class is None


def test_runtime_dispatch_marks_any_and_none() -> None:
    reflector = _make_reflector()

    any_dispatch = reflect_runtime_dispatch(ta.Any, reflector)
    none_dispatch = get_runtime_dispatch(reflector.reflect_type(None), reflector)

    assert any_dispatch.is_any
    assert not any_dispatch.is_none
    assert any_dispatch.runtime_class is None
    assert none_dispatch.is_none
    assert not none_dispatch.is_any
    assert none_dispatch.runtime_class is None


def test_optional_queries_extract_single_non_none_item() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(int | None)

    assert is_optional_type(typ)
    item = get_optional_item(typ)
    assert item is not None
    assert type_str(item) == 'builtins.int'
    assert type_str(reflect_optional_item(int | None, reflector)) == 'builtins.int'  # type: ignore


def test_optional_query_rejects_multi_item_union() -> None:
    reflector = _make_reflector()

    assert get_optional_item(reflector.reflect_type(int | str | None)) is None
    assert not is_optional_type(reflector.reflect_type(int | str | None))


def test_literal_value_type_accepts_same_typed_literals() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(ta.Literal['a', 'b'])

    literal_info = get_literal_value_type(typ)
    assert literal_info is not None
    assert literal_info.value_type is str
    assert literal_info.values == ('a', 'b')

    reflected_info = reflect_literal_value_type(ta.Literal[1, 2], reflector)
    assert reflected_info is not None
    assert reflected_info.value_type is int
    assert reflected_info.values == (1, 2)

    bytes_info = reflect_literal_value_type(ta.Literal[b'a', b'b'], reflector)
    assert bytes_info is not None
    assert bytes_info.value_type is bytes
    assert bytes_info.values == (b'a', b'b')

    none_info = reflect_literal_value_type(ta.Literal[None], reflector)
    assert none_info is not None
    assert none_info.value_type is type(None)
    assert none_info.values == (None,)


def test_literal_value_type_rejects_mixed_literal_types() -> None:
    reflector = _make_reflector()

    assert get_literal_value_type(reflector.reflect_type(ta.Literal['a', 1])) is None
    assert get_literal_value_type(reflector.reflect_type(ta.Literal['a', b'a'])) is None


def test_enum_literal_reflects_mypy_style_name_with_enum_fallback() -> None:
    class Color(enum.Enum):
        RED = 1
        BLUE = 2

    reflector = _make_reflector()
    typ = reflector.reflect_type(ta.Literal[Color.RED])

    assert isinstance(typ, types.LiteralType)
    assert typ.value == 'RED'
    assert typ.fallback.type.is_enum
    assert typ.fallback.type.enum_members == ('RED', 'BLUE')
    assert '.Color@' in type_str(typ)
    assert type_str(typ).endswith('.RED]')
    assert type_key(typ) != type_key(reflector.reflect_type(ta.Literal['RED']))
    assert reflector.to_runtime_annotation(typ) == ta.Literal[Color.RED]


def test_runtime_literal_value_type_reconstructs_enum_members() -> None:
    class Color(enum.Enum):
        RED = 1
        BLUE = 2

    reflector = _make_reflector()
    typ = reflector.reflect_type(ta.Literal[Color.RED, Color.BLUE])

    literal_info = get_literal_value_type(typ)
    assert literal_info is not None
    assert literal_info.value_type is str
    assert literal_info.values == ('RED', 'BLUE')

    runtime_info = get_runtime_literal_value_type(typ, reflector.universe)
    assert runtime_info is not None
    assert runtime_info.value_type is Color
    assert runtime_info.values == (Color.RED, Color.BLUE)
    assert reflect_runtime_literal_value_type(ta.Literal[Color.RED, Color.BLUE], reflector) == runtime_info


def test_runtime_literal_value_type_rejects_mixed_enum_and_plain_string_literals() -> None:
    class Color(enum.Enum):
        RED = 1

    reflector = _make_reflector()

    assert reflect_literal_value_type(ta.Literal[Color.RED, 'RED'], reflector) is not None
    assert reflect_runtime_literal_value_type(ta.Literal[Color.RED, 'RED'], reflector) is None


def test_literal_union_query_splits_single_literal_branch() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(ta.Literal['a', 'b'] | int)

    literal_union = destructure_literal_union(typ)

    assert literal_union is not None
    assert literal_union.value_type is str
    assert literal_union.values == ('a', 'b')
    assert type_str(literal_union.non_literal) == 'builtins.int'

    reflected_union = reflect_literal_union(ta.Literal[1, 2] | str, reflector)
    assert reflected_union is not None
    assert reflected_union.value_type is int
    assert reflected_union.values == (1, 2)
    assert type_str(reflected_union.non_literal) == 'builtins.str'


def test_literal_union_query_rejects_non_matching_shapes() -> None:
    reflector = _make_reflector()

    assert destructure_literal_union(reflector.reflect_type(ta.Literal['a'])) is None
    assert destructure_literal_union(reflector.reflect_type(ta.Literal['a'] | ta.Literal[1])) is None  # noqa


def test_primitive_union_query_splits_primitive_runtime_classes() -> None:
    reflector = _make_reflector()
    typ = reflector.reflect_type(int | str | list[int])

    primitive_union = destructure_primitive_union(typ, universe=reflector.universe)

    assert primitive_union is not None
    assert primitive_union.primitives == (int, str)
    assert len(primitive_union.non_primitives) == 1
    assert type_str(primitive_union.non_primitives[0]) == 'builtins.list[builtins.int]'

    reflected_union = reflect_primitive_union(int | bool, reflector=reflector)
    assert reflected_union is not None
    assert reflected_union.primitives == (int, bool)
    assert reflected_union.non_primitives == ()


def test_primitive_union_query_rejects_unhandled_shapes() -> None:
    reflector = _make_reflector()

    assert destructure_primitive_union(
        reflector.reflect_type(list[int] | dict[str, int]),
        universe=reflector.universe,
    ) is None
    assert destructure_primitive_union(
        reflector.reflect_type(int | list[int] | dict[str, int]),
        universe=reflector.universe,
    ) is None


def test_query_helpers_handle_raw_nodes() -> None:
    none_type = types.NoneType()
    int_info = _make_reflector().universe.get_type_info(int)
    int_type = types.Instance(int_info, [])
    union = types.UnionType([none_type, int_type])

    assert type_str(get_optional_item(union)) == 'builtins.int'  # type: ignore

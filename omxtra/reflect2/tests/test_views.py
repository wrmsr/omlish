# ruff: noqa: F821 PLC0132 SLF001
import typing as ta

from ..core import types
from ..core.strconv import type_str
from ..ops import reflect_structural_join
from ..ops import reflect_structural_meet
from ..queries import get_runtime_collection_shape
from ..queries import get_runtime_dispatch
from ..queries import get_runtime_mapping_shape
from ..queries import get_runtime_type_keys
from ..queries import get_runtime_type_shape
from ..reflect import RuntimeTypeReflector
from ..universe import RuntimeTypeUniverse
from ..views import get_runtime_type_view
from ..views import reflect_runtime_type_view


def test_runtime_type_view_bundles_existing_query_surfaces() -> None:
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())
    typ = reflector.reflect_type(dict[str, int])

    view = get_runtime_type_view(typ, reflector)

    assert view.typ is typ
    assert view.shape == get_runtime_type_shape(typ, reflector)
    assert view.collection == get_runtime_collection_shape(typ, reflector)
    assert view.mapping == get_runtime_mapping_shape(typ, reflector)
    assert view.dispatch == get_runtime_dispatch(typ, reflector)
    assert view.keys == get_runtime_type_keys(typ, reflector)
    assert view.mapping is not None
    assert type_str(view.mapping.key.effective) == 'builtins.str'
    assert type_str(view.mapping.value.effective) == 'builtins.int'


def test_reflect_runtime_type_view_handles_recursive_alias_container() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    node_list = ta.TypeAliasType('NodeList', list[alias])  # type: ignore
    reflector = RuntimeTypeReflector(
        RuntimeTypeUniverse(),
        forward_ref_resolver={'Node': alias}.__getitem__,
    )

    view = reflect_runtime_type_view(node_list, reflector)
    unrolled = reflector.reflect_type(list[int | list[alias]])  # type: ignore

    assert view.collection.sequence_item is not None
    assert type_str(view.collection.sequence_item).endswith('.Node')
    assert view.keys.structural == reflector.structural_type_key(unrolled)


def test_runtime_type_view_composes_with_structural_join_for_recursive_alias() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    unrolled = int | list[alias]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    joined = reflect_structural_join(alias, unrolled, reflector)
    view = get_runtime_type_view(joined, reflector)
    unrolled_view = reflect_runtime_type_view(unrolled, reflector)

    assert view.typ is reflector.reflect_type(alias)
    assert view.shape.alias is not None
    assert view.keys.structural == unrolled_view.keys.structural


def test_runtime_type_view_composes_with_structural_meet_for_recursive_alias() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    unrolled = int | list[alias]  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    met = reflect_structural_meet(alias, unrolled, reflector)
    view = get_runtime_type_view(met, reflector)
    unrolled_view = reflect_runtime_type_view(unrolled, reflector)

    assert view.typ is reflector.reflect_type(alias)
    assert view.shape.alias is not None
    assert view.keys.structural == unrolled_view.keys.structural


def test_runtime_type_view_composes_with_structural_join_for_incompatible_recursive_aliases() -> None:
    left = ta.TypeAliasType('Left', int | list['Left'])  # type: ignore
    right = ta.TypeAliasType('Right', str | list['Right'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    joined = reflect_structural_join(left, right, reflector)
    view = get_runtime_type_view(joined, reflector)

    assert isinstance(joined, types.UnionType)
    assert view.typ is joined
    assert view.shape.primitive_union is None
    assert view.collection.sequence_item is None
    assert view.keys.structural == reflector.structural_type_key(joined)


def test_runtime_type_view_composes_with_structural_meet_for_incompatible_recursive_aliases() -> None:
    left = ta.TypeAliasType('Left', int | list['Left'])  # type: ignore
    right = ta.TypeAliasType('Right', str | list['Right'])  # type: ignore
    reflector = RuntimeTypeReflector(RuntimeTypeUniverse())

    met = reflect_structural_meet(left, right, reflector)
    view = get_runtime_type_view(met, reflector)

    assert isinstance(met, types.UninhabitedType)
    assert view.typ is met
    assert view.dispatch.is_any is False
    assert view.dispatch.is_none is False
    assert view.keys.structural == reflector.structural_type_key(met)

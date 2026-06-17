# ruff: noqa: F821 PLC0132 SLF001
import collections.abc as cabc
import typing as ta

import pytest

from ...core import types
from ...core.strconv import type_str
from ...errors import ReflectionError
from ...errors import UnreflectableTypeError
from ...reflect import TypeReflector
from ...reflect import reflect_type
from ...universe import TypeUniverse
from ..ops import reflect_base_args
from ..ops import reflect_base_args_or_none
from ..ops import reflect_base_instance
from ..ops import reflect_base_instance_or_none
from ..ops import reflect_instance
from ..ops import reflect_instance_args
from ..ops import reflect_instance_info
from ..ops import reflect_is_alpha_equivalent
from ..ops import reflect_is_assignable
from ..ops import reflect_is_assignable_or_false
from ..ops import reflect_is_same_type
from ..ops import reflect_join
from ..ops import reflect_join_list
from ..ops import reflect_meet
from ..ops import reflect_meet_list
from ..ops import reflect_mro_entries
from ..ops import reflect_mro_entries_or_none
from ..ops import reflect_mro_instances
from ..ops import reflect_mro_instances_or_none
from ..ops import reflect_mro_type_strs
from ..ops import reflect_structural_join
from ..ops import reflect_structural_join_list
from ..ops import reflect_structural_meet
from ..ops import reflect_structural_meet_list
from ..ops import reflect_substitute_type
from ..ops import reflect_substitute_types
from ..ops import reflect_type_str
from ..ops import reflect_type_strs


def test_default_reflection_entrypoint_handles_simple_runtime_forms() -> None:
    assert type_str(reflect_type(int)) == 'builtins.int'
    assert type_str(reflect_type(list[int])) == 'builtins.list[builtins.int]'
    assert type_str(reflect_type(int | None)) == 'Union[builtins.int, None]'


def test_factory_entrypoint_wires_universe_and_forward_ref_resolver() -> None:
    class Local:
        pass

    reflector = TypeReflector(
        TypeUniverse(dynamic_type_name_suffix='counter'),
        forward_ref_resolver=lambda name: {'User': int}[name],
    )

    assert reflect_type_str(Local, reflector).endswith('.Local@1')
    assert reflect_type_str('User', reflector) == 'builtins.int'
    assert reflect_is_same_type('User', int, reflector)


def test_explicit_reflector_state_is_shared_across_convenience_entrypoints() -> None:
    class Local:
        pass

    reflector = TypeReflector(TypeUniverse(dynamic_type_name_suffix='counter'))

    direct = reflector.reflect_type(Local)

    assert reflect_instance(Local, reflector) is direct
    assert reflect_instance_info(Local, reflector) is reflect_instance(Local, reflector).type
    assert reflect_type_str(Local, reflector).endswith('.Local@1')


def test_runtime_operation_entrypoints_accept_runtime_type_objects() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    reflector = TypeReflector(TypeUniverse(dynamic_type_name_suffix='counter'))

    assert isinstance(reflect_join(IntBox, Box[int], reflector), types.Instance)  # type: ignore
    assert isinstance(reflect_join_list([IntBox, Box[int]], reflector), types.Instance)  # type: ignore
    assert reflect_meet(IntBox, Box[int], reflector) is reflect_instance(IntBox, reflector)  # type: ignore
    assert type_str(reflect_meet_list([IntBox, Box[int]], reflector)).endswith('.IntBox@1')  # type: ignore

    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    unrolled = int | list[alias]  # type: ignore
    assert reflect_structural_join(alias, unrolled, reflector) is reflector.reflect_type(alias)
    assert reflect_structural_join_list([alias, unrolled], reflector) is reflector.reflect_type(alias)
    assert reflect_structural_meet(alias, unrolled, reflector) is reflector.reflect_type(alias)
    assert reflect_structural_meet_list([alias, unrolled], reflector) is reflector.reflect_type(alias)

    assert reflect_is_assignable(IntBox, Box[int], reflector)  # type: ignore
    assert not reflect_is_assignable_or_false(Box[str], IntBox, reflector)  # type: ignore
    assert reflect_is_same_type(ta.Optional[int], int | None, reflector)  # noqa
    assert reflect_is_alpha_equivalent(list[t_var], list[u_var], reflector)  # type: ignore

    assert reflect_type_str(Box[int], reflector).endswith('.Box@2[builtins.int]')  # type: ignore
    assert reflect_type_strs([int, str], reflector) == ['builtins.int', 'builtins.str']
    assert [type_str(arg) for arg in reflect_instance_args(Box[int], reflector)] == ['builtins.int']  # type: ignore

    base_args = reflect_base_args(IntBox, Box, reflector)
    assert base_args is not None
    assert [type_str(arg) for arg in base_args] == ['builtins.int']
    assert [
        type_str(arg)
        for arg in ta.cast(list[types.Type], reflect_base_args_or_none(IntBox, Box, reflector))
    ] == [
        'builtins.int',
    ]

    base_instance = reflect_base_instance(IntBox, Box, reflector)
    assert base_instance is not None
    assert base_instance.type is reflect_instance_info(Box[int], reflector)  # type: ignore
    assert type_str(ta.cast(types.Instance, reflect_base_instance_or_none(IntBox, Box, reflector))) == (
        type_str(base_instance)
    )

    assert [entry.info for entry in reflect_mro_entries(IntBox, reflector)] == [
        instance.type
        for instance in reflect_mro_instances(IntBox, reflector)
    ]
    assert reflect_mro_entries_or_none(IntBox, reflector) is not None
    assert reflect_mro_instances_or_none(IntBox, reflector) is not None
    assert reflect_mro_type_strs(IntBox, reflector)[:2] == [
        f'{IntBox.__module__}.{IntBox.__qualname__}@1',
        f'{Box.__module__}.{Box.__qualname__}@2[builtins.int]',
    ]

    assert type_str(reflect_substitute_type(list[t_var], {t_var: str}, reflector)) == 'builtins.list[builtins.str]'  # type: ignore  # noqa
    assert [
        type_str(typ)
        for typ in reflect_substitute_types([list[t_var], dict[str, t_var]], {t_var: str}, reflector)  # type: ignore  # noqa
    ] == [
        'builtins.list[builtins.str]',
        'builtins.dict[builtins.str, builtins.str]',
    ]


def test_runtime_entrypoints_preserve_known_collection_abc_mappings() -> None:
    reflector = TypeReflector(TypeUniverse())

    assert reflect_is_assignable(list[int], cabc.Sequence[int], reflector)
    assert type_str(ta.cast(types.Instance, reflect_base_instance(list[int], cabc.Sequence, reflector))) == (
        'collections.abc.Sequence[builtins.int]'
    )
    assert [
        type_str(arg)
        for arg in ta.cast(list[types.Type], reflect_base_args(dict[str, int], cabc.Mapping, reflector))
    ] == [
        'builtins.str',
        'builtins.int',
    ]


def test_runtime_entrypoints_fail_closed_for_unreflectable_inputs() -> None:
    reflector = TypeReflector(TypeUniverse())

    with pytest.raises(UnreflectableTypeError):
        reflect_type(object())

    with pytest.raises(UnreflectableTypeError):
        reflect_type_str(object(), reflector)

    with pytest.raises(UnreflectableTypeError):
        reflect_join(object(), int, reflector)

    with pytest.raises(UnreflectableTypeError):
        reflect_meet(object(), int, reflector)


def test_runtime_entrypoints_raise_type_error_for_wrong_operation_shape() -> None:
    reflector = TypeReflector(TypeUniverse())

    with pytest.raises(ReflectionError, match='instance type'):
        reflect_instance(int | str, reflector)

    with pytest.raises(ReflectionError, match='base target'):
        reflect_base_args(list[int], int | str, reflector)

    with pytest.raises(ReflectionError, match='base target'):
        reflect_base_instance(list[int], int | str, reflector)

    with pytest.raises(ReflectionError, match='MRO source'):
        reflect_mro_entries(int | str, reflector)

    with pytest.raises(ReflectionError, match='substitution key'):
        reflect_substitute_type(list[int], {int: str}, reflector)

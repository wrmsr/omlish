# ruff: noqa: F821 PLC0132 SLF001
# ruff: noqa: PYI059
import annotationlib
import collections.abc as cabc
import sys
import types as pytypes
import typing as ta

import pytest

from ..api import Api
from ..api import global_api
from ..core import symbols
from ..core import types
from ..core.strconv import type_str
from ..core.substitute import substitute_type
from ..core.subtypes import get_mro_instances
from ..core.subtypes import is_alpha_equivalent
from ..core.subtypes import is_equivalent
from ..core.subtypes import is_same_type
from ..core.subtypes import is_subtype
from ..core.typekeys import tuple_type_key
from ..core.typekeys import type_key
from ..core.typeops import get_proper_type
from ..core.types import Type
from ..errors import ReflectionValueError
from ..errors import UnreflectableTypeError
from ..reflector import ForwardRefResolution
from .helpers import make_reflector


def reflect_type(obj: object) -> Type:
    return global_api().reflector.reflect_type(obj)


def test_reflects_bare_runtime_class_as_instance() -> None:
    reflector = make_reflector()

    typ = reflector.reflect_type(int)

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.int'
    assert typ.args == ()


def test_reflects_builtin_generic_alias() -> None:
    reflector = make_reflector()

    typ = reflector.reflect_type(dict[str, int])

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.dict'
    assert [type_str(arg) for arg in typ.args] == ['builtins.str', 'builtins.int']


def test_reflects_omitted_generic_args_as_any() -> None:
    reflector = make_reflector()

    typ = reflector.reflect_type(list)

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.list'
    assert [type_str(arg) for arg in typ.args] == ['Any']
    assert isinstance(typ.args[0], types.AnyType)
    assert typ.args[0].type_of_any == types.TypeOfAny.FROM_OMITTED_GENERICS  # noqa


def test_reflects_any_and_none() -> None:
    assert isinstance(reflect_type(ta.Any), types.AnyType)
    assert isinstance(reflect_type(None), types.NoneType)
    assert isinstance(reflect_type(type(None)), types.NoneType)


def test_reflects_never_and_no_return_as_uninhabited() -> None:
    assert isinstance(reflect_type(ta.Never), types.UninhabitedType)
    assert isinstance(reflect_type(ta.NoReturn), types.UninhabitedType)


def test_reflects_tuple_aliases() -> None:
    reflector = make_reflector()

    fixed = reflector.reflect_type(tuple[int, str])
    variadic = reflector.reflect_type(tuple[int, ...])

    assert isinstance(fixed, types.TupleType)
    assert [type_str(item) for item in fixed.items] == ['builtins.int', 'builtins.str']
    assert type_str(fixed.partial_fallback) == 'builtins.tuple[Any]'

    assert isinstance(variadic, types.Instance)
    assert variadic.type.fullname == 'builtins.tuple'
    assert [type_str(arg) for arg in variadic.args] == ['builtins.int']


def test_reflects_pep604_union() -> None:
    typ = reflect_type(int | None)

    assert isinstance(typ, types.UnionType)
    assert [type_str(item) for item in typ.items] == ['builtins.int', 'None']


def test_reflection_cache_returns_same_type_for_same_object() -> None:
    reflector = make_reflector()

    assert reflector.reflect_type(list[int]) is reflector.reflect_type(list[int])


def test_reflection_cache_skips_unhashable_runtime_forms() -> None:
    reflector = make_reflector()
    form = ta.Annotated[int, []]  # noqa

    with pytest.raises(TypeError):
        hash(form)

    left = reflector.reflect_type(form)
    right = reflector.reflect_type(form)

    assert left is not right
    assert type_str(left) == type_str(right) == 'Annotated[builtins.int, ...]'
    assert isinstance(left, types.AnnotatedType)
    assert isinstance(right, types.AnnotatedType)
    assert left.metadata == right.metadata == ([],)


def test_make_runtime_reflector_accepts_dynamic_name_suffix() -> None:
    class Local:
        pass

    reflector = make_reflector(
        dynamic_type_name_suffix='counter',
    )

    typ = reflector.reflect_type(Local)

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname.endswith('.Local@1')


def test_separate_reflectors_assign_distinct_dynamic_type_infos() -> None:
    class Local:
        pass

    left_reflector = make_reflector(
        dynamic_type_name_suffix='counter',
    )
    right_reflector = make_reflector(
        dynamic_type_name_suffix='counter',
    )

    left = left_reflector.reflect_type(Local)
    right = right_reflector.reflect_type(Local)

    assert isinstance(left, types.Instance)
    assert isinstance(right, types.Instance)
    assert left.type is not right.type
    assert left.type.fullname == right.type.fullname
    assert not is_same_type(left, right)


def test_reflects_type_var() -> None:
    reflector = make_reflector()
    rt_type_var = ta.TypeVar('T')  # type: ignore

    typ = reflector.reflect_type(rt_type_var)

    assert isinstance(typ, types.TypeVarType)
    assert typ.name == 'T'
    assert typ.fullname == 'T'
    assert typ.values == ()
    assert typ.upper_bound.type.fullname == 'builtins.object'  # type: ignore
    assert isinstance(typ.default, types.AnyType)


def test_reflects_bound_type_var() -> None:
    reflector = make_reflector()
    rt_type_var = ta.TypeVar('T', bound=int)  # type: ignore

    typ = reflector.reflect_type(rt_type_var)

    assert isinstance(typ, types.TypeVarType)
    assert type_str(typ.upper_bound) == 'builtins.int'


def test_reflects_constrained_type_var() -> None:
    reflector = make_reflector()
    rt_type_var = ta.TypeVar('T', int, str)  # type: ignore

    typ = reflector.reflect_type(rt_type_var)

    assert isinstance(typ, types.TypeVarType)
    assert [type_str(value) for value in typ.values] == ['builtins.int', 'builtins.str']


def test_reflects_type_var_variance() -> None:
    covariant = make_reflector().reflect_type(ta.TypeVar('T', covariant=True))
    contravariant = make_reflector().reflect_type(ta.TypeVar('T', contravariant=True))

    assert isinstance(covariant, types.TypeVarType)
    assert covariant.variance == symbols.VarianceKind.CO
    assert isinstance(contravariant, types.TypeVarType)
    assert contravariant.variance == symbols.VarianceKind.CONTRA


def test_reflects_type_var_inside_generic_alias() -> None:
    reflector = make_reflector()
    rt_type_var = ta.TypeVar('T')  # type: ignore

    typ = reflector.reflect_type(list[rt_type_var])  # type: ignore

    assert isinstance(typ, types.Instance)
    assert len(typ.args) == 1
    assert isinstance(typ.args[0], types.TypeVarType)
    assert typ.args[0].name == 'T'


def test_reflects_type_var_inside_multi_arg_generic_alias() -> None:
    reflector = make_reflector()
    rt_type_var = ta.TypeVar('T')  # type: ignore

    typ = reflector.reflect_type(dict[str, rt_type_var])  # type: ignore

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.dict'
    assert [type_str(arg) for arg in typ.args] == ['builtins.str', 'T']
    assert isinstance(typ.args[1], types.TypeVarType)


def test_reflects_type_var_inside_abc_generic_alias() -> None:
    reflector = make_reflector()
    rt_type_var = ta.TypeVar('T')  # type: ignore

    typ = reflector.reflect_type(cabc.Sequence[rt_type_var])  # type: ignore

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'collections.abc.Sequence'
    assert [type_str(arg) for arg in typ.args] == ['T']
    assert isinstance(typ.args[0], types.TypeVarType)


def test_reflects_bound_type_var_with_parameterized_bound() -> None:
    reflector = make_reflector()
    rt_type_var = ta.TypeVar('T', bound=cabc.Sequence[int])  # type: ignore

    typ = reflector.reflect_type(rt_type_var)

    assert isinstance(typ, types.TypeVarType)
    assert type_str(typ.upper_bound) == 'collections.abc.Sequence[builtins.int]'


def test_type_var_reflection_cache_uses_runtime_object_identity() -> None:
    reflector = make_reflector()
    left = ta.TypeVar('T')  # type: ignore
    right = ta.TypeVar('T')  # type: ignore

    assert reflector.reflect_type(left) is reflector.reflect_type(left)
    assert reflector.reflect_type(left) is not reflector.reflect_type(right)


def test_separate_reflectors_assign_distinct_runtime_type_vars() -> None:
    rt_type_var = ta.TypeVar('T')  # type: ignore
    left_reflector = make_reflector(
        dynamic_type_name_suffix='id',
    )
    right_reflector = make_reflector(
        dynamic_type_name_suffix='id',
    )

    left = left_reflector.reflect_type(rt_type_var)
    right = right_reflector.reflect_type(rt_type_var)

    assert isinstance(left, types.TypeVarType)
    assert isinstance(right, types.TypeVarType)
    assert left is not right
    assert not is_same_type(left, right)


def test_cross_reflector_type_var_substitution_does_not_match_by_runtime_object() -> None:
    rt_type_var = ta.TypeVar('T')  # type: ignore
    key_reflector = make_reflector(
        dynamic_type_name_suffix='id',
    )
    type_reflector = make_reflector(
        dynamic_type_name_suffix='id',
    )

    key = key_reflector.reflect_type(rt_type_var)
    typ = type_reflector.reflect_type(list[rt_type_var])  # type: ignore
    value = type_reflector.reflect_type(int)

    assert isinstance(key, types.TypeVarType)
    assert isinstance(typ, types.Instance)
    assert isinstance(value, types.Instance)

    substituted = substitute_type(typ, {key: value})

    assert type_str(substituted) == 'builtins.list[T]'


def test_same_runtime_type_var_compares_same_after_reflection() -> None:
    reflector = make_reflector()
    rt_type_var = ta.TypeVar('T')  # type: ignore

    left = reflector.reflect_type(list[rt_type_var])  # type: ignore
    right = reflector.reflect_type(list[rt_type_var])  # type: ignore

    assert is_same_type(left, right)
    assert is_equivalent(left, right)


def test_different_runtime_type_vars_with_same_name_are_not_strictly_same() -> None:
    reflector = make_reflector()
    left_var = ta.TypeVar('T')  # type: ignore
    right_var = ta.TypeVar('T')  # type: ignore

    left = reflector.reflect_type(list[left_var])  # type: ignore
    right = reflector.reflect_type(list[right_var])  # type: ignore

    assert not is_same_type(left, right)
    assert not is_equivalent(left, right)
    assert is_alpha_equivalent(left, right)


def test_bounded_runtime_type_vars_with_same_name_are_not_strictly_same() -> None:
    reflector = make_reflector()
    left_var = ta.TypeVar('T', bound=cabc.Sequence[int])  # type: ignore
    right_var = ta.TypeVar('T', bound=cabc.Sequence[int])  # type: ignore

    left = reflector.reflect_type(list[left_var])  # type: ignore
    right = reflector.reflect_type(list[right_var])  # type: ignore

    assert not is_same_type(left, right)
    assert is_alpha_equivalent(left, right)


def test_constrained_runtime_type_vars_with_same_name_are_not_strictly_same() -> None:
    reflector = make_reflector()
    left_var = ta.TypeVar('T', int, str)  # type: ignore
    right_var = ta.TypeVar('T', int, str)  # type: ignore

    left = reflector.reflect_type(list[left_var])  # type: ignore
    right = reflector.reflect_type(list[right_var])  # type: ignore

    assert not is_same_type(left, right)
    assert is_alpha_equivalent(left, right)


def test_reflection_reflects_param_spec() -> None:
    reflector = make_reflector()
    param_spec = ta.ParamSpec('P')  # type: ignore

    typ = reflector.reflect_type(param_spec)

    assert isinstance(typ, types.ParamSpecType)
    assert typ.name == 'P'
    assert reflector.reflect_type(param_spec) is typ


def test_reflection_reflects_type_var_tuple() -> None:
    reflector = make_reflector()
    type_var_tuple = ta.TypeVarTuple('Ts')  # type: ignore

    typ = reflector.reflect_type(type_var_tuple)

    assert isinstance(typ, types.TypeVarTupleType)
    assert typ.name == 'Ts'
    assert type_str(typ.tuple_fallback) == 'builtins.tuple[Any]'
    assert reflector.reflect_type(type_var_tuple) is typ


def test_reflects_unpack_wrapper() -> None:
    typ = reflect_type(ta.Unpack[tuple[int, str]])

    assert isinstance(typ, types.UnpackType)
    assert type_str(typ.type) == 'tuple[builtins.int, builtins.str]'


def test_reflects_unpack_inside_tuple_alias() -> None:
    typ = reflect_type(tuple[ta.Unpack[tuple[int, str]]])  # noqa

    assert isinstance(typ, types.TupleType)
    assert len(typ.items) == 1
    assert isinstance(typ.items[0], types.UnpackType)
    assert type_str(typ.items[0]) == 'Unpack[tuple[builtins.int, builtins.str]]'


def test_rejects_bare_unpack() -> None:
    with pytest.raises(UnreflectableTypeError):
        reflect_type(ta.Unpack)


def test_reflects_unpack_of_type_var_tuple() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore

    typ = reflect_type(ta.Unpack[ts_var])

    assert isinstance(typ, types.UnpackType)
    assert isinstance(typ.type, types.TypeVarTupleType)
    assert typ.type.name == 'Ts'


def test_reflects_tuple_unpack_of_type_var_tuple() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore

    typ = reflect_type(tuple[ta.Unpack[ts_var]])  # type: ignore  # noqa

    assert isinstance(typ, types.TupleType)
    assert len(typ.items) == 1
    assert isinstance(typ.items[0], types.UnpackType)
    assert isinstance(typ.items[0].type, types.TypeVarTupleType)
    assert typ.items[0].type.name == 'Ts'


def test_reflects_single_literal() -> None:
    typ = reflect_type(ta.Literal['x'])

    assert isinstance(typ, types.LiteralType)
    assert typ.value == 'x'
    assert typ.fallback.type.fullname == 'builtins.str'


def test_reflects_bool_literal_with_bool_fallback() -> None:
    typ = reflect_type(ta.Literal[True])

    assert isinstance(typ, types.LiteralType)
    assert typ.value is True
    assert typ.fallback.type.fullname == 'builtins.bool'


def test_reflects_bytes_literal_with_bytes_fallback_and_string_key() -> None:
    typ = reflect_type(ta.Literal[b'x'])

    assert isinstance(typ, types.LiteralType)
    assert typ.value == b'x'
    assert typ.fallback.type.fullname == 'builtins.bytes'
    assert type_key(typ) == "L[bytes:b'x',I['builtins.bytes']]"


def test_reflects_float_literal_with_float_fallback_and_opaque_key() -> None:
    typ = reflect_type(ta.Literal[1.5])

    assert isinstance(typ, types.LiteralType)
    assert typ.value == 1.5
    assert typ.fallback.type.fullname == 'builtins.float'
    assert type_key(typ) == ("L[$0,I['builtins.float']]", 1.5)


def test_reflects_none_literal_with_none_fallback_and_string_key() -> None:
    typ = reflect_type(ta.Literal[None])

    assert isinstance(typ, types.LiteralType)
    assert typ.value is None
    assert typ.fallback.type.fullname == 'builtins.None'
    assert type_key(typ) == "L[None:,I['builtins.None']]"


def test_reflects_multi_value_literal_as_union() -> None:
    typ = reflect_type(ta.Literal['x', 1, False, b'y', 1.5, None])

    assert isinstance(typ, types.UnionType)
    assert [item.value for item in typ.items if isinstance(item, types.LiteralType)] == [
        'x',
        1,
        False,
        b'y',
        1.5,
        None,
    ]
    assert [item.fallback.type.fullname for item in typ.items if isinstance(item, types.LiteralType)] == [
        'builtins.str',
        'builtins.int',
        'builtins.bool',
        'builtins.bytes',
        'builtins.float',
        'builtins.None',
    ]


def test_rejects_unsupported_literal_value() -> None:
    with pytest.raises(UnreflectableTypeError):
        reflect_type(ta.Literal[object()])


def test_reflects_annotated_as_inner_type() -> None:
    typ = reflect_type(ta.Annotated[int, 'metadata'])

    assert isinstance(typ, types.AnnotatedType)
    assert type_str(typ.item) == 'builtins.int'
    assert typ.metadata == ('metadata',)


def test_reflects_annotated_inside_generic_alias() -> None:
    typ = reflect_type(list[ta.Annotated[int, 'metadata']])

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.list'
    assert [type_str(arg) for arg in typ.args] == ['Annotated[builtins.int, ...]']


def test_reflects_annotated_literal_as_inner_literal() -> None:
    typ = reflect_type(ta.Annotated[ta.Literal['x'], object()])

    assert isinstance(typ, types.AnnotatedType)
    assert isinstance(typ.item, types.LiteralType)
    assert typ.item.value == 'x'


def test_reflects_type_guard_as_type_guarded_type() -> None:
    typ = reflect_type(ta.TypeGuard[int])

    assert isinstance(typ, types.TypeGuardedType)
    assert type_str(typ.type_guard) == 'builtins.int'
    assert type_str(typ) == 'builtins.int'


def test_reflects_type_guard_inside_generic_alias() -> None:
    typ = reflect_type(list[ta.TypeGuard[int]])

    assert isinstance(typ, types.Instance)
    assert type_str(typ) == 'builtins.list[builtins.int]'
    assert isinstance(typ.args[0], types.TypeGuardedType)


def test_rejects_type_is_until_distinct_representation_exists() -> None:
    with pytest.raises(UnreflectableTypeError, match='TypeIs'):
        reflect_type(ta.TypeIs[int])


def test_reflects_newtype_as_supertype() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore

    typ = make_reflector().reflect_type(user_id)

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == f'{__name__}.UserId'
    assert [base.type.fullname for base in typ.type.bases if isinstance(base, types.Instance)] == ['builtins.int']


def test_reflects_newtype_inside_generic_alias_as_supertype() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore

    typ = make_reflector().reflect_type(list[user_id])

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.list'
    assert [type_str(arg) for arg in typ.args] == [f'{__name__}.UserId']


def test_reflects_newtype_with_literal_supertype() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    typ = make_reflector().reflect_type(mode)

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == f'{__name__}.Mode'
    assert [type_str(base) for base in typ.type.bases] == ['builtins.object']


def test_new_type_reflection_is_cached_by_newtype_object() -> None:
    reflector = make_reflector()
    user_id = ta.NewType('UserId', int)  # type: ignore

    typ = reflector.reflect_type(user_id)

    assert reflector.reflect_type(user_id) is typ
    assert reflector._type_cache[user_id] is typ


def test_reflects_type_alias_type_by_preserving_alias_identity() -> None:
    alias = ta.TypeAliasType('Alias', list[int])  # type: ignore

    typ = reflect_type(alias)

    assert isinstance(typ, types.TypeAliasType)
    assert typ.alias is not None
    assert typ.alias.runtime_object is alias
    assert type_str(typ) == f'{__name__}.Alias'
    assert type_str(get_proper_type(typ)) == 'builtins.list[builtins.int]'


def test_type_alias_keys_preserve_runtime_alias_object_identity() -> None:
    reflector = make_reflector()
    left = ta.TypeAliasType('Alias', list[int])  # type: ignore
    right = ta.TypeAliasType('Alias', list[int])  # type: ignore

    left_type = reflector.reflect_type(left)
    right_type = reflector.reflect_type(right)

    assert isinstance(left_type, types.TypeAliasType)
    assert isinstance(right_type, types.TypeAliasType)
    assert left_type.alias is not None
    assert right_type.alias is not None
    assert left_type.alias.runtime_object is left
    assert right_type.alias.runtime_object is right
    assert type_key(left_type) != type_key(right_type)


def test_reflects_type_alias_type_inside_generic_alias() -> None:
    alias = ta.TypeAliasType('Alias', list[int])  # type: ignore

    typ = reflect_type(dict[str, alias])  # type: ignore

    assert isinstance(typ, types.Instance)
    assert type_str(typ) == f'builtins.dict[builtins.str, {__name__}.Alias]'
    assert isinstance(typ.args[1], types.TypeAliasType)
    assert type_str(get_proper_type(typ.args[1])) == 'builtins.list[builtins.int]'


def test_reflects_unsubscripted_generic_type_alias_type_with_type_var() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Alias', list[t_var], type_params=(t_var,))  # type: ignore

    typ = reflect_type(alias)

    assert isinstance(typ, types.TypeAliasType)
    assert type_str(typ) == f'{__name__}.Alias'
    target = get_proper_type(typ)
    assert isinstance(target, types.Instance)
    assert type_str(target) == 'builtins.list[T]'
    assert isinstance(target.args[0], types.TypeVarType)


def test_reflects_subscripted_generic_type_alias_type_by_substituting_args() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Alias', dict[str, t_var], type_params=(t_var,))  # type: ignore

    typ = reflect_type(alias[int])

    assert isinstance(typ, types.TypeAliasType)
    assert type_str(typ) == f'{__name__}.Alias[builtins.int]'
    assert type_str(get_proper_type(typ)) == 'builtins.dict[builtins.str, builtins.int]'


def test_reflects_subscripted_variadic_type_alias_type_by_packing_args() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore

    typ = reflect_type(alias[int, str])

    assert isinstance(typ, types.TypeAliasType)
    assert len(typ.args) == 1
    assert isinstance(typ.args[0], types.TupleType)
    assert type_str(typ) == f'{__name__}.Alias[tuple[builtins.int, builtins.str]]'
    assert type_str(get_proper_type(typ)) == 'tuple[builtins.int, builtins.str]'


def test_reflects_subscripted_variadic_type_alias_type_with_fixed_prefix_and_suffix() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[t_var, *ts_var, u_var], type_params=(t_var, ts_var, u_var))  # type: ignore

    typ = reflect_type(alias[int, str, bool, bytes])

    assert isinstance(typ, types.TypeAliasType)
    assert len(typ.args) == 3
    assert type_str(typ.args[0]) == 'builtins.int'
    assert isinstance(typ.args[1], types.TupleType)
    assert [type_str(item) for item in typ.args[1].items] == ['builtins.str', 'builtins.bool']
    assert type_str(typ.args[2]) == 'builtins.bytes'
    assert type_str(get_proper_type(typ)) == 'tuple[builtins.int, builtins.str, builtins.bool, builtins.bytes]'


def test_rejects_overapplied_nonvariadic_type_alias_type() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Alias', list[t_var], type_params=(t_var,))  # type: ignore

    with pytest.raises(UnreflectableTypeError, match='type alias arguments'):
        reflect_type(alias[int, str])


def test_rejects_underapplied_variadic_type_alias_type_with_fixed_suffix() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var, u_var], type_params=(ts_var, u_var))  # type: ignore

    with pytest.raises(UnreflectableTypeError, match='type alias arguments'):
        reflect_type(alias[*()])


def test_rejects_type_alias_type_with_multiple_type_var_tuple_parameters() -> None:
    left_ts = ta.TypeVarTuple('LeftTs')  # type: ignore
    right_ts = ta.TypeVarTuple('RightTs')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*left_ts, *right_ts], type_params=(left_ts, right_ts))  # type: ignore

    with pytest.raises(UnreflectableTypeError, match='multiple TypeVarTuple'):
        reflect_type(alias[int, str])


def test_reflects_direct_recursive_type_alias_type_as_alias_node() -> None:
    alias = ta.TypeAliasType('Alias', list['Alias'])  # type: ignore
    reflector = make_reflector()

    typ = reflector.reflect_type(alias)

    assert isinstance(typ, types.TypeAliasType)
    assert typ.is_recursive
    assert type_key(typ) == "RA[I['builtins.list',AR[0]]]"
    assert tuple_type_key(typ) == (
        'recursive_type_alias',
        (),
        (
            'instance',
            'builtins.list',
            (('type_alias_ref', 0, ()),),
            (),
        ),
    )


def test_reflects_indirect_recursive_type_alias_type_as_alias_nodes() -> None:
    alias_a = ta.TypeAliasType('A', list['B'])  # type: ignore
    alias_b = ta.TypeAliasType('B', dict[str, 'A'])  # type: ignore
    aliases = {
        'A': alias_a,
        'B': alias_b,
    }
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: aliases[frr.name],
    )

    typ_a = reflector.reflect_type(alias_a)
    typ_b = reflector.reflect_type(alias_b)

    assert isinstance(typ_a, types.TypeAliasType)
    assert isinstance(typ_b, types.TypeAliasType)
    assert typ_a.is_recursive
    assert typ_b.is_recursive
    assert type_key(typ_a) != type_key(typ_b)


def test_reflects_parameterized_recursive_type_alias_type_as_alias_node() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Alias', list['Alias[T]'], type_params=(t_var,))  # type: ignore
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: {'Alias': alias}[frr.name],
    )

    typ = reflector.reflect_type(alias[int])

    assert isinstance(typ, types.TypeAliasType)
    assert typ.is_recursive
    assert tuple_type_key(typ) == (
        'recursive_type_alias',
        (('instance', 'builtins.int', (), ()),),
        (
            'instance',
            'builtins.list',
            (
                (
                    'type_alias_ref',
                    0,
                    (('instance', 'builtins.int', (), ()),),
                ),
            ),
            (),
        ),
    )


def test_reflects_parameterized_recursive_tuple_type_alias_type_as_alias_node() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[t_var, 'Alias[T]'], type_params=(t_var,))  # type: ignore
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: {'Alias': alias}[frr.name],
    )

    typ = reflector.reflect_type(alias[int])

    assert isinstance(typ, types.TypeAliasType)
    assert typ.is_recursive
    assert tuple_type_key(typ) == (
        'recursive_type_alias',
        (('instance', 'builtins.int', (), ()),),
        (
            'tuple',
            (
                ('instance', 'builtins.int', (), ()),
                (
                    'type_alias_ref',
                    0,
                    (('instance', 'builtins.int', (), ()),),
                ),
            ),
            ('instance', 'builtins.tuple', (('any', types.TypeOfAny.FROM_OMITTED_GENERICS),), ()),
        ),
    )


def test_reflects_variadic_recursive_type_alias_forward_ref_spread_as_packed_arg() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var, 'Alias[*Ts]'], type_params=(ts_var,))  # type: ignore
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: {'Alias': alias}[frr.name],
    )

    typ = reflector.reflect_type(alias[int, str])

    assert isinstance(typ, types.TypeAliasType)
    assert typ.is_recursive
    assert len(typ.args) == 1
    assert isinstance(typ.args[0], types.TupleType)
    assert [type_str(item) for item in typ.args[0].items] == ['builtins.int', 'builtins.str']
    assert typ.alias is not None
    reflected_ts = typ.alias.alias_tvars[0]
    assert isinstance(reflected_ts, types.TypeVarTupleType)
    packed_arg_key = (
        'tuple',
        (
            ('instance', 'builtins.int', (), ()),
            ('instance', 'builtins.str', (), ()),
        ),
        ('instance', 'builtins.tuple', (('any', types.TypeOfAny.FROM_OMITTED_GENERICS),), ()),
    )
    assert tuple_type_key(typ) == (
        'recursive_type_alias',
        (packed_arg_key,),
        (
            'tuple',
            (
                ('instance', 'builtins.int', (), ()),
                ('instance', 'builtins.str', (), ()),
                (
                    'type_alias_ref',
                    0,
                    (
                        packed_arg_key,
                    ),
                ),
            ),
            ('instance', 'builtins.tuple', (('any', types.TypeOfAny.FROM_OMITTED_GENERICS),), ()),
        ),
    )


def test_rejects_type_alias_type_forward_value_until_resolution_exists() -> None:
    reflector = make_reflector(
        unresolved_forward_ref_policy='raise',
    )

    alias = ta.TypeAliasType('Alias', 'Missing')  # type: ignore

    with pytest.raises(UnreflectableTypeError, match='forward reference'):
        reflector.reflect_type(alias)


def test_rejects_raw_string_forward_reference_until_resolution_exists() -> None:
    reflector = make_reflector(
        unresolved_forward_ref_policy='raise',
    )

    with pytest.raises(UnreflectableTypeError, match='forward reference'):
        reflector.reflect_type('Missing')


def test_rejects_annotationlib_forward_reference_until_resolution_exists() -> None:
    reflector = make_reflector(
        unresolved_forward_ref_policy='raise',
    )

    with pytest.raises(UnreflectableTypeError, match='forward reference'):
        reflector.reflect_type(annotationlib.ForwardRef('Missing'))


def test_rejects_typing_forward_reference_until_resolution_exists() -> None:
    reflector = make_reflector(
        unresolved_forward_ref_policy='raise',
    )

    with pytest.raises(UnreflectableTypeError, match='forward reference'):
        reflector.reflect_type(ta.ForwardRef('Missing'))


def test_resolves_raw_string_forward_reference_with_resolver() -> None:
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: {'User': int}[frr.name],
    )

    typ = reflector.reflect_type('User')

    assert isinstance(typ, types.Instance)
    assert type_str(typ) == 'builtins.int'


def test_make_runtime_reflector_accepts_forward_ref_resolver() -> None:
    resolver = lambda frr: {'User': int}[frr.name]
    reflector = make_reflector(
        dynamic_type_name_suffix='id',
        forward_ref_resolver=resolver,
    )

    typ = reflector.reflect_type('User')

    assert isinstance(typ, types.Instance)
    assert type_str(typ) == 'builtins.int'


def test_resolves_annotationlib_forward_reference_with_resolver() -> None:
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: {'User': list[int]}[frr.name],
    )

    typ = reflector.reflect_type(annotationlib.ForwardRef('User'))

    assert isinstance(typ, types.Instance)
    assert type_str(typ) == 'builtins.list[builtins.int]'


def test_resolves_type_alias_type_forward_value_with_resolver() -> None:
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: {'User': str}[frr.name],
    )
    alias = ta.TypeAliasType('Alias', 'User')  # type: ignore

    typ = reflector.reflect_type(alias)

    assert isinstance(typ, types.TypeAliasType)
    assert type_str(typ) == f'{__name__}.Alias'
    assert type_str(get_proper_type(typ)) == 'builtins.str'


def test_forward_reference_resolver_result_must_be_reflectable() -> None:
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: object(),
    )

    with pytest.raises(UnreflectableTypeError):
        reflector.reflect_type('User')


def test_forward_reference_resolver_does_not_mask_nested_unresolved_reference() -> None:
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: annotationlib.ForwardRef('Other'),
    )

    with pytest.raises(UnreflectableTypeError, match='Recursive forward reference'):
        reflector.reflect_type('User')


def test_reflects_typing_callable_with_explicit_args() -> None:
    typ = reflect_type(ta.Callable[[int, str], bool])

    assert isinstance(typ, types.CallableType)
    assert not typ.is_ellipsis_args
    assert [type_str(arg) for arg in typ.arg_types] == ['builtins.int', 'builtins.str']
    assert typ.arg_kinds == (symbols.ArgKind.POS, symbols.ArgKind.POS)
    assert typ.arg_names == (None, None)
    assert type_str(typ.ret_type) == 'builtins.bool'
    assert typ.fallback.type.fullname == 'collections.abc.Callable'


def test_reflects_collections_callable_with_explicit_args() -> None:
    import collections.abc as cabc

    typ = reflect_type(cabc.Callable[[int], str])

    assert isinstance(typ, types.CallableType)
    assert not typ.is_ellipsis_args
    assert [type_str(arg) for arg in typ.arg_types] == ['builtins.int']
    assert type_str(typ.ret_type) == 'builtins.str'


def test_reflects_callable_with_ellipsis_args() -> None:
    typ = reflect_type(ta.Callable[..., int])

    assert isinstance(typ, types.CallableType)
    assert typ.is_ellipsis_args
    assert typ.arg_types == ()
    assert typ.arg_kinds == ()
    assert typ.arg_names == ()
    assert type_str(typ.ret_type) == 'builtins.int'
    assert type_str(typ) == 'def (...) -> builtins.int'


def test_reflects_callable_with_param_spec_args() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    typ = reflect_type(ta.Callable[param_spec, int])  # noqa

    assert isinstance(typ, types.CallableType)
    assert [type(arg).__name__ for arg in typ.arg_types] == ['ParamSpecType', 'ParamSpecType']
    assert typ.arg_kinds == (symbols.ArgKind.STAR, symbols.ArgKind.STAR2)
    assert typ.arg_names == (None, None)
    assert [var.name for var in typ.variables] == ['P']


def test_reflects_callable_with_concatenate_args() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    typ = reflect_type(ta.Callable[ta.Concatenate[int, str, param_spec], bool])  # noqa

    assert isinstance(typ, types.CallableType)
    assert [type_str(arg) for arg in typ.arg_types] == ['builtins.int', 'builtins.str', 'P', 'P']
    assert typ.arg_kinds == (symbols.ArgKind.POS, symbols.ArgKind.POS, symbols.ArgKind.STAR, symbols.ArgKind.STAR2)
    assert [var.name for var in typ.variables] == ['P']


def test_reflects_type_type_alias() -> None:
    typ = reflect_type(type[int])

    assert isinstance(typ, types.TypeType)
    assert type_str(typ.item) == 'builtins.int'


def test_reflects_typing_type_alias() -> None:
    typ = reflect_type(ta.Type[str])  # noqa

    assert isinstance(typ, types.TypeType)
    assert type_str(typ.item) == 'builtins.str'


def test_reflects_type_type_alias_with_any() -> None:
    typ = reflect_type(type[ta.Any])

    assert isinstance(typ, types.TypeType)
    assert isinstance(typ.item, types.AnyType)


def test_reflects_type_type_alias_inside_generic_alias() -> None:
    typ = reflect_type(list[type[int]])

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.list'
    assert len(typ.args) == 1
    assert isinstance(typ.args[0], types.TypeType)
    assert type_str(typ.args[0].item) == 'builtins.int'


def test_reflects_bare_type_as_generic_instance() -> None:
    typ = reflect_type(type)

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.type'
    assert [type_str(arg) for arg in typ.args] == ['Any']


def test_reflects_class_var_as_inner_type() -> None:
    typ = reflect_type(ta.ClassVar[int])

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.int'


def test_reflects_final_as_inner_type() -> None:
    typ = reflect_type(ta.Final[str])

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.str'


def test_reflects_final_inside_generic_alias() -> None:
    typ = reflect_type(list[ta.Final[int]])  # type: ignore

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'builtins.list'
    assert [type_str(arg) for arg in typ.args] == ['builtins.int']


def test_reflects_required_and_not_required_wrappers() -> None:
    required = reflect_type(ta.Required[int])
    not_required = reflect_type(ta.NotRequired[str])

    assert isinstance(required, types.RequiredType)
    assert required.required
    assert type_str(required.item) == 'builtins.int'

    assert isinstance(not_required, types.RequiredType)
    assert not not_required.required
    assert type_str(not_required.item) == 'builtins.str'


def test_reflects_read_only_wrapper() -> None:
    typ = reflect_type(ta.ReadOnly[int])

    assert isinstance(typ, types.ReadOnlyType)
    assert type_str(typ.item) == 'builtins.int'


def test_reflects_typed_dict_wrappers_inside_generic_alias() -> None:
    typ = reflect_type(tuple[ta.Required[int], ta.NotRequired[str], ta.ReadOnly[bool]])  # type: ignore

    assert isinstance(typ, types.TupleType)
    assert [type_str(item) for item in typ.items] == [
        'Required[builtins.int]',
        'NotRequired[builtins.str]',
        'ReadOnly[builtins.bool]',
    ]


def test_reflects_typed_dict_class() -> None:
    class Movie(ta.TypedDict):
        title: str
        year: int

    typ = reflect_type(Movie)

    assert isinstance(typ, types.TypedDictType)
    assert typ.required_keys == {'title', 'year'}
    assert typ.readonly_keys == set()
    assert [type_str(item) for item in typ.items.values()] == [
        'builtins.str',
        'builtins.int',
    ]
    assert type_str(typ) == "TypedDict({'title': builtins.str, 'year': builtins.int})"


def test_reflects_typed_dict_required_not_required_and_read_only_keys() -> None:
    class Movie(ta.TypedDict, total=False):
        title: ta.Required[str]
        year: int
        tag: ta.ReadOnly[ta.NotRequired[str]]
        alias: ta.NotRequired[ta.ReadOnly[int]]

    typ = reflect_type(Movie)

    assert isinstance(typ, types.TypedDictType)
    assert typ.required_keys == {'title'}
    assert typ.readonly_keys == {'tag', 'alias'}
    assert {name: type_str(item) for name, item in typ.items.items()} == {
        'title': 'builtins.str',
        'year': 'builtins.int',
        'tag': 'builtins.str',
        'alias': 'builtins.int',
    }
    assert type_str(typ) == (
        "TypedDict({'title': builtins.str, 'year'?: builtins.int, "
        "'tag'?=: builtins.str, 'alias'?=: builtins.int})"
    )


def test_reflects_generic_typed_dict_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore

    class Payload(ta.TypedDict, ta.Generic[t_var]):  # type: ignore
        item: t_var  # type: ignore
        items: list[t_var]  # type: ignore

    typ = reflect_type(Payload[int])  # type: ignore

    assert isinstance(typ, types.TypedDictType)
    assert {name: type_str(item) for name, item in typ.items.items()} == {
        'item': 'builtins.int',
        'items': 'builtins.list[builtins.int]',
    }


def test_reflects_typed_dict_forward_refs_with_resolver() -> None:
    class Payload(ta.TypedDict):
        user: 'User'  # type: ignore  # noqa
        maybe_user: ta.NotRequired['User']  # type: ignore  # noqa

    reflector = make_reflector(
        forward_ref_resolver=lambda frr: {'User': int}[frr.name],
    )

    typ = reflector.reflect_type(Payload)

    assert isinstance(typ, types.TypedDictType)
    assert typ.required_keys == {'user'}
    assert {name: type_str(item) for name, item in typ.items.items()} == {
        'user': 'builtins.int',
        'maybe_user': 'builtins.int',
    }


def test_rejects_nested_required_typed_dict_item_wrapper() -> None:
    class Payload(ta.TypedDict):
        item: ta.Required[ta.NotRequired[int]]  # type: ignore

    with pytest.raises(UnreflectableTypeError, match='nested Required'):
        reflect_type(Payload)


def test_rejects_nested_read_only_typed_dict_item_wrapper() -> None:
    class Payload(ta.TypedDict):
        item: ta.ReadOnly[ta.ReadOnly[int]]  # type: ignore

    with pytest.raises(UnreflectableTypeError, match='nested ReadOnly'):
        reflect_type(Payload)


def test_rejects_required_typed_dict_item_wrapper_below_top_level() -> None:
    class Payload(ta.TypedDict):
        item: list[ta.Required[int]]  # type: ignore

    with pytest.raises(UnreflectableTypeError, match='nested TypedDict item wrapper'):
        reflect_type(Payload)


def test_rejects_read_only_typed_dict_item_wrapper_below_top_level() -> None:
    class Payload(ta.TypedDict):
        item: list[ta.ReadOnly[int]]  # type: ignore

    with pytest.raises(UnreflectableTypeError, match='nested TypedDict item wrapper'):
        reflect_type(Payload)


def test_rejects_bare_class_var_final_and_typed_dict_wrappers() -> None:
    with pytest.raises(UnreflectableTypeError):
        reflect_type(ta.ClassVar)

    with pytest.raises(UnreflectableTypeError):
        reflect_type(ta.Final)

    with pytest.raises(UnreflectableTypeError):
        reflect_type(ta.Required)

    with pytest.raises(UnreflectableTypeError):
        reflect_type(ta.NotRequired)

    with pytest.raises(UnreflectableTypeError):
        reflect_type(ta.ReadOnly)


def test_rejects_self_without_class_context() -> None:
    with pytest.raises(UnreflectableTypeError):
        reflect_type(ta.Self)


def test_reflects_optional_as_union_with_none() -> None:
    typ = reflect_type(ta.Optional[int])  # noqa

    assert isinstance(typ, types.UnionType)
    assert [type_str(item) for item in typ.items] == ['builtins.int', 'None']


def test_reflects_nested_unions_flattened_by_core_helper() -> None:
    typ = reflect_type(ta.Union[int, ta.Optional[str]])  # noqa

    assert isinstance(typ, types.UnionType)
    assert [type_str(item) for item in typ.items] == ['builtins.int', 'builtins.str', 'None']


def test_reflected_class_type_info_includes_runtime_generic_bases() -> None:
    reflector = make_reflector()
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    typ = reflector.reflect_type(IntBox)

    assert isinstance(typ, types.Instance)
    assert len(typ.type.bases) == 1
    base = typ.type.bases[0]
    assert isinstance(base, types.Instance)
    assert base.type is reflector.universe.get_type_info(Box)
    assert [type_str(arg) for arg in base.args] == ['builtins.int']
    assert typ.type.mro[:2] == (
        reflector.universe.get_type_info(IntBox),
        reflector.universe.get_type_info(Box),
    )


def test_reflected_class_generic_base_args_participate_in_subtyping() -> None:
    reflector = make_reflector()
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class IntBox(Box[int]):  # type: ignore
        pass

    child = reflector.reflect_type(IntBox)
    int_box = reflector.reflect_type(Box[int])  # type: ignore
    str_box = reflector.reflect_type(Box[str])  # type: ignore

    assert isinstance(child, types.Instance)
    assert isinstance(int_box, types.Instance)
    assert isinstance(str_box, types.Instance)
    assert is_subtype(child, int_box)
    assert not is_subtype(child, str_box)


def test_reflected_class_indirect_generic_base_args_participate_in_subtyping() -> None:
    reflector = make_reflector()
    t_var = ta.TypeVar('T')  # type: ignore

    class Box(ta.Generic[t_var]):  # type: ignore
        pass

    class Middle(Box[t_var]):  # type: ignore
        pass

    class Child(Middle[t_var]):  # type: ignore
        pass

    child = reflector.reflect_type(Child[int])  # type: ignore
    int_box = reflector.reflect_type(Box[int])  # type: ignore
    str_box = reflector.reflect_type(Box[str])  # type: ignore

    assert isinstance(child, types.Instance)
    assert isinstance(int_box, types.Instance)
    assert isinstance(str_box, types.Instance)
    assert is_subtype(child, int_box)
    assert not is_subtype(child, str_box)


def test_reflected_class_generic_mro_remaps_type_vars_at_each_layer() -> None:
    reflector = make_reflector(dynamic_type_name_suffix='counter')
    a_var = ta.TypeVar('A')  # type: ignore
    b_var = ta.TypeVar('B')  # type: ignore
    x_var = ta.TypeVar('X')  # type: ignore
    y_var = ta.TypeVar('Y')  # type: ignore

    class Base(ta.Generic[a_var, b_var]):  # type: ignore
        pass

    class Middle(ta.Generic[x_var], Base[list[x_var], str]):  # type: ignore
        pass

    class Child(ta.Generic[y_var], Middle[dict[str, y_var]]):  # type: ignore
        pass

    typ = reflector.reflect_type(Child[int])  # type: ignore

    assert isinstance(typ, types.Instance)
    mapped_mro = get_mro_instances(typ)

    assert [type_str(item) for item in mapped_mro] == [
        f'{Child.__module__}.{Child.__qualname__}@1[builtins.int]',
        f'{Middle.__module__}.{Middle.__qualname__}@2[builtins.dict[builtins.str, builtins.int]]',
        (
            f'{Base.__module__}.{Base.__qualname__}@3'
            '[builtins.list[builtins.dict[builtins.str, builtins.int]], builtins.str]'
        ),
        'typing.Generic',
        'builtins.object',
    ]


##
# Default (owner-scope) forward reference resolution.
#
# These exercise the `_forward_ref_resolver=None` default: a forward reference is resolved against the module (or class)
# scope in which the annotation carrying it was defined, leaning on stdlib `typing.evaluate_forward_ref`. The module-
# level fixtures below deliberately reference each other by string so the bounds / items are genuine forward references
# at reflection time.


class _CtxBound:
    pass


class _CtxItem:
    pass


_CtxBoundVar = ta.TypeVar('_CtxBoundVar', bound='_CtxBound')
_CtxNestedVar = ta.TypeVar('_CtxNestedVar', bound=list['_CtxBound'])


class _CtxBox(ta.Generic[_CtxBoundVar]):
    pass


class _CtxTypedDict(ta.TypedDict):
    item: '_CtxItem'  # noqa: UP037  # quoted to stay a genuine forward reference at reflection time


def test_default_resolution_resolves_type_var_bound_from_defining_module() -> None:
    reflector = make_reflector()

    typ = reflector.reflect_type(_CtxBoundVar)

    assert isinstance(typ, types.TypeVarType)
    assert isinstance(typ.upper_bound, types.Instance)
    assert reflector.universe.get_runtime_type(typ.upper_bound.type) is _CtxBound


def test_default_resolution_resolves_nested_forward_ref_inside_type_var_bound() -> None:
    reflector = make_reflector()

    typ = reflector.reflect_type(_CtxNestedVar)

    assert isinstance(typ, types.TypeVarType)
    assert isinstance(typ.upper_bound, types.Instance)
    assert typ.upper_bound.type.fullname == 'builtins.list'
    (arg,) = typ.upper_bound.args
    assert isinstance(arg, types.Instance)
    assert reflector.universe.get_runtime_type(arg.type) is _CtxBound


def test_default_resolution_resolves_generic_class_parameter_bound() -> None:
    reflector = make_reflector()

    typ = reflector.reflect_type(_CtxBox[int])  # type: ignore[type-var]

    assert isinstance(typ, types.Instance)
    (type_var,) = typ.type.type_vars
    assert isinstance(type_var, types.TypeVarType)
    assert isinstance(type_var.upper_bound, types.Instance)
    assert reflector.universe.get_runtime_type(type_var.upper_bound.type) is _CtxBound


def test_default_resolution_resolves_typed_dict_item_forward_ref() -> None:
    reflector = make_reflector()

    typ = reflector.reflect_type(_CtxTypedDict)

    assert isinstance(typ, types.TypedDictType)
    (item,) = typ.items.values()
    assert isinstance(item, types.Instance)
    assert reflector.universe.get_runtime_type(item.type) is _CtxItem


def test_default_resolution_without_owner_scope_still_rejects_bare_forward_ref() -> None:
    reflector = make_reflector(
        unresolved_forward_ref_policy='raise',
    )

    with pytest.raises(UnreflectableTypeError, match='forward reference'):
        reflector.reflect_type('_CtxBound')


def test_forward_ref_resolver_receives_full_resolution_context() -> None:
    captured: list[ForwardRefResolution] = []

    def resolver(frr):
        captured.append(frr)
        return int

    reflector = make_reflector(forward_ref_resolver=resolver)

    typ = reflector.reflect_type(_CtxBoundVar)

    assert isinstance(typ, types.TypeVarType)
    assert type_str(typ.upper_bound) == 'builtins.int'

    (frr,) = captured
    assert isinstance(frr, ForwardRefResolution)
    assert frr.name == '_CtxBound'
    assert isinstance(frr.obj, annotationlib.ForwardRef)
    assert frr.obj.__forward_arg__ == '_CtxBound'
    assert callable(frr.resolve)


def test_forward_ref_resolver_overrides_owner_scope_resolution() -> None:
    reflector = make_reflector(forward_ref_resolver=lambda frr: str)

    typ = reflector.reflect_type(_CtxBoundVar)

    assert isinstance(typ, types.TypeVarType)
    assert type_str(typ.upper_bound) == 'builtins.str'


def test_forward_ref_resolver_can_delegate_to_owner_scope_resolution() -> None:
    reflector = make_reflector(forward_ref_resolver=lambda frr: frr.resolve())

    typ = reflector.reflect_type(_CtxBoundVar)

    assert isinstance(typ, types.TypeVarType)
    assert isinstance(typ.upper_bound, types.Instance)
    assert reflector.universe.get_runtime_type(typ.upper_bound.type) is _CtxBound


def test_forward_ref_resolver_delegation_without_owner_scope_raises() -> None:
    reflector = make_reflector(
        forward_ref_resolver=lambda frr: frr.resolve(),
        unresolved_forward_ref_policy='raise',
    )

    with pytest.raises(UnreflectableTypeError, match='forward reference'):
        reflector.reflect_type('Missing')


##
# Cross-module / cache-safety of context-dependent forward reference resolution.


def _install_forward_ref_module(name: str, source: str) -> pytypes.ModuleType:
    module = pytypes.ModuleType(name)
    exec(source, module.__dict__)  # noqa: S102
    sys.modules[name] = module
    return module


def test_type_var_bound_resolves_in_type_var_module_not_using_class_module() -> None:
    module_name = f'{__name__}._synthetic_type_var_module'
    module = _install_forward_ref_module(
        module_name,
        'import typing as ta\n'
        'class Target: pass\n'
        "T = ta.TypeVar('T', bound='Target')\n",
    )
    try:
        type_var = module.T  # defined in `module`, whose scope alone contains `Target`

        class Using(ta.Generic[type_var]):  # type: ignore  # noqa
            pass

        reflector = make_reflector()

        typ = reflector.reflect_type(Using[int])  # type: ignore

        assert isinstance(typ, types.Instance)
        (reflected_var,) = typ.type.type_vars
        assert isinstance(reflected_var, types.TypeVarType)
        assert isinstance(reflected_var.upper_bound, types.Instance)
        assert reflector.universe.get_runtime_type(reflected_var.upper_bound.type) is module.Target
    finally:
        sys.modules.pop(module_name, None)


def test_same_named_forward_ref_bounds_in_distinct_modules_do_not_collide() -> None:
    name_a = f'{__name__}._synthetic_collision_module_a'
    name_b = f'{__name__}._synthetic_collision_module_b'
    source = (
        'import typing as ta\n'
        'class Foo: pass\n'
        "T = ta.TypeVar('T', bound='Foo')\n"
    )
    module_a = _install_forward_ref_module(name_a, source)
    module_b = _install_forward_ref_module(name_b, source)
    try:
        # The two `ForwardRef('Foo')` bounds compare equal and hash equal despite naming different classes.
        assert module_a.T.__bound__ == module_b.T.__bound__

        reflector = make_reflector()

        typ_a = reflector.reflect_type(module_a.T)
        typ_b = reflector.reflect_type(module_b.T)

        assert isinstance(typ_a, types.TypeVarType)
        assert isinstance(typ_b, types.TypeVarType)
        assert isinstance(typ_a.upper_bound, types.Instance)
        assert isinstance(typ_b.upper_bound, types.Instance)

        # Without the forward-ref cache guard the second reflection would collide with the first and return module_a's
        # `Foo`.
        assert reflector.universe.get_runtime_type(typ_a.upper_bound.type) is module_a.Foo
        assert reflector.universe.get_runtime_type(typ_b.upper_bound.type) is module_b.Foo
        assert typ_a.upper_bound.type is not typ_b.upper_bound.type
    finally:
        sys.modules.pop(name_a, None)
        sys.modules.pop(name_b, None)


def test_strict_policy_raises_on_unresolvable_forward_ref() -> None:
    with pytest.raises(UnreflectableTypeError, match='forward reference'):
        make_reflector(unresolved_forward_ref_policy='raise').reflect_type('Missing')


def test_rejects_unsupported_unresolved_forward_ref_policy_policy() -> None:
    with pytest.raises(ReflectionValueError):
        make_reflector(unresolved_forward_ref_policy='nonsense')


def test_unbound_policy_degrades_unresolvable_forward_ref_and_retains_identity() -> None:
    reflector = make_reflector(unresolved_forward_ref_policy='unbound')
    forward_ref = annotationlib.ForwardRef('Missing')

    typ = reflector.reflect_type(forward_ref)

    assert isinstance(typ, types.UnboundType)
    assert typ.name == 'Missing'
    assert typ.args == ()
    assert typ.runtime_object is forward_ref  # the *original* ForwardRef, for `is`-identity
    assert type_str(typ) == 'Missing?'


def test_unbound_policy_on_bare_string_retains_no_runtime_object() -> None:
    reflector = make_reflector(unresolved_forward_ref_policy='unbound')

    typ = reflector.reflect_type('Missing')

    assert isinstance(typ, types.UnboundType)
    assert typ.name == 'Missing'
    assert typ.runtime_object is None  # a bare str has no object identity to preserve


def test_unbound_policy_reflects_recursive_old_style_alias_to_finite_leaves() -> None:
    # Shaped like packaging's lite RequiresMarkerList: a recursive, unresolvable old-style alias (a bare typing form
    # whose self-referential forward refs carry no resolvable scope).
    alias = ta.Sequence[ta.Union['_Rec', int]]  # type: ignore[name-defined]  # noqa
    forward_ref = ta.get_args(ta.get_args(alias)[0])[0]

    reflector = make_reflector(unresolved_forward_ref_policy='unbound')

    typ = reflector.reflect_type(alias)

    assert isinstance(typ, types.Instance)
    assert typ.type.fullname == 'collections.abc.Sequence'
    (arg,) = typ.args
    assert isinstance(arg, types.UnionType)
    unbound = [item for item in arg.items if isinstance(item, types.UnboundType)]
    assert [u.name for u in unbound] == ['_Rec']
    assert unbound[0].runtime_object is forward_ref


def test_unbound_policy_still_prefers_resolution_when_available() -> None:
    # The policy governs only the terminal give-up; owner scope and resolvers still resolve first.
    reflector = make_reflector(
        unresolved_forward_ref_policy='unbound',
        forward_ref_resolver=lambda frr: {'Known': int}[frr.name],
    )

    typ = reflector.reflect_type('Known')

    assert isinstance(typ, types.Instance)
    assert type_str(typ) == 'builtins.int'


def test_unbound_policy_does_not_pollute_cache_across_owners() -> None:
    # The forward-ref cache guard still holds: a bare ForwardRef is never cached under its (ambiguous) key, so distinct
    # ForwardRef objects with the same name keep their own retained identity even in 'unbound' mode.
    reflector = make_reflector(unresolved_forward_ref_policy='unbound')
    left = annotationlib.ForwardRef('Same')
    right = annotationlib.ForwardRef('Same')

    left_type = reflector.reflect_type(left)
    right_type = reflector.reflect_type(right)

    assert isinstance(left_type, types.UnboundType)
    assert isinstance(right_type, types.UnboundType)
    assert left_type.runtime_object is left
    assert right_type.runtime_object is right


def test_unbound_type_key_preserves_forward_ref_identity_by_default() -> None:
    reflector = make_reflector(unresolved_forward_ref_policy='unbound')
    forward_ref = annotationlib.ForwardRef('Missing')

    typ = reflector.reflect_type(forward_ref)

    # Default policy folds the retained ForwardRef into the key as an opaque ref; the structural policy drops it to a
    # bare name.
    assert type_key(typ) == ("Unbound['Missing',$0]", forward_ref)
    assert type_key(typ, 'structural') == "Unbound['Missing']"
    assert tuple_type_key(typ) == ('unbound', 'Missing', forward_ref, ())
    assert tuple_type_key(typ, 'structural') == ('unbound', 'Missing', None, ())


def test_unbound_type_key_identity_folds_by_forward_ref_equality() -> None:
    # ForwardRef equality is name-based, so the key's identity fold distinguishes by name; the hard object handle for
    # true `is`-distinction is UnboundType.runtime_object (see above), not the key.
    reflector = make_reflector(unresolved_forward_ref_policy='unbound')

    same_a = reflector.reflect_type(annotationlib.ForwardRef('Same'))
    same_b = reflector.reflect_type(annotationlib.ForwardRef('Same'))
    other = reflector.reflect_type(annotationlib.ForwardRef('Other'))

    assert type_key(same_a) == type_key(same_b)
    assert type_key(same_a) != type_key(other)


def test_api_threads_unresolved_forward_ref_policy_policy_leaving_global_strict() -> None:
    tolerant = Api(unresolved_forward_ref_policy='unbound')

    typ = tolerant.reflect_type('Missing')
    assert isinstance(typ, types.UnboundType)
    assert typ.name == 'Missing'

    with pytest.raises(UnreflectableTypeError):
        make_reflector(unresolved_forward_ref_policy='raise').reflect_type('Missing')

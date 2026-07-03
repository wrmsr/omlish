# ruff: noqa: F821 PLC0132 SLF001
import collections.abc as cabc
import typing as ta

import pytest

from ..annotations import to_runtime_annotation
from ..core import symbols
from ..core import types
from ..errors import ReflectionError
from .helpers import make_mirror


def _to_annotation(obj: object) -> object:
    mirror = make_mirror()
    return to_runtime_annotation(
        mirror.reflect_type(obj),
    )


def test_to_runtime_annotation_returns_runtime_class_for_instance() -> None:
    assert _to_annotation(int) is int


def test_to_runtime_annotation_subscripts_generic_runtime_class() -> None:
    assert _to_annotation(list[str]) == list[str]
    assert _to_annotation(dict[str, int]) == dict[str, int]


def test_to_runtime_annotation_emits_none_and_any() -> None:
    assert _to_annotation(None) is None
    assert _to_annotation(ta.Any) is ta.Any


def test_to_runtime_annotation_emits_union() -> None:
    annotation = _to_annotation(int | str)

    assert ta.get_origin(annotation) is ta.Union
    assert ta.get_args(annotation) == (int, str)


def test_to_runtime_annotation_emits_literal_union_as_single_literal() -> None:
    annotation = _to_annotation(ta.Literal['a', 'b'])

    assert ta.get_origin(annotation) is ta.Literal
    assert ta.get_args(annotation) == ('a', 'b')


def test_to_runtime_annotation_emits_bytes_and_float_literal_unions() -> None:
    bytes_annotation = _to_annotation(ta.Literal[b'a', b'b'])
    float_annotation = _to_annotation(ta.Literal[1.5, 2.5])
    none_annotation = _to_annotation(ta.Literal[None])

    assert ta.get_origin(bytes_annotation) is ta.Literal
    assert ta.get_args(bytes_annotation) == (b'a', b'b')
    assert ta.get_origin(float_annotation) is ta.Literal
    assert ta.get_args(float_annotation) == (1.5, 2.5)
    assert ta.get_origin(none_annotation) is ta.Literal
    assert ta.get_args(none_annotation) == (None,)


def test_to_runtime_annotation_emits_mixed_literal_union() -> None:
    annotation = _to_annotation(ta.Literal['a'] | int)

    assert ta.get_origin(annotation) is ta.Union
    assert ta.get_args(annotation) == (ta.Literal['a'], int)


def test_to_runtime_annotation_emits_tuple_type() -> None:
    assert _to_annotation(tuple[int, str]) == tuple[int, str]


def test_to_runtime_annotation_emits_tuple_unpack_of_type_var_tuple() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    annotation = _to_annotation(tuple[ta.Unpack[ts_var]])  # type: ignore  # noqa

    assert annotation == tuple[ta.Unpack[ts_var]]  # type: ignore  # noqa
    assert ta.get_args(annotation) == (ta.Unpack[ts_var],)  # noqa


def test_to_runtime_annotation_emits_tuple_with_prefix_and_type_var_tuple_unpack() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    annotation = _to_annotation(tuple[int, ta.Unpack[ts_var], bytes])  # type: ignore  # noqa

    assert annotation == tuple[int, ta.Unpack[ts_var], bytes]  # type: ignore  # noqa
    assert ta.get_args(annotation) == (int, ta.Unpack[ts_var], bytes)  # noqa


def test_to_runtime_annotation_emits_tuple_unpack_of_concrete_tuple() -> None:
    annotation = _to_annotation(tuple[ta.Unpack[tuple[int, str]]])  # noqa

    assert annotation == tuple[ta.Unpack[tuple[int, str]]]  # noqa
    assert ta.get_args(annotation) == (ta.Unpack[tuple[int, str]],)  # noqa


def test_to_runtime_annotation_emits_type_type() -> None:
    assert _to_annotation(type[int]) == type[int]


def test_to_runtime_annotation_emits_callable_type() -> None:
    annotation = _to_annotation(cabc.Callable[[int, str], bool])

    assert ta.get_origin(annotation) is cabc.Callable
    assert ta.get_args(annotation) == ([int, str], bool)


def test_to_runtime_annotation_emits_callable_with_param_spec() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    annotation = _to_annotation(cabc.Callable[param_spec, int])

    assert ta.get_origin(annotation) is cabc.Callable
    assert ta.get_args(annotation) == (param_spec, int)


def test_to_runtime_annotation_emits_callable_with_equivalent_param_spec_nodes() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    mirror = make_mirror()
    reflected = mirror.reflect_type(param_spec)

    assert isinstance(reflected, types.ParamSpecType)
    same_reflected = types.ParamSpecType(
        reflected._name,
        reflected._fullname,
        types.TypeVarId(reflected._id._raw_id, reflected._id._meta_level, reflected._id._namespace),
        reflected._upper_bound,
        reflected._default,
    )
    callable_type = types.CallableType(
        [reflected, same_reflected],
        [symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        [None, None],
        mirror.reflect_type(int),
        types.Instance(
            mirror.get_type_info(cabc.Callable),  # type: ignore
            [types.AnyType(types.TypeOfAny.FROM_OMITTED_GENERICS)],
        ),
        variables=[reflected],
    )

    annotation = to_runtime_annotation(callable_type)

    assert ta.get_origin(annotation) is cabc.Callable
    assert ta.get_args(annotation) == (param_spec, int)


def test_to_runtime_annotation_emits_callable_with_concatenate() -> None:
    param_spec = ta.ParamSpec('P')  # type: ignore
    annotation = _to_annotation(cabc.Callable[ta.Concatenate[int, str, param_spec], bool])
    arg_spec, ret = ta.get_args(annotation)

    assert ta.get_origin(annotation) is cabc.Callable
    assert ret is bool
    assert ta.get_origin(arg_spec) is ta.Concatenate
    assert ta.get_args(arg_spec) == (int, str, param_spec)


def test_to_runtime_annotation_fails_closed_for_keyword_only_callable_shape() -> None:
    mirror = make_mirror()
    callable_type = types.CallableType(
        [mirror.reflect_type(int)],
        [symbols.ArgKind.NAMED],
        ['value'],
        mirror.reflect_type(str),
        types.Instance(
            mirror.get_type_info(cabc.Callable),  # type: ignore
            [types.AnyType(types.TypeOfAny.FROM_OMITTED_GENERICS)],
        ),
    )

    with pytest.raises(ReflectionError, match='parameter shape'):
        to_runtime_annotation(callable_type)


def test_to_runtime_annotation_fails_closed_for_mismatched_param_spec_nodes() -> None:
    mirror = make_mirror()
    left = mirror.reflect_type(ta.ParamSpec('P'))
    right = mirror.reflect_type(ta.ParamSpec('Q'))

    assert isinstance(left, types.ParamSpecType)
    assert isinstance(right, types.ParamSpecType)
    callable_type = types.CallableType(
        [left, right],
        [symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        [None, None],
        mirror.reflect_type(int),
        types.Instance(
            mirror.get_type_info(cabc.Callable),  # type: ignore
            [types.AnyType(types.TypeOfAny.FROM_OMITTED_GENERICS)],
        ),
        variables=[left, right],
    )

    with pytest.raises(ReflectionError, match='parameter shape'):
        to_runtime_annotation(callable_type)


def test_to_runtime_annotation_preserves_annotated_metadata() -> None:
    metadata = object()
    annotation = _to_annotation(ta.Annotated[int, 'cfg', metadata])

    assert ta.get_origin(annotation) is ta.Annotated
    assert ta.get_args(annotation) == (int, 'cfg', metadata)


def test_to_runtime_annotation_preserves_newtype_identity() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore

    assert _to_annotation(user_id) is user_id


def test_to_runtime_annotation_preserves_literal_newtype_identity() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    assert _to_annotation(mode) is mode


def test_to_runtime_annotation_expands_newtype_literal_alias() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    assert _to_annotation(mode_list) == list[mode]  # noqa


def test_to_runtime_annotation_can_preserve_newtype_literal_alias() -> None:
    mirror = make_mirror()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    typ = mirror.reflect_type(mode_list)

    assert to_runtime_annotation(typ) == list[mode]  # noqa
    assert to_runtime_annotation(typ, type_alias_policy='preserve') is mode_list


def test_to_runtime_annotation_expands_generic_newtype_literal_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    box_alias = ta.TypeAliasType('BoxAlias', list[t_var], type_params=(t_var,))  # type: ignore

    assert _to_annotation(box_alias[mode]) == list[mode]  # noqa


def test_to_runtime_annotation_can_preserve_generic_newtype_literal_alias() -> None:
    mirror = make_mirror()
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore  # noqa
    box_alias = ta.TypeAliasType('BoxAlias', list[t_var], type_params=(t_var,))  # type: ignore
    form = box_alias[mode]  # noqa

    typ = mirror.reflect_type(form)

    assert to_runtime_annotation(typ) == list[mode]  # noqa
    assert to_runtime_annotation(typ, type_alias_policy='preserve') == form


def test_to_runtime_annotation_expands_unsubscripted_variadic_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore

    annotation = _to_annotation(alias)

    assert annotation == tuple[ta.Unpack[ts_var]]  # type: ignore  # noqa
    assert ta.get_args(annotation) == (ta.Unpack[ts_var],)  # noqa


def test_to_runtime_annotation_can_preserve_unsubscripted_variadic_alias() -> None:
    mirror = make_mirror()
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    typ = mirror.reflect_type(alias)

    assert to_runtime_annotation(typ, type_alias_policy='preserve') is alias


def test_to_runtime_annotation_expands_subscripted_variadic_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore

    assert _to_annotation(alias[int, str]) == tuple[int, str]  # noqa


def test_to_runtime_annotation_can_preserve_subscripted_variadic_alias() -> None:
    mirror = make_mirror()
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    form = alias[int, str]  # noqa
    typ = mirror.reflect_type(form)

    assert to_runtime_annotation(typ, type_alias_policy='preserve') == form


def test_to_runtime_annotation_can_preserve_subscripted_variadic_alias_with_fixed_edges() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    u_var = ta.TypeVar('U')  # type: ignore
    alias_value = tuple[t_var, *ts_var, u_var]  # type: ignore[valid-type]
    alias = ta.TypeAliasType(
        'alias',
        alias_value,
        type_params=(t_var, ts_var, u_var),  # type: ignore[type-var]
    )
    form = alias[int, str, bool, bytes]  # type: ignore[type-arg]  # noqa
    mirror = make_mirror()
    typ = mirror.reflect_type(form)

    assert to_runtime_annotation(typ) == tuple[int, str, bool, bytes]
    assert to_runtime_annotation(typ, type_alias_policy='preserve') == form


def test_to_runtime_annotation_preserves_recursive_alias_when_expand_policy_is_requested() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    mirror = make_mirror(
        forward_ref_resolver=lambda frr: {'Node': alias}[frr.name],
    )
    typ = mirror.reflect_type(alias)

    assert to_runtime_annotation(typ) is alias
    assert to_runtime_annotation(typ, type_alias_policy='preserve') is alias


def test_to_runtime_annotation_preserves_variadic_recursive_alias_when_expand_policy_is_requested() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    form = alias[int, str]  # noqa
    mirror = make_mirror(
        forward_ref_resolver=lambda frr: {'TupleNode': alias}[frr.name],
    )
    typ = mirror.reflect_type(form)

    assert to_runtime_annotation(typ) == form
    assert to_runtime_annotation(typ, type_alias_policy='preserve') == form


def test_to_runtime_annotation_preserves_generic_variadic_recursive_alias_with_type_var_tuple_arg() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    form = alias[ts_var]
    mirror = make_mirror(
        forward_ref_resolver=lambda frr: {'TupleNode': alias}[frr.name],
    )
    typ = mirror.reflect_type(form)

    assert to_runtime_annotation(typ) == form
    assert to_runtime_annotation(typ, type_alias_policy='preserve') == form


def test_to_runtime_annotation_fails_closed_for_malformed_preserved_variadic_alias_arg() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    mirror = make_mirror()
    reflected = mirror.reflect_type(alias)

    assert isinstance(reflected, types.TypeAliasType)
    malformed = types.TypeAliasType(reflected.alias, [mirror.reflect_type(int)])

    with pytest.raises(ReflectionError, match='type alias'):
        to_runtime_annotation(malformed, type_alias_policy='preserve')


def test_to_runtime_annotation_fails_closed_for_unknown_type_info() -> None:
    typ = types.Instance(types.TypeInfo('Missing', 'example.Missing'), [])

    with pytest.raises(ReflectionError, match='Runtime class is unavailable'):
        to_runtime_annotation(typ)


def test_to_runtime_annotation_fails_closed_for_unsupported_ir_nodes() -> None:
    mirror = make_mirror()
    fallback = types.Instance(
        mirror.get_type_info(cabc.Callable),  # type: ignore
        [types.AnyType(types.TypeOfAny.FROM_OMITTED_GENERICS)],
    )
    int_type = mirror.reflect_type(int)
    unsupported = [
        types.UnboundType('Missing'),
        types.CallableArgument(int_type, 'value'),
        types.TypeList([int_type]),
        types.Overloaded([types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback)]),
        types.TypedDictType({'x': int_type}, {'x'}, set(), mirror.reflect_type(dict[str, int])),  # type: ignore  # noqa
        types.RawExpressionType(1, 'builtins.int'),
        types.PartialType(None, None),
        types.EllipsisType(),
        types.PlaceholderType('Later', [int_type]),
    ]

    for typ in unsupported:
        with pytest.raises(ReflectionError, match='Runtime annotation is not implemented'):
            to_runtime_annotation(typ)


def test_to_runtime_annotation_fails_closed_for_unrepresentable_unpack_payload() -> None:
    mirror = make_mirror()
    typ = types.UnpackType(mirror.reflect_type(int))

    with pytest.raises(ReflectionError, match='unpack type'):
        to_runtime_annotation(typ)

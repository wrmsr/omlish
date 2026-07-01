# ruff: noqa: F821 PLC0132 SLF001
import collections.abc as cabc
import threading
import typing as ta

import pytest

from ..annotations import TypeAnnotations
from ..annotations import to_runtime_annotation
from ..core import symbols
from ..core import types
from ..errors import ReflectionError
from ..interning import Interner
from ..reflector import TypeReflector
from ..universe import TypeUniverse


def _make_annotations() -> TypeAnnotations:
    lock = threading.RLock()
    universe = TypeUniverse(
        dynamic_type_name_suffix='counter',
        lock=lock,
    )
    reflector = TypeReflector(
        universe=universe,
        interner=Interner(
            lock=lock,
        ),
        lock=lock,
    )
    annotations = TypeAnnotations(
        reflector=reflector,
        lock=lock,
    )
    return annotations


def _to_annotation(obj: object) -> object:
    annotations = _make_annotations()
    return annotations.to_runtime_annotation(annotations._reflector.reflect_type(obj))


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
    annotations = _make_annotations()
    param_spec = ta.ParamSpec('P')  # type: ignore
    reflected = annotations._reflector.reflect_type(param_spec)

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
        annotations._reflector.reflect_type(int),
        types.Instance(
            annotations._reflector.universe.get_type_info(cabc.Callable),  # type: ignore
            [types.AnyType(types.TypeOfAny.FROM_OMITTED_GENERICS)],
        ),
        variables=[reflected],
    )

    annotation = annotations.to_runtime_annotation(callable_type)

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
    annotations = _make_annotations()
    callable_type = types.CallableType(
        [annotations._reflector.reflect_type(int)],
        [symbols.ArgKind.NAMED],
        ['value'],
        annotations._reflector.reflect_type(str),
        types.Instance(
            annotations._reflector.universe.get_type_info(cabc.Callable),  # type: ignore
            [types.AnyType(types.TypeOfAny.FROM_OMITTED_GENERICS)],
        ),
    )

    with pytest.raises(ReflectionError, match='parameter shape'):
        annotations.to_runtime_annotation(callable_type)


def test_to_runtime_annotation_fails_closed_for_mismatched_param_spec_nodes() -> None:
    annotations = _make_annotations()
    left = annotations._reflector.reflect_type(ta.ParamSpec('P'))
    right = annotations._reflector.reflect_type(ta.ParamSpec('Q'))

    assert isinstance(left, types.ParamSpecType)
    assert isinstance(right, types.ParamSpecType)
    callable_type = types.CallableType(
        [left, right],
        [symbols.ArgKind.STAR, symbols.ArgKind.STAR2],
        [None, None],
        annotations._reflector.reflect_type(int),
        types.Instance(
            annotations._reflector.universe.get_type_info(cabc.Callable),  # type: ignore
            [types.AnyType(types.TypeOfAny.FROM_OMITTED_GENERICS)],
        ),
        variables=[left, right],
    )

    with pytest.raises(ReflectionError, match='parameter shape'):
        annotations.to_runtime_annotation(callable_type)


def test_reflector_runtime_annotation_cache_reuses_emitted_annotation() -> None:
    annotations = _make_annotations()
    typ = annotations._reflector.reflect_type(ta.Annotated[list[int], 'cfg'])

    assert annotations.to_runtime_annotation(typ) is annotations.to_runtime_annotation(typ)
    assert annotations.to_runtime_annotation(
        typ,
        type_alias_policy='preserve',
    ) is annotations.to_runtime_annotation(typ, type_alias_policy='preserve')


def test_reflector_runtime_annotation_cache_reuses_recursive_variadic_alias_annotations() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    form = alias[int, str]  # noqa
    annotations = TypeAnnotations(
        reflector=TypeReflector(
            universe=TypeUniverse(
                lock=(lock := threading.RLock()),
            ),
            interner=Interner(
                lock=lock,
            ),
            lock=lock,
        ),
        forward_ref_resolver={'TupleNode': alias}.__getitem__,
        lock=lock,
    )
    typ = annotations._reflector.reflect_type(form)

    assert annotations.to_runtime_annotation(typ) is annotations.to_runtime_annotation(typ)
    assert annotations.to_runtime_annotation(
        typ,
        type_alias_policy='preserve',
    ) is annotations.to_runtime_annotation(typ, type_alias_policy='preserve')


def test_reflector_runtime_annotation_cache_does_not_store_failures() -> None:
    annotations = _make_annotations()
    typ = types.PartialType(None, None)

    for _ in range(2):
        with pytest.raises(ReflectionError, match='Runtime annotation is not implemented'):
            annotations.to_runtime_annotation(typ)
        assert all(key[0] is not typ for key in annotations._annotation_cache)


def test_to_runtime_annotation_preserves_annotated_metadata() -> None:
    metadata = object()
    annotation = _to_annotation(ta.Annotated[int, 'cfg', metadata])

    assert ta.get_origin(annotation) is ta.Annotated
    assert ta.get_args(annotation) == (int, 'cfg', metadata)


def test_to_runtime_annotation_preserves_new_type_identity() -> None:
    user_id = ta.NewType('UserId', int)  # type: ignore

    assert _to_annotation(user_id) is user_id


def test_to_runtime_annotation_preserves_literal_new_type_identity() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore

    assert _to_annotation(mode) is mode


def test_to_runtime_annotation_expands_new_type_literal_alias() -> None:
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    assert _to_annotation(mode_list) == list[mode]  # noqa


def test_to_runtime_annotation_can_preserve_new_type_literal_alias() -> None:
    annotations = _make_annotations()
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    mode_list = ta.TypeAliasType('ModeList', list[mode])  # type: ignore

    typ = annotations._reflector.reflect_type(mode_list)

    assert annotations.to_runtime_annotation(typ) == list[mode]  # noqa
    assert annotations.to_runtime_annotation(typ, type_alias_policy='preserve') is mode_list


def test_to_runtime_annotation_expands_generic_new_type_literal_alias() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore
    box_alias = ta.TypeAliasType('BoxAlias', list[t_var], type_params=(t_var,))  # type: ignore

    assert _to_annotation(box_alias[mode]) == list[mode]  # noqa


def test_to_runtime_annotation_can_preserve_generic_new_type_literal_alias() -> None:
    annotations = _make_annotations()
    t_var = ta.TypeVar('T')  # type: ignore
    mode = ta.NewType('Mode', ta.Literal['a', 'b'])  # type: ignore  # noqa
    box_alias = ta.TypeAliasType('BoxAlias', list[t_var], type_params=(t_var,))  # type: ignore
    form = box_alias[mode]  # noqa

    typ = annotations._reflector.reflect_type(form)

    assert annotations.to_runtime_annotation(typ) == list[mode]  # noqa
    assert annotations.to_runtime_annotation(typ, type_alias_policy='preserve') == form


def test_to_runtime_annotation_expands_unsubscripted_variadic_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore

    annotation = _to_annotation(alias)

    assert annotation == tuple[ta.Unpack[ts_var]]  # type: ignore  # noqa
    assert ta.get_args(annotation) == (ta.Unpack[ts_var],)  # noqa


def test_to_runtime_annotation_can_preserve_unsubscripted_variadic_alias() -> None:
    annotations = _make_annotations()
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    typ = annotations._reflector.reflect_type(alias)

    assert annotations.to_runtime_annotation(typ, type_alias_policy='preserve') is alias


def test_to_runtime_annotation_expands_subscripted_variadic_alias() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore

    assert _to_annotation(alias[int, str]) == tuple[int, str]  # noqa


def test_to_runtime_annotation_can_preserve_subscripted_variadic_alias() -> None:
    annotations = _make_annotations()
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    form = alias[int, str]  # noqa
    typ = annotations._reflector.reflect_type(form)

    assert annotations.to_runtime_annotation(typ, type_alias_policy='preserve') == form


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
    annotations = _make_annotations()
    typ = annotations._reflector.reflect_type(form)

    assert annotations.to_runtime_annotation(typ) == tuple[int, str, bool, bytes]
    assert annotations.to_runtime_annotation(typ, type_alias_policy='preserve') == form


def test_to_runtime_annotation_preserves_recursive_alias_when_expand_policy_is_requested() -> None:
    alias = ta.TypeAliasType('Node', int | list['Node'])  # type: ignore
    annotations = TypeAnnotations(
        reflector=TypeReflector(
            universe=TypeUniverse(
                lock=(lock := threading.RLock()),
            ),
            interner=Interner(
                lock=lock,
            ),
            lock=lock,
        ),
        forward_ref_resolver={'Node': alias}.__getitem__,
        lock=lock,
    )
    typ = annotations._reflector.reflect_type(alias)

    assert annotations.to_runtime_annotation(typ) is alias
    assert annotations.to_runtime_annotation(typ, type_alias_policy='preserve') is alias


def test_to_runtime_annotation_preserves_variadic_recursive_alias_when_expand_policy_is_requested() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    form = alias[int, str]  # noqa
    annotations = TypeAnnotations(
        reflector=TypeReflector(
            universe=TypeUniverse(
                lock=(lock := threading.RLock()),
            ),
            interner=Interner(
                lock=lock,
            ),
            lock=lock,
        ),
        forward_ref_resolver={'TupleNode': alias}.__getitem__,
        lock=lock,
    )
    typ = annotations._reflector.reflect_type(form)

    assert annotations.to_runtime_annotation(typ) == form
    assert annotations.to_runtime_annotation(typ, type_alias_policy='preserve') == form


def test_to_runtime_annotation_preserves_generic_variadic_recursive_alias_with_type_var_tuple_arg() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('TupleNode', tuple[*ts_var, 'TupleNode[*Ts]'], type_params=(ts_var,))  # type: ignore
    form = alias[ts_var]
    annotations = TypeAnnotations(
        reflector=TypeReflector(
            universe=TypeUniverse(
                lock=(lock := threading.RLock()),
            ),
            interner=Interner(
                lock=lock,
            ),
            lock=lock,
        ),
        forward_ref_resolver={'TupleNode': alias}.__getitem__,
        lock=lock,
    )
    typ = annotations._reflector.reflect_type(form)

    assert annotations.to_runtime_annotation(typ) == form
    assert annotations.to_runtime_annotation(typ, type_alias_policy='preserve') == form


def test_to_runtime_annotation_fails_closed_for_malformed_preserved_variadic_alias_arg() -> None:
    ts_var = ta.TypeVarTuple('Ts')  # type: ignore
    alias = ta.TypeAliasType('Alias', tuple[*ts_var], type_params=(ts_var,))  # type: ignore
    annotations = _make_annotations()
    reflected = annotations._reflector.reflect_type(alias)

    assert isinstance(reflected, types.TypeAliasType)
    malformed = types.TypeAliasType(reflected.alias, [annotations._reflector.reflect_type(int)])

    with pytest.raises(ReflectionError, match='type alias'):
        annotations.to_runtime_annotation(malformed, type_alias_policy='preserve')


def test_to_runtime_annotation_fails_closed_for_type_var() -> None:
    t_var = ta.TypeVar('T')  # type: ignore
    annotations = _make_annotations()

    with pytest.raises(ReflectionError, match='type variable'):
        to_runtime_annotation(annotations._reflector.reflect_type(t_var), annotations._reflector.universe)


def test_to_runtime_annotation_fails_closed_for_unknown_type_info() -> None:
    typ = types.Instance(types.TypeInfo('Missing', 'example.Missing'), [])

    with pytest.raises(ReflectionError, match='Runtime class is unavailable'):
        to_runtime_annotation(typ, TypeUniverse(lock=threading.RLock()))


def test_to_runtime_annotation_fails_closed_for_unsupported_ir_nodes() -> None:
    annotations = _make_annotations()
    fallback = types.Instance(
        annotations._reflector.universe.get_type_info(cabc.Callable),  # type: ignore
        [types.AnyType(types.TypeOfAny.FROM_OMITTED_GENERICS)],
    )
    int_type = annotations._reflector.reflect_type(int)
    unsupported = [
        types.UnboundType('Missing'),
        types.CallableArgument(int_type, 'value'),
        types.TypeList([int_type]),
        types.Overloaded([types.CallableType([int_type], [symbols.ArgKind.POS], [None], int_type, fallback)]),
        types.TypedDictType({'x': int_type}, {'x'}, set(), annotations._reflector.reflect_type(dict[str, int])),  # type: ignore  # noqa
        types.RawExpressionType(1, 'builtins.int'),
        types.PartialType(None, None),
        types.EllipsisType(),
        types.PlaceholderType('Later', [int_type]),
    ]

    for typ in unsupported:
        with pytest.raises(ReflectionError, match='Runtime annotation is not implemented'):
            annotations.to_runtime_annotation(typ)


def test_to_runtime_annotation_fails_closed_for_unrepresentable_unpack_payload() -> None:
    annotations = _make_annotations()
    typ = types.UnpackType(annotations._reflector.reflect_type(int))

    with pytest.raises(ReflectionError, match='unpack type'):
        annotations.to_runtime_annotation(typ)

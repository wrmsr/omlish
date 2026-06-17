# ruff: noqa: SLF001
import collections.abc as cabc
import enum
import typing as ta

from .core.symbols import ArgKind
from .core.symbols import TypeInfo
from .core.typeops import get_type_alias_target
from .core.types import AnnotatedType
from .core.types import AnyType
from .core.types import CallableType
from .core.types import Instance
from .core.types import LiteralType
from .core.types import NoneType
from .core.types import ParamSpecType
from .core.types import ReadOnlyType
from .core.types import RequiredType
from .core.types import TupleType
from .core.types import Type
from .core.types import TypeAliasType
from .core.types import TypeGuardedType
from .core.types import TypeType
from .core.types import TypeVarLikeType
from .core.types import TypeVarTupleType
from .core.types import UnionType
from .core.types import UnpackType
from .errors import ReflectionTypeError
from .errors import ReflectionValueError
from .universe import DEFAULT_UNIVERSE
from .universe import RuntimeTypeUniverse


TypeVarResolver: ta.TypeAlias = ta.Callable[[TypeVarLikeType], object | None]
TypeAliasAnnotationPolicy: ta.TypeAlias = ta.Literal['expand', 'preserve']


##


def _get_universe(universe: RuntimeTypeUniverse | None) -> RuntimeTypeUniverse:
    return DEFAULT_UNIVERSE if universe is None else universe


def _get_runtime_type(info: TypeInfo, universe: RuntimeTypeUniverse) -> object:
    cls = universe.get_runtime_type(info)
    if cls is None:
        raise ReflectionTypeError(f'Runtime class is unavailable for type info: {info._fullname}')
    return cls


def _to_instance_annotation(
        typ: Instance,
        universe: RuntimeTypeUniverse,
        type_var_resolver: TypeVarResolver | None,
        type_alias_policy: TypeAliasAnnotationPolicy,
) -> object:
    cls = _get_runtime_type(typ._type, universe)
    if not typ._args:
        return cls

    if not isinstance(cls, type):
        raise ReflectionTypeError(f'Runtime object is not subscriptable for type info: {typ._type._fullname}')

    args = tuple(to_runtime_annotation(
        arg,
        universe,
        type_var_resolver=type_var_resolver,
        type_alias_policy=type_alias_policy,
    ) for arg in typ._args)
    try:
        return cls[*args]  # type: ignore[index]
    except TypeError as e:
        raise ReflectionTypeError(f'Runtime class is not subscriptable for type info: {typ._type._fullname}') from e


def _to_union_annotation(
        typ: UnionType,
        universe: RuntimeTypeUniverse,
        type_var_resolver: TypeVarResolver | None,
        type_alias_policy: TypeAliasAnnotationPolicy,
) -> object:
    literal_values: list[object] = []
    for item in typ._items:
        if not isinstance(item, LiteralType):
            break
        literal_values.append(_to_literal_annotation_value(item, universe))
    else:
        return ta.Literal[*tuple(literal_values)]  # noqa

    return ta.Union[*tuple(  # noqa
        to_runtime_annotation(
            item,
            universe,
            type_var_resolver=type_var_resolver,
            type_alias_policy=type_alias_policy,
        )
        for item in typ._items
    )]


def _to_literal_annotation_value(typ: LiteralType, universe: RuntimeTypeUniverse) -> object:
    cls = universe.get_runtime_type(typ._fallback._type)
    if (
            isinstance(cls, type) and
            issubclass(cls, enum.Enum) and
            isinstance(typ._value, str)
    ):
        try:
            return cls[typ._value]
        except KeyError as e:
            raise ReflectionTypeError(f'Runtime enum member is unavailable for literal type: {typ!r}') from e

    return typ._value


def _to_tuple_annotation(
        typ: TupleType,
        universe: RuntimeTypeUniverse,
        type_var_resolver: TypeVarResolver | None,
        type_alias_policy: TypeAliasAnnotationPolicy,
) -> object:
    return tuple[*tuple(  # type: ignore[misc]
        to_runtime_annotation(
            item,
            universe,
            type_var_resolver=type_var_resolver,
            type_alias_policy=type_alias_policy,
        )
        for item in typ._items
    )]


def _to_unpack_annotation(
        typ: UnpackType,
        universe: RuntimeTypeUniverse,
        type_var_resolver: TypeVarResolver | None,
        type_alias_policy: TypeAliasAnnotationPolicy,
) -> object:
    item = typ._type
    if not isinstance(item, (TypeVarTupleType, TupleType)):
        raise ReflectionTypeError(f'Runtime annotation cannot represent unpack type: {typ!r}')

    return ta.Unpack[to_runtime_annotation(  # noqa
        item,
        universe,
        type_var_resolver=type_var_resolver,
        type_alias_policy=type_alias_policy,
    )]


def _to_type_var_annotation(
        typ: TypeVarLikeType,
        type_var_resolver: TypeVarResolver | None,
) -> object:
    if type_var_resolver is None:
        raise ReflectionTypeError(f'Runtime annotation is unavailable for type variable: {typ!r}')

    obj = type_var_resolver(typ)
    if obj is None:
        raise ReflectionTypeError(f'Runtime annotation is unavailable for type variable: {typ!r}')

    return obj


def _same_type_var_like_id(left: TypeVarLikeType, right: TypeVarLikeType) -> bool:
    return (
        left._id._namespace == right._id._namespace and
        left._id._raw_id == right._id._raw_id and
        left._id._meta_level == right._id._meta_level
    )


def _get_callable_param_spec_annotation(
        typ: CallableType,
        universe: RuntimeTypeUniverse,
        type_var_resolver: TypeVarResolver | None,
        type_alias_policy: TypeAliasAnnotationPolicy,
) -> object | None:
    if len(typ._arg_types) < 2:
        return None
    if typ._arg_kinds[-2:] != (ArgKind.STAR, ArgKind.STAR2):
        return None

    arg_type = typ._arg_types[-2]
    kw_arg_type = typ._arg_types[-1]
    if (
            not isinstance(arg_type, ParamSpecType)
            or not isinstance(kw_arg_type, ParamSpecType)
            or not _same_type_var_like_id(arg_type, kw_arg_type)
    ):
        return None

    param_spec = _to_type_var_annotation(arg_type, type_var_resolver)
    prefix_types = typ._arg_types[:-2]
    prefix_kinds = typ._arg_kinds[:-2]
    prefix_names = typ._arg_names[:-2]
    if not prefix_types:
        return param_spec

    if (
            prefix_kinds != tuple(ArgKind.POS for _ in prefix_types) or
            prefix_names != tuple(None for _ in prefix_types)
    ):
        raise ReflectionTypeError(f'Runtime Callable annotation cannot represent callable parameter shape: {typ!r}')

    return ta.Concatenate[
        *tuple(to_runtime_annotation(
            prefix,
            universe,
            type_var_resolver=type_var_resolver,
            type_alias_policy=type_alias_policy,
        ) for prefix in prefix_types),
        param_spec,
    ]


def _to_callable_annotation(
        typ: CallableType,
        universe: RuntimeTypeUniverse,
        type_var_resolver: TypeVarResolver | None,
        type_alias_policy: TypeAliasAnnotationPolicy,
) -> object:
    ret = to_runtime_annotation(
        typ._ret_type,
        universe,
        type_var_resolver=type_var_resolver,
        type_alias_policy=type_alias_policy,
    )
    if typ._is_ellipsis_args:
        return cabc.Callable[..., ret]

    if (param_spec := _get_callable_param_spec_annotation(
            typ,
            universe,
            type_var_resolver,
            type_alias_policy,
    )) is not None:
        return cabc.Callable[param_spec, ret]

    if (
            typ._arg_kinds != tuple(ArgKind.POS for _ in typ._arg_types) or
            typ._arg_names != tuple(None for _ in typ._arg_types)
    ):
        raise ReflectionTypeError(f'Runtime Callable annotation cannot represent callable parameter shape: {typ!r}')

    return cabc.Callable[
        [to_runtime_annotation(
            arg,
            universe,
            type_var_resolver=type_var_resolver,
            type_alias_policy=type_alias_policy,
        ) for arg in typ._arg_types],
        ret,
    ]


def _to_preserved_type_alias_annotation(
        typ: TypeAliasType,
        universe: RuntimeTypeUniverse,
        type_var_resolver: TypeVarResolver | None,
        type_alias_policy: TypeAliasAnnotationPolicy,
) -> object:
    if typ._alias is None:
        raise ReflectionTypeError(f'Runtime annotation is unavailable for unresolved type alias: {typ!r}')

    obj = typ._alias._runtime_object
    if obj is None:
        raise ReflectionTypeError(f'Runtime annotation is unavailable for type alias: {typ._alias._fullname}')
    if not typ._args:
        return obj

    args: list[object] = []
    if len(typ._args) != len(typ._alias._alias_tvars):
        raise ReflectionTypeError(f'Runtime annotation is unavailable for type alias: {typ._alias._fullname}')

    for arg, alias_tvar in zip(typ._args, typ._alias._alias_tvars):
        if isinstance(alias_tvar, TypeVarTupleType):
            if not isinstance(arg, TupleType):
                raise ReflectionTypeError(f'Runtime annotation is unavailable for type alias: {typ._alias._fullname}')

            args.extend(
                to_runtime_annotation(
                    item,
                    universe,
                    type_var_resolver=type_var_resolver,
                    type_alias_policy=type_alias_policy,
                )
                for item in arg._items
            )

        else:
            args.append(to_runtime_annotation(
                arg,
                universe,
                type_var_resolver=type_var_resolver,
                type_alias_policy=type_alias_policy,
            ))

    try:
        return obj[*tuple(args)]  # type: ignore[index]
    except TypeError as e:
        raise ReflectionTypeError(f'Runtime type alias is not subscriptable: {typ._alias._fullname}') from e


def to_runtime_annotation(
        typ: Type,
        universe: RuntimeTypeUniverse | None = None,
        *,
        type_var_resolver: TypeVarResolver | None = None,
        type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
) -> object:
    rt_universe = _get_universe(universe)

    if isinstance(typ, TypeAliasType):
        if typ._alias is None:
            raise ReflectionTypeError(f'Runtime annotation is unavailable for unresolved type alias: {typ!r}')
        if type_alias_policy == 'preserve' or typ.is_recursive:
            return _to_preserved_type_alias_annotation(
                typ,
                rt_universe,
                type_var_resolver,
                type_alias_policy,
            )
        if type_alias_policy != 'expand':
            raise ReflectionValueError(f'Unsupported type alias annotation policy: {type_alias_policy!r}')
        return to_runtime_annotation(
            get_type_alias_target(typ),
            rt_universe,
            type_var_resolver=type_var_resolver,
            type_alias_policy=type_alias_policy,
        )

    if isinstance(typ, TypeGuardedType):
        return to_runtime_annotation(
            typ._type_guard,
            rt_universe,
            type_var_resolver=type_var_resolver,
            type_alias_policy=type_alias_policy,
        )

    if isinstance(typ, AnnotatedType):
        return ta.Annotated[
            to_runtime_annotation(
                typ._item,
                rt_universe,
                type_var_resolver=type_var_resolver,
                type_alias_policy=type_alias_policy,
            ),
            *typ._metadata,
        ]

    if isinstance(typ, RequiredType):
        item = to_runtime_annotation(
            typ._item,
            rt_universe,
            type_var_resolver=type_var_resolver,
            type_alias_policy=type_alias_policy,
        )
        if typ._required:
            return ta.Required[item]  # noqa
        return ta.NotRequired[item]  # noqa

    if isinstance(typ, ReadOnlyType):
        return ta.ReadOnly[to_runtime_annotation(  # noqa
            typ._item,
            rt_universe,
            type_var_resolver=type_var_resolver,
            type_alias_policy=type_alias_policy,
        )]

    if isinstance(typ, TypeVarLikeType):
        return _to_type_var_annotation(typ, type_var_resolver)

    if isinstance(typ, AnyType):
        return ta.Any

    if isinstance(typ, NoneType):
        return None

    if isinstance(typ, Instance):
        return _to_instance_annotation(typ, rt_universe, type_var_resolver, type_alias_policy)

    if isinstance(typ, CallableType):
        return _to_callable_annotation(typ, rt_universe, type_var_resolver, type_alias_policy)

    if isinstance(typ, TupleType):
        return _to_tuple_annotation(typ, rt_universe, type_var_resolver, type_alias_policy)

    if isinstance(typ, UnpackType):
        return _to_unpack_annotation(typ, rt_universe, type_var_resolver, type_alias_policy)

    if isinstance(typ, LiteralType):
        return ta.Literal[_to_literal_annotation_value(typ, rt_universe)]  # noqa

    if isinstance(typ, UnionType):
        return _to_union_annotation(typ, rt_universe, type_var_resolver, type_alias_policy)

    if isinstance(typ, TypeType):
        return type[to_runtime_annotation(
            typ._item,
            rt_universe,
            type_var_resolver=type_var_resolver,
            type_alias_policy=type_alias_policy,
        )]

    raise ReflectionTypeError(f'Runtime annotation is not implemented for type: {typ!r}')

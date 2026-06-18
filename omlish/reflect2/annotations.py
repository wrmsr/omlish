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
from .core.typevisitor import DefaultTypeVisitor
from .errors import ReflectionTypeError
from .errors import ReflectionValueError
from .locking import NeedsLock
from .reflector import NeedsReflector
from .universe import NeedsUniverse
from .universe import TypeUniverse


TypeVarResolver: ta.TypeAlias = ta.Callable[[TypeVarLikeType], object | None]
TypeAliasAnnotationPolicy: ta.TypeAlias = ta.Literal['expand', 'preserve']


##


class _AnnotationMaker(
    DefaultTypeVisitor[object],
    NeedsUniverse,
):
    def __init__(
            self,
            *,
            type_var_resolver: TypeVarResolver | None = None,
            type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
            **kwargs: ta.Any,
    ) -> None:
        super().__init__(**kwargs)

        self._type_var_resolver = type_var_resolver
        self._type_alias_policy = type_alias_policy

    def visit_type(self, typ: Type) -> object:
        raise ReflectionTypeError(f'Runtime annotation is not implemented for type: {typ!r}')

    def _get_runtime_type(self, info: TypeInfo) -> object:
        cls = self._universe.get_runtime_type(info)
        if cls is None:
            raise ReflectionTypeError(f'Runtime class is unavailable for type info: {info._fullname}')
        return cls

    def _to_type_var_annotation(self, typ: TypeVarLikeType) -> object:
        if self._type_var_resolver is None:
            raise ReflectionTypeError(f'Runtime annotation is unavailable for type variable: {typ!r}')

        obj = self._type_var_resolver(typ)
        if obj is None:
            raise ReflectionTypeError(f'Runtime annotation is unavailable for type variable: {typ!r}')

        return obj

    def _same_type_var_like_id(self, left: TypeVarLikeType, right: TypeVarLikeType) -> bool:
        return (
            left._id._namespace == right._id._namespace and
            left._id._raw_id == right._id._raw_id and
            left._id._meta_level == right._id._meta_level
        )

    def _get_callable_param_spec_annotation(self, typ: CallableType) -> object | None:
        if len(typ._arg_types) < 2:
            return None
        if typ._arg_kinds[-2:] != (ArgKind.STAR, ArgKind.STAR2):
            return None

        arg_type = typ._arg_types[-2]
        kw_arg_type = typ._arg_types[-1]
        if (
                not isinstance(arg_type, ParamSpecType)
                or not isinstance(kw_arg_type, ParamSpecType)
                or not self._same_type_var_like_id(arg_type, kw_arg_type)
        ):
            return None

        param_spec = self._to_type_var_annotation(arg_type)
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
            *tuple(prefix.accept(self) for prefix in prefix_types),
            param_spec,
        ]

    def _to_preserved_type_alias_annotation(self, typ: TypeAliasType) -> object:
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
                    raise ReflectionTypeError(
                        f'Runtime annotation is unavailable for type alias: {typ._alias._fullname}',
                    )

                args.extend(
                    item.accept(self)
                    for item in arg._items
                )

            else:
                args.append(arg.accept(self))

        try:
            return obj[*tuple(args)]  # type: ignore[index]
        except TypeError as e:
            raise ReflectionTypeError(f'Runtime type alias is not subscriptable: {typ._alias._fullname}') from e

    def visit_type_alias_type(self, typ: TypeAliasType) -> object:
        if typ._alias is None:
            raise ReflectionTypeError(f'Runtime annotation is unavailable for unresolved type alias: {typ!r}')
        if self._type_alias_policy == 'preserve' or typ.is_recursive:
            return self._to_preserved_type_alias_annotation(typ)
        if self._type_alias_policy != 'expand':
            raise ReflectionValueError(f'Unsupported type alias annotation policy: {self._type_alias_policy!r}')
        return get_type_alias_target(typ).accept(self)

    def visit_type_guarded_type(self, typ: TypeGuardedType) -> object:
        return typ._type_guard.accept(self)

    def visit_annotated_type(self, typ: AnnotatedType) -> object:
        return ta.Annotated[
            typ._item.accept(self),
            *typ._metadata,
        ]

    def visit_required_type(self, typ: RequiredType) -> object:
        item = typ._item.accept(self)
        if typ._required:
            return ta.Required[item]  # noqa
        return ta.NotRequired[item]  # noqa

    def visit_read_only_type(self, typ: ReadOnlyType) -> object:
        return ta.ReadOnly[typ._item.accept(self)]  # noqa

    def visit_type_var_like_type(self, typ: TypeVarLikeType) -> object:
        return self._to_type_var_annotation(typ)

    def visit_unpack_type(self, typ: UnpackType) -> object:
        item = typ._type
        if not isinstance(item, (TypeVarTupleType, TupleType)):
            raise ReflectionTypeError(f'Runtime annotation cannot represent unpack type: {typ!r}')

        return ta.Unpack[item.accept(self)]  # noqa

    def visit_any(self, typ: AnyType) -> object:
        return ta.Any

    def visit_none_type(self, typ: NoneType) -> object:
        return None

    def visit_instance(self, typ: Instance) -> object:
        cls = self._get_runtime_type(typ._type)
        if not typ._args:
            return cls

        if not isinstance(cls, type):
            raise ReflectionTypeError(f'Runtime object is not subscriptable for type info: {typ._type._fullname}')

        args = tuple(arg.accept(self) for arg in typ._args)
        try:
            return cls[*args]  # type: ignore[index]
        except TypeError as e:
            raise ReflectionTypeError(f'Runtime class is not subscriptable for type info: {typ._type._fullname}') from e

    def visit_callable_type(self, typ: CallableType) -> object:
        ret = typ._ret_type.accept(self)
        if typ._is_ellipsis_args:
            return cabc.Callable[..., ret]

        if (param_spec := self._get_callable_param_spec_annotation(typ)) is not None:
            return cabc.Callable[param_spec, ret]

        if (
                typ._arg_kinds != tuple(ArgKind.POS for _ in typ._arg_types) or
                typ._arg_names != tuple(None for _ in typ._arg_types)
        ):
            raise ReflectionTypeError(f'Runtime Callable annotation cannot represent callable parameter shape: {typ!r}')

        return cabc.Callable[
            [arg.accept(self) for arg in typ._arg_types],
            ret,
        ]

    def visit_tuple_type(self, typ: TupleType) -> object:
        return tuple[*tuple(  # type: ignore[misc]
            item.accept(self)
            for item in typ._items
        )]

    def _to_literal_annotation_value(self, typ: LiteralType) -> object:
        cls = self._universe.get_runtime_type(typ._fallback._type)
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

    def visit_literal_type(self, typ: LiteralType) -> object:
        return ta.Literal[self._to_literal_annotation_value(typ)]  # noqa

    def visit_union_type(self, typ: UnionType) -> object:
        literal_values: list[object] = []
        for item in typ._items:
            if not isinstance(item, LiteralType):
                break
            literal_values.append(self._to_literal_annotation_value(item))
        else:
            return ta.Literal[*tuple(literal_values)]  # noqa

        return ta.Union[*tuple(  # noqa
            item.accept(self)
            for item in typ._items
        )]

    def visit_type_type(self, typ: TypeType) -> object:
        return type[typ._item.accept(self)]


def to_runtime_annotation(
        typ: Type,
        universe: TypeUniverse | None = None,
        *,
        type_var_resolver: TypeVarResolver | None = None,
        type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
) -> object:
    return typ.accept(_AnnotationMaker(
        type_var_resolver=type_var_resolver,
        type_alias_policy=type_alias_policy,
        universe=universe,
    ))


##


@ta.final
class TypeAnnotations(
    NeedsReflector,
    NeedsLock,
):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(**kwargs)

        self._annotation_cache: dict[tuple[Type, TypeAliasAnnotationPolicy], object] = {}

    #

    def _to_runtime_annotation(
            self,
            typ: Type,
            *,
            type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
    ) -> object:
        cache_key = (typ, type_alias_policy)
        try:
            return self._annotation_cache[cache_key]
        except KeyError:
            pass

        annotation = to_runtime_annotation(
            typ,
            self._reflector._universe,
            type_var_resolver=self._reflector.get_runtime_type_param,
            type_alias_policy=type_alias_policy,
        )
        self._annotation_cache[cache_key] = annotation
        return annotation

    def to_runtime_annotation(
            self,
            typ: Type,
            *,
            type_alias_policy: TypeAliasAnnotationPolicy = 'expand',
    ) -> object:
        cache_key = (typ, type_alias_policy)
        try:
            return self._annotation_cache[cache_key]
        except KeyError:
            pass

        with self._lock:
            return self._to_runtime_annotation(
                typ,
                type_alias_policy=type_alias_policy,
            )

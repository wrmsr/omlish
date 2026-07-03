# ruff: noqa: I001
from .. import lang as _lang


with _lang.auto_proxy_init(globals()):
    #

    from .core.strconv import (  # noqa
        type_str,
        type_info_str,
    )

    from .core.symbols import (  # noqa
        VarianceKind,
        ArgKind,

        Symbol,
        TypeInfo,
        TypeAlias,
    )

    from .core.typekeys import (  # noqa
        TypeKey,
        TupleTypeKey,

        StandardTypeKeyPolicy,

        TypeKeyPolicy,

        TYPE_KEY,
        ALPHA_TYPE_KEY,
        STRUCTURAL_TYPE_KEY,
        ALPHA_STRUCTURAL_TYPE_KEY,

        get_type_key_policy,

        type_key_or_none,
        type_key,

        tuple_type_key_or_none,
        tuple_type_key,
    )

    from .core.typeops import (  # noqa
        RecursiveTypeError,
        get_type_alias_target,
        get_proper_type,
        get_proper_types,

        has_type_vars,

        get_literal_values,
        get_literal_values_or_none,

        collect_aliases,
        is_recursive_alias,

        make_union,
        make_simplified_union,
    )

    from .core.types import (  # noqa
        LiteralValue,
        is_literal_value,

        Type,
        TypeAliasType,
        TypeGuardedType,
        AnnotatedType,
        RequiredType,
        ReadOnlyType,
        ProperType,
        TypeVarId,
        TypeVarLikeType,
        TypeVarType,
        ParamSpecType,
        TypeVarTupleType,
        UnboundType,
        CallableArgument,
        TypeList,
        UnpackType,
        TypeOfAny,
        AnyType,
        any_type,
        UninhabitedType,
        uninhabited_type,
        NoneType,
        none_type,
        ErasedType,
        erased_type,
        DeletedType,
        ExtraAttrs,
        Instance,
        FunctionLike,
        FormalArgument,
        Parameters,
        CallableType,
        Overloaded,
        TupleType,
        TypedDictType,
        RawExpressionType,
        LiteralType,
        UnionType,
        PartialType,
        EllipsisType,
        ellipsis_type,
        TypeType,
        PlaceholderType,
    )

    from .annotations import (  # noqa
        TypeVarResolver,
        TypeAliasAnnotationPolicy,

        to_runtime_annotation as to_runtime_annotation_,
    )

    from .api import (  # noqa
        Api,

        global_api,
        or_global_api,

        get_type_info,
        get_newtype_info,
        get_runtime_type,

        reflect_type,

        to_runtime_annotation,

        inspect_members,

        inspect_dataclass,

        inspect_namedtuple,
    )

    from .errors import (  # noqa
        ReflectionError,
        ReflectionTypeError,
        ReflectionValueError,
        ReflectionRuntimeError,
        ReflectionInternalError,
        UnsupportedTypeOperationError,
        UnreflectableTypeError,
        ProtocolReflectionError,
    )

    from .ops import (  # noqa
        reflect_mro_entries,
        reflect_mro_entries_by_info,
    )

    from .reflector import (  # noqa
        UnresolvedForwardRefPolicy,

        ForwardRefResolution,
        ForwardRefResolver,

        TypeReflector,
    )

    from .universe import (  # noqa
        TypeUniverse,
    )

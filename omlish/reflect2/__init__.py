# ruff: noqa: I001
from .. import lang as _lang


with _lang.auto_proxy_init(globals()):
    #

    from .core.strconv import (  # noqa
        type_str,
        type_info_str,
    )

    from .core.substitute import (  # noqa
        SubstitutionKey,
        SubstitutionMap,
        SubstitutionInputMap,

        substitute_type,
        substitute_types,
    )

    from .core.subtypes import (  # noqa
        MroEntry,
        get_mro_entries,
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
        TypeAliasAnnotationPolicy,

        to_runtime_annotation,
    )

    from .dataclasses import (  # noqa
        DataclassField,
        DataclassInspection,

        DataclassInspector,
        inspect_dataclass,
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
        RecursiveTypeReflectionError,
    )

    from .globals import (  # noqa
        global_mirror,
        or_global_mirror,

        get_type_info,
        can_reflect_type,
        reflect_type,
    )

    from .internals import (  # noqa
        is_simple_generic_alias_type,

        get_orig_bases,
        get_orig_class,
    )

    from .members import (  # noqa
        MemberKind,
        MemberParameter,
        MemberSignature,
        Member,
        MembersInspection,

        MembersInspector,
        inspect_members,
    )

    from .mirror import (  # noqa
        UnresolvedForwardRefPolicy,

        ForwardRefResolution,
        ForwardRefResolver,

        Mirror,
    )

    from .namedtuples import (  # noqa
        NamedtupleField,
        NamedtupleInspection,

        NamedtupleInspector,
        inspect_namedtuple,
    )

    from .ops import (  # noqa
        typeof,

        get_runtime_object_or_none,
        get_runtime_object,
        get_runtime_type_or_none,
        get_runtime_type,

        is_optional,
        strip_optional,

        Mro,
        get_mro,
    )

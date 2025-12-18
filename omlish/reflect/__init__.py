from .. import lang as _lang


with _lang.auto_proxy_init(
        globals(),
        update_exports=True,
        # eager=True,
):
    ##

    from .inspect import (  # noqa
        has_annotations,

        get_annotations,

        get_filtered_type_hints,
    )

    from .ops import (  # noqa
        strip_objs,
        strip_annotations,

        types_equivalent,

        get_underlying,
        get_concrete_type,

        to_annotation,
    )

    from .subst import (  # noqa
        get_type_var_replacements,
        replace_type_vars,

        GenericSubstitution,
        DEFAULT_GENERIC_SUBSTITUTION,
        ALIAS_UPDATING_GENERIC_SUBSTITUTION,

        generic_mro,
        get_generic_bases,
    )

    from .types import (  # noqa
        is_simple_generic_alias_type,
        get_params,
        is_union_type,
        get_orig_bases,
        get_orig_class,
        get_newtype_supertype,
        get_type_var_bound,

        TypeInfo,
        Type,
        TYPES,

        Union,

        GenericLike,
        Generic,
        Protocol,

        NewType,

        Annotated,

        Literal,

        Any,
        ANY,

        ReflectTypeError,

        Reflector,
        DEFAULT_REFLECTOR,
        is_type,
        type_,
    )

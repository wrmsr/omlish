from .. import lang as _lang


with _lang.auto_proxy_init(
        globals(),
        update_exports=True,
        # eager=True,
):
    ##

    from .inspect import (  # noqa
        get_annotations,
        get_filtered_type_hints,
        has_annotations,
    )

    from .ops import (  # noqa
        get_concrete_type,
        get_underlying,
        strip_annotations,
        strip_objs,
        to_annotation,
        types_equivalent,
    )

    from .subst import (  # noqa
        ALIAS_UPDATING_GENERIC_SUBSTITUTION,
        DEFAULT_GENERIC_SUBSTITUTION,
        GenericSubstitution,
        generic_mro,
        get_generic_bases,
        get_type_var_replacements,
        replace_type_vars,
    )

    from .types import (  # noqa
        ANY,
        Annotated,
        Any,
        DEFAULT_REFLECTOR,
        Generic,
        GenericLike,
        Literal,
        NewType,
        Protocol,
        ReflectTypeError,
        Reflector,
        TYPES,
        Type,
        TypeInfo,
        Union,
        get_newtype_supertype,
        get_orig_bases,
        get_orig_class,
        get_params,
        get_type_var_bound,
        is_type,
        is_union_type,
        type_,
    )

from .. import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .accessor import (  # noqa
        TypedValuesAccessor,
    )

    from .collection import (  # noqa
        DuplicateUniqueTypedValueError,

        TypedValues,

        collect,
        as_collection,
    )

    from .consumer import (  # noqa
        UnconsumedTypedValuesError,

        TypedValuesConsumer,

        consume,
    )

    from .generic import (  # noqa
        TypedValueGeneric,
    )

    from .holder import (  # noqa
        TypedValueHolder,
    )

    from .of_ import (  # noqa
        of,
    )

    from .reflect import (  # noqa
        reflect_typed_values_impls,
    )

    from .values import (  # noqa
        TypedValue,

        UniqueTypedValue,

        ScalarTypedValue,

        UniqueScalarTypedValue,
    )


##


from .. import marshal as _msh


_msh.register_global_module_import('.marshal', __package__)

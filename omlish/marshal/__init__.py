# ruff: noqa: I001
from .. import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from .. import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()):
    ##

    from .api.configs import (  # noqa
        Config,
        ConfigValues,

        Configs,

        ConfigRegistrySealedError,
        ConfigRegistry,
    )

    from .api.contexts import (  # noqa
        BaseContext,

        MarshalFactoryContext,
        UnmarshalFactoryContext,

        MarshalContext,
        UnmarshalContext,
    )

    from .api.errors import (  # noqa
        ForbiddenError,
        ForbiddenTypeError,
        MarshalError,
        UnhandledTypeError,
    )

    from .api.funcs import (  # noqa
        FuncMarshaler,
        FuncUnmarshaler,

        FuncMarshalerFactory,
        FuncUnmarshalerFactory,
    )

    from .api.naming import (  # noqa
        Naming,
        translate_name,
    )

    from .api.options import (  # noqa
        Option,
    )

    from .api.reflect import (  # noqa
        ReflectOverride,
    )

    from .api.types import (  # noqa
        Marshaler,
        Unmarshaler,

        MarshalerMaker,
        UnmarshalerMaker,

        MarshalerFactory,
        UnmarshalerFactory,

        Marshaling,

        SimpleMarshaling,
    )

    from .api.values import (  # noqa
        Value,
    )

    from .composite.api import (  # noqa
        DefaultIterableConstructors,
        DefaultMappingConstructors,
    )

    from .composite.iterables import (  # noqa
        IterableMarshaler,
        IterableUnmarshaler,
    )

    from .composite.optionals import (  # noqa
        OptionalMarshaler,
        OptionalUnmarshaler,
    )

    from .composite.unions.literals import (  # noqa
        LITERAL_UNION_TYPES,
        LiteralUnionMarshaler,
        LiteralUnionMarshalerFactory,
        LiteralUnionUnmarshaler,
        LiteralUnionUnmarshalerFactory,
    )

    from .composite.unions.primitives import (  # noqa
        PRIMITIVE_UNION_TYPES,
        PrimitiveUnionMarshaler,
        PrimitiveUnionMarshalerFactory,
        PrimitiveUnionUnmarshaler,
        PrimitiveUnionUnmarshalerFactory,
    )

    from .composite.wrapped import (  # noqa
        WrappedMarshaler,
        WrappedUnmarshaler,
    )

    from .factories.method import (  # noqa
        MarshalerFactoryMethodClass,
        UnmarshalerFactoryMethodClass,
    )

    from .factories.api import (  # noqa
        LazyInitFn,
        LazyInit,

        ModuleImport,

        Override,
    )

    from .factories.lazyinit import (  # noqa
        LazyInitRunningMarshalerFactory,
        LazyInitRunningUnmarshalerFactory,
    )

    from .factories.multi import (  # noqa
        MultiMarshalerFactory,
        MultiUnmarshalerFactory,
    )

    from .factories.override import (  # noqa
        OverrideMarshalerFactory,
        OverrideUnmarshalerFactory,
    )

    from .factories.typemap import (  # noqa
        TypeMapMarshalerFactory,
        TypeMapUnmarshalerFactory,
    )

    from .factories.typecache import (  # noqa
        TypeCacheMarshalerFactory,
        TypeCacheUnmarshalerFactory,
    )

    from .factories.recursive import (  # noqa
        RecursiveMarshalerFactory,
        RecursiveUnmarshalerFactory,
    )

    from .objects.dataclasses import (  # noqa
        DataclassMarshalerFactory,
        DataclassUnmarshalerFactory,
        get_dataclass_field_infos,
        get_dataclass_options,
    )

    from .objects.api import (  # noqa
        FieldOptions,
        ObjectOptions,
        ObjectSpecials,
    )

    from .objects.helpers import (  # noqa
        update_fields_options,
        update_object_options,
        with_field_options,
    )

    from .objects.infos import (  # noqa
        FieldInfo,
        FieldInfos,
    )

    from .objects.marshal import (  # noqa
        ObjectMarshaler,
        SimpleObjectMarshalerFactory,
    )

    from .objects.unmarshal import (  # noqa
        ObjectUnmarshaler,
        SimpleObjectUnmarshalerFactory,
    )

    from .polymorphism.api import (  # noqa
        AutoStripSuffix,
        FieldTypeTagging,
        Impl,
        Impls,
        ImplBase,
        ImplBases,
        Polymorphism,
        TypeTagging,
        WrapperTypeTagging,
        polymorphism_from_impls,
        polymorphism_from_subclasses,
    )

    from .polymorphism.marshal import (  # noqa
        PolymorphismMarshaler,
        PolymorphismMarshalerFactory,
        make_polymorphism_marshaler,
    )

    from .polymorphism.standard import (  # noqa
        standard_polymorphism_factories,
    )

    from .polymorphism.unmarshal import (  # noqa
        PolymorphismUnmarshaler,
        PolymorphismUnmarshalerFactory,
        make_polymorphism_unmarshaler,
    )

    from .singular.base64 import (  # noqa
        BASE64_MARSHALER_FACTORY,
        BASE64_UNMARSHALER_FACTORY,
        Base64MarshalerUnmarshaler,
    )

    from .singular.primitives import (  # noqa
        PRIMITIVE_TYPES,
    )

    from .standard.api import (  # noqa
        StandardMarshalerFactories,
        StandardUnmarshalerFactories,
    )

    from .standard.defaults import (  # noqa
        DEFAULT_STANDARD_FACTORIES,
    )

    from .standard.factories import (  # noqa
        StandardMarshalerFactory,
        StandardUnmarshalerFactory,

        new_standard_marshaler_factory,
        new_standard_unmarshaler_factory,
    )

    from .trivial.forbidden import (  # noqa
        ForbiddenMarshalerUnmarshaler,

        ForbiddenTypeMarshalerFactory,
        ForbiddenTypeMarshalerFactoryUnmarshalerFactory,
        ForbiddenTypeUnmarshalerFactory,
    )

    from .trivial.nop import (  # noqa
        NOP_MARSHALER_UNMARSHALER,
        NopMarshalerUnmarshaler,
    )

    from .typedvalues.collections import (  # noqa
        build_typed_values_marshaler,
        build_typed_values_unmarshaler,
    )

    from .globals import (  # noqa
        global_config_registry,
        global_marshaler_factory,
        global_unmarshaler_factory,
        global_marshaling,

        marshal,
        unmarshal,

        register_global_config,
        register_global_lazy_init,
        register_global_module_import,

        install_standard_factories,
        install_standard_factories_to,
    )

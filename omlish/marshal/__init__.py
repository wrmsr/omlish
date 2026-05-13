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
        Options,

        DefaultOptions,
        IgnoreDefaultOptions,

        update_default_options,
        build_effective_options,
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

        VALUE_TYPES,
    )

    from .api.vias import (  # noqa
        MarshalVia,
        UnmarshalVia,

        make_marshaler_via,
        make_unmarshaler_via,

        set_marshal_via,
        set_unmarshal_via,
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
    )

    from .factories.filtered import (  # noqa
        FilteredMarshalerFactory,
        FilteredUnmarshalerFactory,
    )

    from .factories.lazy import (  # noqa
        LazyMarshalerFactory,
        LazyUnmarshalerFactory,
    )

    from .factories.lazyinit import (  # noqa
        LazyInitRunningMarshalerFactory,
        LazyInitRunningUnmarshalerFactory,
    )

    from .factories.multi import (  # noqa
        MultiMarshalerFactory,
        MultiUnmarshalerFactory,
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

    from .factories.vias import (  # noqa
        ViaConfigMarshalerFactory,
        ViaConfigUnmarshalerFactory,

        ViaMetadataMarshalerFactory,
        ViaMetadataUnmarshalerFactory,
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
        update_field_options,
        update_object_options,
        dc_field_options,
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
        PolymorphismTagError,
        PolymorphismImplError,

        AUTO_STRIP_SUFFIX,

        TypeTagging,
        WrapperTypeTagging,
        FieldTypeTagging,

        Impl,
        Impls,
        ImplBase,
        ImplBases,
        Polymorphism,

        polymorphism_from_impls,
        polymorphism_from_subclasses,

        PolymorphismOptions,
        OpenPolymorphismImpl,

        set_polymorphic_from_subclasses,
    )

    from .polymorphism.marshal import (  # noqa
        PolymorphismMarshaler,
        PolymorphismMarshalerFactory,
        make_polymorphism_marshaler,
    )

    from .polymorphism.metadata import (  # noqa
        PolymorphismMetadataCache,

        PolymorphismMetadataMarshalerFactory,
        PolymorphismMetadataUnmarshalerFactory,

        make_polymorphism_metadata_factories,
    )

    from .polymorphism.open import (  # noqa
        OpenPolymorphismMarshalerFactory,
        OpenPolymorphismUnmarshalerFactory,
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
        Base64MarshalerUnmarshaler,

        BASE64_MARSHALER_FACTORY,
        BASE64_UNMARSHALER_FACTORY,
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

    from .trivial.any import (  # noqa
        AnyMarshalerUnmarshaler,

        ANY_MARSHALER_UNMARSHALER,
        ANY_MARSHALER_FACTORY,
        ANY_UNMARSHALER_FACTORY,
    )

    from .trivial.const import (  # noqa
        ConstMarshaler,
        ConstUnmarshaler,
    )

    from .trivial.forbidden import (  # noqa
        ForbiddenMarshalerUnmarshaler,

        ForbiddenTypeMarshalerFactory,
        ForbiddenTypeMarshalerFactoryUnmarshalerFactory,
        ForbiddenTypeUnmarshalerFactory,
    )

    from .trivial.nop import (  # noqa
        NopMarshalerUnmarshaler,

        NOP_MARSHALER_UNMARSHALER,
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

        update_global_config,
        register_global_lazy_init,
        register_global_module_import,

        install_standard_factories,
        install_standard_factories_to,
    )

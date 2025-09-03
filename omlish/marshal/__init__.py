# ruff: noqa: I001
"""
TODO:
 - redacted
 - strongly typed MarshalerFactory base class?
 - strongly typed Composite/Cached Marshaler/Unmarshaler factories - footgun
 - streaming? Start/EndObject, etc..
 - lang.Marker - class name, handle type[Foo]
  - can't disambiguate from str - can't coexist in bare union
 - factories being free MatchFns does more harm than good - in practice these are such big guns you want to write a
   class body if only ceremonially
 - simple lite interop like inj - alt ObjMarshalerManager impl for Context

See:
 - https://github.com/python-attrs/cattrs
 - https://github.com/jcrist/msgspec
 - https://github.com/Fatal1ty/mashumaro
 - https://github.com/Kotlin/kotlinx.serialization/blob/master/docs/serializers.md#custom-serializers
"""
from .. import dataclasses as _dc  # noqa


_dc.init_package(
    globals(),
    codegen=True,
)


##


from .. import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()) as _api_cap:
    ##

    from .base.configs import (  # noqa
        Config,
        ConfigRegistry,
    )

    from .base.contexts import (  # noqa
        BaseContext,
        MarshalContext,
        UnmarshalContext,
    )

    from .base.errors import (  # noqa
        ForbiddenTypeError,
        MarshalError,
        UnhandledTypeError,
    )

    from .base.funcs import (  # noqa
        FuncMarshaler,
        FuncUnmarshaler,

        FuncMarshalerFactory,
        FuncUnmarshalerFactory,
    )

    from .base.options import (  # noqa
        Option,
    )

    from .base.overrides import (  # noqa
        Override,
        ReflectOverride,
    )

    from .base.registries import (  # noqa
        RegistrySealedError,
        Registry,
    )

    from .base.types import (  # noqa
        Marshaler,
        Unmarshaler,

        MarshalerMaker,
        UnmarshalerMaker,

        MarshalerFactory,
        UnmarshalerFactory,

        Marshaling,
    )

    from .base.values import (  # noqa
        Value,
    )

    from .composite.iterables import (  # noqa
        IterableMarshaler,
        IterableUnmarshaler,
    )

    from .composite.wrapped import (  # noqa
        WrappedMarshaler,
        WrappedUnmarshaler,
    )

    from .factories.simple import (  # noqa
        SimpleMarshalerFactory,
        SimpleUnmarshalerFactory,
    )

    from .factories.match import (  # noqa
        MarshalerFactoryMatchClass,
        UnmarshalerFactoryMatchClass,
    )

    from .factories.moduleimport.configs import (  # noqa
        ModuleImport,
    )

    from .factories.moduleimport.factories import (  # noqa
        ModuleImportingMarshalerFactory,
        ModuleImportingUnmarshalerFactory,
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

    from .objects.dataclasses import (  # noqa
        AbstractDataclassFactory,
        DataclassMarshalerFactory,
        DataclassUnmarshalerFactory,
        get_dataclass_field_infos,
        get_dataclass_metadata,
    )

    from .objects.helpers import (  # noqa
        update_fields_metadata,
        update_object_metadata,
        with_field_metadata,
    )

    from .objects.marshal import (  # noqa
        ObjectMarshaler,
        SimpleObjectMarshalerFactory,
    )

    from .objects.metadata import (  # noqa
        FieldInfo,
        FieldInfos,
        FieldMetadata,
        FieldOptions,
        ObjectMetadata,
        ObjectSpecials,
    )

    from .objects.unmarshal import (  # noqa
        ObjectUnmarshaler,
        SimpleObjectUnmarshalerFactory,
    )

    from .polymorphism.marshal import (  # noqa
        PolymorphismMarshaler,
        PolymorphismMarshalerFactory,
        make_polymorphism_marshaler,
    )

    from .polymorphism.metadata import (  # noqa
        FieldTypeTagging,
        Impl,
        Impls,
        Polymorphism,
        TypeTagging,
        WrapperTypeTagging,
        polymorphism_from_impls,
        polymorphism_from_subclasses,
    )

    from .polymorphism.standard import (  # noqa
        standard_polymorphism_factories,
    )

    from .polymorphism.unions import (  # noqa
        PRIMITIVE_UNION_TYPES,
        PolymorphismUnionMarshalerFactory,
        PolymorphismUnionUnmarshalerFactory,
        PrimitiveUnionMarshaler,
        PrimitiveUnionMarshalerFactory,
        PrimitiveUnionUnmarshaler,
        PrimitiveUnionUnmarshalerFactory,
    )

    from .polymorphism.unmarshal import (  # noqa
        PolymorphismUnmarshaler,
        PolymorphismUnmarshalerFactory,
        make_polymorphism_unmarshaler,
    )

    from .singular.base64 import (  # noqa
        BASE64_MARSHALER_FACTORY,
        BASE64_UNMARSHALER_FACTORY,
    )

    from .singular.primitives import (  # noqa
        PRIMITIVE_TYPES,
    )

    from .trivial.forbidden import (  # noqa
        ForbiddenTypeMarshalerFactory,
        ForbiddenTypeUnmarshalerFactory,
    )

    from .trivial.nop import (  # noqa
        NOP_MARSHALER_UNMARSHALER,
        NopMarshalerUnmarshaler,
    )

    from .globals import (  # noqa
        global_config_registry,
        global_marshaler_factory,
        global_unmarshaler_factory,
        global_marshaling,

        marshal,
        unmarshal,

        register_global_config,
        register_global_module_import,
    )

    from .naming import (  # noqa
        Naming,
        translate_name,
    )

    from .standard import (  # noqa
        StandardFactories,
        DEFAULT_STANDARD_FACTORIES,

        new_standard_marshaler_factory,
        new_standard_unmarshaler_factory,

        install_standard_factories,
    )

"""
~> https://github.com/google/guice/commit/70248eafa90cd70a68b293763e53f6aec656e73c
"""
from .. import dataclasses as _dc


_dc.init_package(
    globals(),
    codegen=True,
)


##


from .. import lang as _lang  # noqa


with _lang.auto_proxy_init(globals()):
    ##

    from .helpers.constfn import (  # noqa
        ConstFn,
    )

    from .helpers.id import (  # noqa
        Id,
    )

    from .helpers.multis import (  # noqa
        bind_map_entry_const,
        bind_set_entry_const,

        ItemsBinderHelper as items_binder_helper,  # noqa
    )

    from .helpers.wrappers import (  # noqa
        WrapperBinderHelper as wrapper_binder_helper,  # noqa
    )

    from .binder import (  # noqa
        bind,
        bind_as_fn,
    )

    from .bindings import (  # noqa
        Binding,
    )

    from .eagers import (  # noqa
        Eager,
    )

    from .elements import (  # noqa
        Element,
        Elements,
        Elemental,
        as_elements,
        iter_elements,
    )

    from .errors import (  # noqa
        BaseKeyError,
        ConflictingKeyError,
        CyclicDependencyError,
        ScopeAlreadyOpenError,
        ScopeError,
        ScopeNotOpenError,
        UnboundKeyError,
    )

    from .injector import (  # noqa
        AsyncInjector,
        create_async_injector,
    )

    from .inspect import (  # noqa
        Kwarg,
        KwargsTarget,
        build_kwargs_target,
        tag,
    )

    from .keys import (  # noqa
        Key,
        as_key,
    )

    from .listeners import (  # noqa
        ProvisionListener,
        ProvisionListenerBinding,
        bind_provision_listener,
    )

    from .managed import (  # noqa
        create_async_managed_injector,
        make_async_managed_provider,

        create_managed_injector,
        make_managed_provider,

        create_maysync_managed_injector,
        make_maysync_managed_provider,
    )

    from .maysync import (  # noqa
        MaysyncInjector,
        create_maysync_injector,
    )

    from .multis import (  # noqa
        MapBinding,
        MapProvider,
        SetBinding,
        SetProvider,
        MapBinder,
        SetBinder,

        MapBinder as map_binder,  # noqa
        SetBinder as set_binder,  # noqa
    )


    from .overrides import (  # noqa
        Overrides,
        override,
    )

    from .origins import (  # noqa
        HasOrigins,
        Origin,
        Origins,
    )

    from .privates import (  # noqa
        Expose,
        Private,
        private,

        Expose as expose,  # noqa
    )

    from .providers import (  # noqa
        AsyncFnProvider,
        ConstProvider,
        CtorProvider,
        FnProvider,
        LinkProvider,
        Provider,
    )

    from .scopes import (  # noqa
        ScopeBinding,
        bind_scope,

        Singleton,

        ThreadScope,

        SeededScope,
        ScopeSeededProvider,
        bind_scope_seed,

        async_enter_seeded_scope,
        enter_seeded_scope,
        maysync_enter_seeded_scope,
    )

    from .sync import (  # noqa
        Injector,
        create_injector,
    )

    from .types import (  # noqa
        Scope,
        Tag,
        Unscoped,
    )

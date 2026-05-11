from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .events.injection import (  # noqa
        event_callbacks,
    )

    from .specs.injection import (  # noqa
        InjectorBackendSpecInstantiator,
    )

    from .tools.execution.injection import (  # noqa
        tool_catalog_entries,
        tool_context_providers,
        bind_tool_context_provider_to_key,
    )

from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .events.injection import event_callbacks  # noqa
    from .tools.execution.injection import tool_catalog_entries  # noqa
    from .tools.execution.injection import tool_context_providers  # noqa
    from .tools.execution.injection import bind_tool_context_provider_to_key  # noqa

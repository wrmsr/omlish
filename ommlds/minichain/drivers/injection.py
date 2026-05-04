from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .ai.injection import chat_options_providers  # noqa
    from .phases.injection import phase_callbacks  # noqa
    from .preparing.injection import placeholder_contents_providers  # noqa
    from .preparing.injection import system_message_providers  # noqa
    from .tools.injection import bind_tool_context_provider_to_key  # noqa
    from .tools.injection import tool_catalog_entries  # noqa
    from .tools.injection import tool_context_providers  # noqa

from omlish import lang as _lang


with _lang.auto_proxy_init(globals()):
    ##

    from .ai.injection import chat_options_providers  # noqa
    from .phases.injection import phase_callbacks  # noqa
    from .preparing.injection import placeholder_contents_providers  # noqa
    from .preparing.injection import system_message_providers  # noqa

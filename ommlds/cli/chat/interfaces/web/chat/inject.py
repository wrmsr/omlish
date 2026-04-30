from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import handler as _handler
    from . import service as _service
    from . import types as _types


##


def bind_chat() -> inj.Elements:
    els: list[inj.Elemental] = []

    els.extend([
        inj.bind(_handler.ChatCompletionsHandler, singleton=True),

        inj.bind(_service.ServiceChatStreamer, singleton=True),
        inj.bind(_types.ChatStreamer, to_key=_service.ServiceChatStreamer),
    ])

    return inj.as_elements(*els)

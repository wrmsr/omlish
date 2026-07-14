from omlish import inject as inj
from omlish import lang


with lang.auto_proxy_import(globals()):
    from . import driver as _driver
    from . import handler as _handler
    from . import service as _service
    from . import types as _types


##


def bind_chat(
        *,
        use_driver: bool = True,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.extend([
        inj.bind(_handler.ChatCompletionsHandler, singleton=True),
    ])

    #

    if use_driver:
        els.extend([
            inj.bind(_driver.DriverChatStreamer, singleton=True),
            inj.bind(_types.ChatStreamer, to_key=_driver.DriverChatStreamer),
        ])

    else:
        els.extend([
            inj.bind(_service.ServiceChatStreamer, singleton=True),
            inj.bind(_types.ChatStreamer, to_key=_service.ServiceChatStreamer),
        ])

    #

    return inj.as_elements(*els)

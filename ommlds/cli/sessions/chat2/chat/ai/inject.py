from omlish import inject as inj
from omlish import lang

from .injection import chat_options


with lang.auto_proxy_import(globals()):
    from . import rendering as _rendering
    from . import services as _services
    from . import types as _types


##


def bind_ai(
        *,
        stream: bool = False,
        silent: bool = False,
) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(chat_options().bind_items_provider(singleton=True))

    #

    if stream:
        ai_stack = inj.wrapper_binder_helper(_types.StreamAiChatGenerator)

        els.append(ai_stack.push_bind(to_ctor=_services.ChatChoicesStreamServiceStreamAiChatGenerator, singleton=True))

        if not silent:
            els.append(ai_stack.push_bind(to_ctor=_rendering.RenderingStreamAiChatGenerator, singleton=True))

        els.extend([
            inj.bind(_types.StreamAiChatGenerator, to_key=ai_stack.top),
            inj.bind(_types.AiChatGenerator, to_key=_types.StreamAiChatGenerator),
        ])

    else:
        ai_stack = inj.wrapper_binder_helper(_types.AiChatGenerator)

        els.append(ai_stack.push_bind(to_ctor=_services.ChatChoicesServiceAiChatGenerator, singleton=True))

        if not silent:
            els.append(ai_stack.push_bind(to_ctor=_rendering.RenderingAiChatGenerator, singleton=True))

        els.append(inj.bind(_types.AiChatGenerator, to_key=ai_stack.top))

    #

    return inj.as_elements(*els)

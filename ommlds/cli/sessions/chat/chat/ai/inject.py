from omlish import inject as inj
from omlish import lang

from ...... import minichain as mc
from .configs import AiConfig
from .injection import chat_options_providers


with lang.auto_proxy_import(globals()):
    from . import rendering as _rendering
    from . import services as _services
    from . import tools as _tools
    from . import types as _types


##


def bind_ai(cfg: AiConfig = AiConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(chat_options_providers().bind_items_provider(singleton=True))

    def _provide_chat_choices_options_provider(
            ps: _services.ChatChoicesServiceOptionsProviders,
    ) -> _services.ChatChoicesServiceOptionsProvider:
        return _services.ChatChoicesServiceOptionsProvider(lambda: [o for p in ps for o in p()])

    els.append(inj.bind(_provide_chat_choices_options_provider, singleton=True))

    #

    ai_stack = inj.wrapper_binder_helper(_types.AiChatGenerator)

    if cfg.stream:
        stream_ai_stack = inj.wrapper_binder_helper(_types.StreamAiChatGenerator)

        els.append(stream_ai_stack.push_bind(to_ctor=_services.ChatChoicesStreamServiceStreamAiChatGenerator, singleton=True))  # noqa

        if not cfg.silent:
            els.append(stream_ai_stack.push_bind(to_ctor=_rendering.RenderingStreamAiChatGenerator, singleton=True))

        els.extend([
            inj.bind(_types.StreamAiChatGenerator, to_key=stream_ai_stack.top),
            ai_stack.push_bind(to_key=_types.StreamAiChatGenerator),
        ])

    else:
        els.append(ai_stack.push_bind(to_ctor=_services.ChatChoicesServiceAiChatGenerator, singleton=True))

        if not cfg.silent:
            els.append(ai_stack.push_bind(to_ctor=_rendering.RenderingAiChatGenerator, singleton=True))

    if cfg.enable_tools:
        els.append(ai_stack.push_bind(to_ctor=_tools.ToolExecutingAiChatGenerator, singleton=True))

    els.append(inj.bind(_types.AiChatGenerator, to_key=ai_stack.top))

    #

    if cfg.enable_tools:
        def _provide_tools_chat_choices_options_provider(tc: mc.ToolCatalog) -> _services.ChatChoicesServiceOptionsProvider:  # noqa
            return _services.ChatChoicesServiceOptionsProvider(lambda: [
                mc.Tool(tce.spec)
                for tce in tc.by_name.values()
            ])

        els.append(chat_options_providers().bind_item(to_fn=_provide_tools_chat_choices_options_provider, singleton=True))  # noqa

    #

    return inj.as_elements(*els)

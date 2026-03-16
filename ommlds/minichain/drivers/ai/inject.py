from omlish import inject as inj

from ...chat.choices.services import ChatChoicesService
from ...chat.choices.stream.services import ChatChoicesStreamService
from ...chat.tools.types import Tool
from ...tools.execution.catalog import ToolCatalog
from .configs import AiConfig
from .eventemit import EventEmittingAiChatGenerator
from .eventemit import EventEmittingStreamAiChatGenerator
from .injection import chat_options_providers
from .services import ChatChoicesServiceAiChatGenerator
from .services import ChatChoicesServiceOptionsProvider
from .services import ChatChoicesServiceOptionsProviders
from .services import ChatChoicesStreamServiceStreamAiChatGenerator
from .services import InternalChatChoicesService
from .services import InternalChatChoicesStreamService
from .tools import ToolExecutingAiChatGenerator
from .types import AiChatGenerator
from .types import StreamAiChatGenerator


##


def bind_ai(cfg: AiConfig = AiConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    #

    els.append(chat_options_providers().bind_items_provider(singleton=True))

    def _provide_chat_choices_options_provider(
            ps: ChatChoicesServiceOptionsProviders,
    ) -> ChatChoicesServiceOptionsProvider:
        return ChatChoicesServiceOptionsProvider(lambda: [o for p in ps for o in p()])

    els.append(inj.bind(_provide_chat_choices_options_provider, singleton=True))

    #

    ai_stack = inj.wrapper_binder_helper(AiChatGenerator)

    if cfg.stream:
        els.append(inj.bind(InternalChatChoicesStreamService, to_key=ChatChoicesStreamService))

        stream_ai_stack = inj.wrapper_binder_helper(StreamAiChatGenerator)

        els.append(stream_ai_stack.push_bind(to_ctor=ChatChoicesStreamServiceStreamAiChatGenerator, singleton=True))  # noqa

        els.append(stream_ai_stack.push_bind(to_ctor=EventEmittingStreamAiChatGenerator, singleton=True))

        els.extend([
            inj.bind(StreamAiChatGenerator, to_key=stream_ai_stack.top),
            ai_stack.push_bind(to_key=StreamAiChatGenerator),
        ])

    else:
        els.append(inj.bind(InternalChatChoicesService, to_key=ChatChoicesService))

        els.append(ai_stack.push_bind(to_ctor=ChatChoicesServiceAiChatGenerator, singleton=True))

        els.append(ai_stack.push_bind(to_ctor=EventEmittingAiChatGenerator, singleton=True))

    if cfg.enable_tools:
        els.append(ai_stack.push_bind(to_ctor=ToolExecutingAiChatGenerator, singleton=True))

    els.append(inj.bind(AiChatGenerator, to_key=ai_stack.top))

    #

    if cfg.enable_tools:
        def _provide_tools_chat_choices_options_provider(
                tc: ToolCatalog,
        ) -> ChatChoicesServiceOptionsProvider:
            return ChatChoicesServiceOptionsProvider(lambda: [
                Tool(tce.spec)
                for tce in tc.by_name.values()
            ])

        els.append(chat_options_providers().bind_item(to_fn=_provide_tools_chat_choices_options_provider, singleton=True))  # noqa

    #

    return inj.as_elements(*els)

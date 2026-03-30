import typing as ta

from omlish import inject as inj

from ...chat.choices.services import ChatChoicesService
from ...chat.choices.stream.services import ChatChoicesStreamService
from ...chat.tools.types import Tool
from ...chat.transform.metadata import CreatedAtAddingMessageTransform
from ...chat.transform.metadata import MessageUuidAddingMessageTransform
from ...chat.transform.metadata import OriginalMetadataStrippingMessageTransform
from ...chat.transform.types import CompositeMessageTransform
from ...chat.transform.types import MessageTransformChatTransform
from ...tools.execution.catalog import ToolCatalog
from ...wrappers.uuids import RequestResponseUuidAddingService
from .configs import AiConfig
from .eventemit import EventEmittingAiChatGenerator
from .eventemit import EventEmittingStreamAiChatGenerator
from .injection import chat_options_providers
from .services import ChatChoicesServiceAiChatGenerator
from .services import ChatChoicesServiceOptionsProvider
from .services import ChatChoicesServiceOptionsProviders
from .services import ChatChoicesStreamServiceStreamAiChatGenerator
from .tools import ToolExecutingAiChatGenerator
from .transforms import AiChatChatTransform
from .transforms import ChatTransformAiChatGenerator
from .transforms import ChatTransformStreamAiChatGenerator
from .types import AiChatGenerator
from .types import StreamAiChatGenerator


InternalChatChoicesService = ta.NewType('InternalChatChoicesService', ChatChoicesService)  # type: ignore[misc]
InternalChatChoicesStreamService = ta.NewType('InternalChatChoicesStreamService', ChatChoicesStreamService)  # type: ignore[misc]  # noqa


##


def bind_ai(cfg: AiConfig = AiConfig()) -> inj.Elements:
    els: list[inj.Elemental] = []

    ##

    els.append(chat_options_providers().bind_items_provider(singleton=True))

    def _provide_chat_choices_options_provider(
            ps: ChatChoicesServiceOptionsProviders,
    ) -> ChatChoicesServiceOptionsProvider:
        return ChatChoicesServiceOptionsProvider(lambda: [o for p in ps for o in p()])

    els.append(inj.bind(_provide_chat_choices_options_provider, singleton=True))

    ##

    els.append(inj.bind(AiChatChatTransform, to_const=MessageTransformChatTransform(
        CompositeMessageTransform([
            MessageUuidAddingMessageTransform(),
            CreatedAtAddingMessageTransform(),
            OriginalMetadataStrippingMessageTransform(),
        ]),
    )))

    ##

    ai_stack = inj.wrapper_binder_helper(AiChatGenerator)

    if cfg.stream:
        stream_service_stack = inj.wrapper_binder_helper(InternalChatChoicesStreamService, unwrapped_key=ChatChoicesStreamService)  # noqa

        els.append(stream_service_stack.push_bind(to_key=ChatChoicesStreamService))

        els.append(stream_service_stack.push_bind(
            to_fn=inj.target(svc=ChatChoicesStreamService)(lambda svc: RequestResponseUuidAddingService(svc)),
            singleton=True,
        ))

        els.append(inj.bind(InternalChatChoicesStreamService, to_key=stream_service_stack.top))

        #

        stream_ai_stack = inj.wrapper_binder_helper(StreamAiChatGenerator)

        els.append(stream_ai_stack.push_bind(to_ctor=ChatChoicesStreamServiceStreamAiChatGenerator, singleton=True, with_=[  # noqa
            inj.bind(ChatChoicesStreamService, to_key=InternalChatChoicesStreamService),
        ]))

        els.append(stream_ai_stack.push_bind(to_ctor=ChatTransformStreamAiChatGenerator, singleton=True))
        els.append(stream_ai_stack.push_bind(to_ctor=EventEmittingStreamAiChatGenerator, singleton=True))

        els.extend([
            inj.bind(StreamAiChatGenerator, to_key=stream_ai_stack.top),
            ai_stack.push_bind(to_key=StreamAiChatGenerator),
        ])

    #

    else:
        service_stack = inj.wrapper_binder_helper(InternalChatChoicesService, unwrapped_key=ChatChoicesService)

        els.append(service_stack.push_bind(to_key=ChatChoicesService))

        els.append(service_stack.push_bind(
            to_fn=inj.target(svc=ChatChoicesService)(lambda svc: RequestResponseUuidAddingService(svc)),
            singleton=True,
        ))

        els.append(inj.bind(InternalChatChoicesService, to_key=service_stack.top))

        #

        els.append(ai_stack.push_bind(to_ctor=ChatChoicesServiceAiChatGenerator, singleton=True, with_=[
            inj.bind(ChatChoicesService, to_key=InternalChatChoicesService),
        ]))

        els.append(ai_stack.push_bind(to_ctor=ChatTransformAiChatGenerator, singleton=True))
        els.append(ai_stack.push_bind(to_ctor=EventEmittingAiChatGenerator, singleton=True))

    #

    if cfg.enable_tools:
        els.append(ai_stack.push_bind(to_ctor=ToolExecutingAiChatGenerator, singleton=True))

    els.append(inj.bind(AiChatGenerator, to_key=ai_stack.top))

    ##

    if cfg.enable_tools:
        def _provide_tools_chat_choices_options_provider(
                tc: ToolCatalog,
        ) -> ChatChoicesServiceOptionsProvider:
            return ChatChoicesServiceOptionsProvider(lambda: [
                Tool(tce.spec)
                for tce in tc.by_name.values()
            ])

        els.append(chat_options_providers().bind_item(to_fn=_provide_tools_chat_choices_options_provider, singleton=True))  # noqa

    ##

    return inj.as_elements(*els)

from ...... import minichain as mc
from .types import ChatPreparer
from .types import PlaceholderContentsProviders
from .types import SystemMessageProviders


##


class SimpleChatPreparer(ChatPreparer):
    def __init__(
            self,
            *,
            system_message_providers: SystemMessageProviders | None = None,
            placeholder_contents_providers: PlaceholderContentsProviders | None = None,
    ) -> None:
        super().__init__()

        self._system_message_providers = system_message_providers
        self._placeholder_contents_providers = placeholder_contents_providers

    async def prepare_chat(self, chat: 'mc.Chat') -> 'mc.Chat':
        ph_dct: dict[mc.PlaceholderContentKey, mc.Content] = {}

        ch_tfm = mc.MessageTransformChatTransform(
            mc.ContentTransformMessageTransform(
                mc.FnContentTransform(
                    lambda c: mc.render_content_str(
                        c,
                        placeholder_contents=ph_dct,
                    ),
                ),
            ),
        )

        chat = ch_tfm.transform(chat)

        return chat

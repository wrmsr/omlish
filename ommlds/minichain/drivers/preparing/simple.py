from ...chat.messages import Chat
from ...chat.messages import SystemMessage
from ...chat.transform.content import ContentTransformMessageTransform
from ...chat.transform.types import MessageTransformChatTransform
from ...content.placeholders import PlaceholderContents
from ...content.render.standard import StandardContentRenderer
from ...content.transform.types import FnContentTransform
from .types import ChatPreparer
from .types import PlaceholderContentsProviders
from .types import ProvidedSystemMessage
from .types import SystemMessageProviders


##


class SimpleChatPreparer(ChatPreparer):
    def __init__(
            self,
            *,
            system_message_providers: SystemMessageProviders | None = None,
            placeholder_contents_providers: PlaceholderContentsProviders | None = None,
            content_str_renderer: StandardContentRenderer | None = None,
    ) -> None:
        super().__init__()

        self._system_message_providers = system_message_providers
        self._placeholder_contents_providers = placeholder_contents_providers
        if content_str_renderer is None:
            content_str_renderer = StandardContentRenderer()
        self._content_str_renderer = content_str_renderer

    async def prepare_chat(self, chat: Chat) -> Chat:
        psm_lst: list[ProvidedSystemMessage] = []
        for smp in self._system_message_providers or []:
            psm_lst.extend(await smp.provide_system_messages())

        if psm_lst:
            psm_lst.sort(key=lambda x: x.priority or 0)
            sm = SystemMessage([
                psm.c for psm in psm_lst
            ])
            chat = [sm, *chat]

        #

        pcs: list[PlaceholderContents] = []
        for pcp in self._placeholder_contents_providers or []:
            pcs.append(await pcp.provide_placeholder_contents())

        #

        ch_tfm = MessageTransformChatTransform(
            ContentTransformMessageTransform(
                FnContentTransform(
                    lambda c: self._content_str_renderer.render(
                        c,
                        StandardContentRenderer.Context(
                            placeholder_contents=pcs,
                        ),
                    ),
                ),
            ),
        )

        chat = ch_tfm.transform(chat)

        return chat

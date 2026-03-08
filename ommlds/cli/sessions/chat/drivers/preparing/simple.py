from ...... import minichain as mc
from ..types import PlaceholderContentsProviders
from ..types import ProvidedSystemMessage
from ..types import SystemMessageProviders
from .types import ChatPreparer


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
        psm_lst: list[ProvidedSystemMessage] = []
        for smp in self._system_message_providers or []:
            psm_lst.extend(await smp.provide_system_messages())

        if psm_lst:
            psm_lst.sort(key=lambda x: x.priority or 0)
            sm = mc.SystemMessage([
                psm.c for psm in psm_lst
            ])
            chat = [sm, *chat]

        #

        pcs: list[mc.PlaceholderContents] = []
        for pcp in self._placeholder_contents_providers or []:
            pcs.append(await pcp.provide_placeholder_contents())

        #

        ch_tfm = mc.MessageTransformChatTransform(
            mc.ContentTransformMessageTransform(
                mc.FnContentTransform(
                    lambda c: mc.render_content_str(
                        c,
                        placeholder_contents=pcs,
                    ),
                ),
            ),
        )

        chat = ch_tfm.transform(chat)

        return chat

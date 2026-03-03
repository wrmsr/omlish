from ...... import minichain as mc
from .types import ChatPreparer


##


class SimpleChatPreparer(ChatPreparer):
    async def prepare_chat(self, chat: 'mc.Chat') -> 'mc.Chat':
        cm = mc.DefaultContentMaterializer[None]()
        ct = mc.ContentMaterializerContentTransform[None](cm)
        mt = mc.ContentTransformMessageTransform[None](ct)
        ht = mc.MessageTransformChatTransform[None](mt)

        return ht.transform(chat, None)

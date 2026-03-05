from ...... import minichain as mc
from .types import ChatPreparer


##


class SimpleChatPreparer(ChatPreparer):
    async def prepare_chat(self, chat: 'mc.Chat') -> 'mc.Chat':
        # ph_dct: dict[mc.PlaceholderContentKey, mc.Content] = {}
        #
        # # FIXME: lol
        # from ......minichain.lib.code import prompts as code_prompts
        # ph_dct[code_prompts.CodeAgentSystemPromptEnvironmentPlaceholder] = code_prompts.build_code_agent_system_prompt_environment()  # noqa
        #
        # cm = mc.DefaultContentMaterializer[None](
        #     placeholder_contents=ph_dct,
        # )
        #
        # ct = mc.CompositeContentTransform[None]([
        #     mc.ContentMaterializerContentTransform[None](cm),
        #     mc.FnContentTransform[None](mc.stringify_content),
        # ])
        #
        # mt = mc.ContentTransformMessageTransform[None](ct)
        #
        # ht = mc.MessageTransformChatTransform[None](mt)
        #
        # chat = ht.transform(chat, None)

        return chat

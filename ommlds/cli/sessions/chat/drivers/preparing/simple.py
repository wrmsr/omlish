from ...... import minichain as mc
from .types import ChatPreparer


##


class SimpleChatPreparer(ChatPreparer):
    async def prepare_chat(self, chat: 'mc.Chat') -> 'mc.Chat':
        ph_dct: dict[mc.PlaceholderContentKey, mc.Content] = {}

        # FIXME: lol
        # from ......minichain.lib.code import prompts as code_prompts
        # ph_dct[code_prompts.CodeAgentSystemPromptEnvironmentPlaceholder] = code_prompts.build_code_agent_system_prompt_environment()  # noqa

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

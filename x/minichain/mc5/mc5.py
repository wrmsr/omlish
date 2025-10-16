"""
input: interactive, oneshot
completion: immediate, stream
rendering: raw, markdown
tools: list
prompt: yes/no
"""
import abc
import typing as ta

from omlish import check
from omlish import lang

from ommlds import minichain as mc


##


class UserChatInput(lang.Abstract):
    @abc.abstractmethod
    def get_next_user_messages(self) -> ta.Awaitable[mc.UserChat]:
        raise NotImplementedError


class OneshotUserChatInput(UserChatInput):
    def __init__(
            self,
            initial_chat: mc.UserChat,
    ) -> None:
        super().__init__()

        self._pending_chat: mc.UserChat | None = initial_chat

    async def get_next_user_messages(self) -> mc.UserChat:
        ret = self._pending_chat
        self._pending_chat = None
        return ret or []


class InteractiveUserChatInput(UserChatInput):
    async def get_next_user_messages(self) -> mc.UserChat:
        try:
            prompt = input('> ')  # FIXME: async lol
        except EOFError:
            return []
        return [mc.UserMessage(prompt)]


##


class AiChatGenerator(lang.Abstract):
    @abc.abstractmethod
    def get_next_ai_messages(self, chat: mc.Chat) -> ta.Awaitable[mc.AiChat]:
        raise NotImplementedError


class ImmediateAiChatGenerator(AiChatGenerator, lang.Abstract):
    pass


class ChatChoicesServiceImmediateAiChatGenerator(ImmediateAiChatGenerator):
    def __init__(self, service: mc.ChatChoicesService) -> None:
        super().__init__()

        self._service = service

    async def get_next_ai_messages(self, chat: mc.Chat) -> mc.AiChat:
        resp = await self._service.invoke(mc.ChatChoicesRequest(chat))

        return check.single(resp.v).ms


class StreamAiChatGenerator(AiChatGenerator, lang.Abstract):
    pass


class ChatChoicesStreamServiceStreamAiChatGenerator(StreamAiChatGenerator):
    async def get_next_ai_messages(self, chat: mc.Chat) -> mc.AiChat:
        raise NotImplementedError


##


class ImmediateRendering(lang.Abstract):
    @abc.abstractmethod
    def render_content(self, content: mc.Content) -> ta.Awaitable[None]:
        raise NotImplementedError


class RawImmediateRendering(ImmediateRendering):
    pass


class MarkdownImmediateRendering(ImmediateRendering):
    pass


##


class StreamRendering(lang.Abstract):
    pass


class RawStreamRendering(StreamRendering):
    pass


class MarkdownStreamRendering(StreamRendering):
    pass


##


class ToolConfirmation(lang.Abstract):
    pass


class InteractiveToolConfirmation(lang.Abstract):
    pass


##


class ChatStorage(lang.Abstract):
    pass


class InMemoryChatStorage(ChatStorage):
    pass


class JsonFileChatStorage(ChatStorage):
    pass

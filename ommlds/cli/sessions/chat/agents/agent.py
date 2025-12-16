"""
TODO:
 - lifecycles
 - StreamService
"""
from .ai.types import AiChatGenerator
from .phases.manager import ChatPhaseManager
from .phases.types import ChatPhase
from .state.types import ChatStateManager
from .protocol import ChatAgentInput
from .protocol import ChatAgentOutputSink
from .protocol import UserMessagesChatAgentInput
from .protocol import AiMessagesChatAgentOutput


##


class ChatAgent:
    def __init__(
            self,
            *,
            phases: ChatPhaseManager,
            ai_chat_generator: AiChatGenerator,
            chat_state_manager: ChatStateManager,
    ) -> None:
        super().__init__()

        self._phases = phases
        self._ai_chat_generator = ai_chat_generator
        self._chat_state_manager = chat_state_manager

    async def start(self) -> None:
        await self._phases.set_phase(ChatPhase.STARTING)
        await self._phases.set_phase(ChatPhase.STARTED)

    async def stop(self) -> None:
        await self._phases.set_phase(ChatPhase.STOPPING)
        await self._phases.set_phase(ChatPhase.STOPPED)

    async def invoke(
            self,
            input: ChatAgentInput,  # noqa
            output: ChatAgentOutputSink,
    ) -> None:
        if isinstance(input, UserMessagesChatAgentInput):
            next_user_chat = input.chat

            prev_user_chat = (await self._chat_state_manager.get_state()).chat

            next_ai_chat = await self._ai_chat_generator.get_next_ai_messages([*prev_user_chat, *next_user_chat])

            await output(AiMessagesChatAgentOutput(next_ai_chat))

            await self._chat_state_manager.extend_chat([*next_user_chat, *next_ai_chat])

        else:
            raise TypeError(input)

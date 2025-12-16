from ...agents.agent import ChatAgent
from ..base import ChatInterface


##


class OneshotBareChatInterface(ChatInterface):
    def __init__(
            self,
            *,
            agent: ChatAgent,
    ) -> None:
        super().__init__()

        self._agent = agent

    async def run(self) -> None:
        await self._agent.start()

        await self._agent.stop()

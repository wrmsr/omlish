from ...... import minichain as mc
from .types import ChatDriverInterfaceGetter


##


class PreviousMessageReplayer:
    def __init__(
            self,
            *,
            chat_driver_interface: ChatDriverInterfaceGetter,
            chat_manager: mc.drivers.DriverStateManager,
    ) -> None:
        super().__init__()

        self._chat_driver_interface = chat_driver_interface
        self._chat_manager = chat_manager

    async def replay_previous_messages(self) -> None:
        chat = await self._chat_manager.get_chat()
        await (await self._chat_driver_interface()).mount_messages(chat, suppress_background_terminal_render=True)

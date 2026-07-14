from ...... import minichain as mc
from .types import ChatDriverInterfaceGetter


##


class TextualUserInputSender(mc.facades.UserInputSender):
    def __init__(
            self,
            *,
            chat_driver_interface: ChatDriverInterfaceGetter,
            facade: mc.facades.Facade,
    ) -> None:
        super().__init__()

        self._chat_driver_interface = chat_driver_interface
        self._facade = facade

    async def send_user_input(self, text: str, *, no_echo: bool = False) -> None:
        cdi = await self._chat_driver_interface()
        cdi.call_later(cdi.send_user_input, text, no_echo=no_echo)

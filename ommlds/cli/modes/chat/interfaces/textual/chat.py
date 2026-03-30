from ...facades.chat import UserInputSender
from ...facades.facade import ChatFacade
from .types import ChatAppGetter


##


class TextualUserInputSender(UserInputSender):
    def __init__(
            self,
            *,
            app: ChatAppGetter,
            facade: ChatFacade,
    ) -> None:
        super().__init__()

        self._app = app
        self._facade = facade

    async def send_user_input(self, text: str, *, no_echo: bool = False) -> None:
        await (await self._app()).send_user_input(text, no_echo=no_echo)

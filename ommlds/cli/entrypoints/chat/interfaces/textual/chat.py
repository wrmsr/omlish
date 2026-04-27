from ...... import minichain as mc
from .types import ChatAppGetter


##


class TextualUserInputSender(mc.facades.UserInputSender):
    def __init__(
            self,
            *,
            app: ChatAppGetter,
            facade: mc.facades.Facade,
    ) -> None:
        super().__init__()

        self._app = app
        self._facade = facade

    async def send_user_input(self, text: str, *, no_echo: bool = False) -> None:
        app = await self._app()
        app.call_later(app.send_user_input, text, no_echo=no_echo)

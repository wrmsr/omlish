from omdev.tui import textual as tx

from ..base import ChatInterface
from .app import ChatApp


##


class TextualChatInterface(ChatInterface):
    def __init__(
            self,
            *,
            app: ChatApp,
    ) -> None:
        super().__init__()

        self._app = app

    async def run(self) -> None:
        # FIXME: move lol
        tx.set_root_logger_to_devtools(self._app.devtools)

        await self._app.run_async()

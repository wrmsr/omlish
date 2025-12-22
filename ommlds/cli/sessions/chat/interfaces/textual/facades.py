from ...facades.ui import UiMessageDisplayer
from .app import ChatAppGetter


##


class ChatAppUiMessageDisplayer(UiMessageDisplayer):
    def __init__(
            self,
            *,
            app: ChatAppGetter,
    ) -> None:
        super().__init__()

        self._app = app

    async def display_ui_message(self, content: str) -> None:
        await (await self._app()).display_ui_message(content)

from ...... import minichain as mc
from .types import ChatDriverInterfaceGetter


##


class ChatAppUiMessageDisplayer(mc.facades.UiMessageDisplayer):
    def __init__(
            self,
            *,
            chat_driver_interface: ChatDriverInterfaceGetter,
    ) -> None:
        super().__init__()

        self._chat_driver_interface = chat_driver_interface

    async def display_ui_message(self, text: mc.CanUiText) -> None:
        rt = mc.ui_text_to_rich_text(text)
        await (await self._chat_driver_interface()).display_ui_message(rt)

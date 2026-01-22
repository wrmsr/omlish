import typing as ta

from ...clipboard import Clipboard
from ...clipboard import TextClipboardContents
from ...clipboard import get_platform_clipboard


if ta.TYPE_CHECKING:
    from textual.driver import Driver


##


class ClipboardAppMixin:
    _driver: ta.Optional['Driver']
    _clipboard: str

    #

    _clipboard_api_: Clipboard | None

    def _clipboard_api(self) -> Clipboard | None:
        try:
            return self._clipboard_api_
        except AttributeError:
            pass
        self._clipboard_api_ = get_platform_clipboard()
        return self._clipboard_api_

    #

    def copy_to_clipboard(self, text: str) -> None:
        if (cb_api := self._clipboard_api()) is None:
            super().copy_to_clipboard(text)  # type: ignore
            return

        self._clipboard = text
        cb_api.put(TextClipboardContents(text))

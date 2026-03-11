import abc
import typing as ta

from omlish import lang

from .text import CanFacadeText
from .text import FacadeText


##


class UiMessageDisplayer(lang.Abstract):
    @abc.abstractmethod
    def display_ui_message(self, text: CanFacadeText) -> ta.Awaitable[None]:
        pass


class NopUiMessageDisplayer(UiMessageDisplayer):
    async def display_ui_message(self, text: CanFacadeText) -> None:
        pass


class PrintMessageDisplayer(UiMessageDisplayer):
    async def display_ui_message(self, text: CanFacadeText) -> None:
        print(FacadeText.str_of(text))


##


class UiQuitSignal(lang.Func0[ta.Awaitable[None]]):
    pass


async def raise_system_exit_ui_quit_signal() -> None:
    raise SystemExit

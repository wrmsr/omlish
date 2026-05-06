import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang

from ..ui.text import CanUiText
from ..ui.text import UiText


##


class UiMessageDisplayer(lang.Abstract):
    @abc.abstractmethod
    def display_ui_message(self, text: CanUiText) -> ta.Awaitable[None]:
        pass


class NopUiMessageDisplayer(UiMessageDisplayer):
    async def display_ui_message(self, text: CanUiText) -> None:
        pass


class PrintMessageDisplayer(UiMessageDisplayer):
    async def display_ui_message(self, text: CanUiText) -> None:
        print(UiText.str_of(text))


##


class UiQuitSignal(lang.Func0[ta.Awaitable[None]]):
    pass


@dc.dataclass(frozen=True)
class RaiseUiQuitSignal:
    exc: BaseException | type[BaseException]

    async def __call__(self) -> None:
        raise self.exc

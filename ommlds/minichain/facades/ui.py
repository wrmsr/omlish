import abc
import typing as ta

from omlish import dataclasses as dc
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


@dc.dataclass(frozen=True)
class RaiseUiQuitSignal:
    exc: BaseException | type[BaseException]

    async def __call__(self) -> None:
        raise self.exc

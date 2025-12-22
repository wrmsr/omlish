import abc
import typing as ta

from omlish import lang


##


class UiMessageDisplayer(lang.Abstract):
    @abc.abstractmethod
    def display_ui_message(self, content: str) -> ta.Awaitable[None]:
        pass


class NopUiMessageDisplayer(UiMessageDisplayer):
    async def display_ui_message(self, content: str) -> None:
        pass


class PrintMessageDisplayer(UiMessageDisplayer):
    async def display_ui_message(self, content: str) -> None:
        print(content)


##


class UiQuitSignal(lang.Func0[ta.Awaitable[None]]):
    pass


async def raise_system_exit_ui_quit_signal() -> None:
    raise SystemExit

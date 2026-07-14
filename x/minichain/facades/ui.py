import abc
import typing as ta

from omcore import dataclasses as dc
from omcore import lang
from omcore import marshal as msh

from ..events.types import Event
from ..events.types import EventCallback
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


@dc.dataclass(frozen=True)
class UiMessageEvent(Event, lang.Final):
    """A user-facing notice, as an event - so ui messages can flow to frontends through timelines."""

    text: UiText


class EventEmittingUiMessageDisplayer(UiMessageDisplayer):
    def __init__(self, *, on_event: EventCallback) -> None:
        super().__init__()

        self._on_event = on_event

    async def display_ui_message(self, text: CanUiText) -> None:
        await self._on_event(UiMessageEvent(UiText.of(text)))


@msh.register_global_lazy_init
def _setup_marshal(cfgs: msh.ConfigRegistry) -> None:
    cfgs.update(Event, msh.OpenPolymorphismImpl(UiMessageEvent))


##


class UiQuitSignal(lang.Func0[ta.Awaitable[None]]):
    pass


@dc.dataclass(frozen=True)
class RaiseUiQuitSignal:
    exc: BaseException | type[BaseException]

    async def __call__(self) -> None:
        raise self.exc

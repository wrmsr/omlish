import typing as ta

from textual.binding import BindingType
from textual.screen import Screen as Screen_
from textual.screen import ScreenResultType
from textual.widget import Widget


##


class Screen(Screen_[ScreenResultType], Widget):
    BINDINGS: ta.ClassVar[ta.Sequence[BindingType]] = Screen_.BINDINGS  # type: ignore[assignment]

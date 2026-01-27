import typing as ta

from textual.app import App as App_
from textual.binding import BindingType


##


class App(App_):
    BINDINGS: ta.ClassVar[ta.Sequence[BindingType]] = App_.BINDINGS  # type: ignore[assignment]

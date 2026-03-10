import typing as ta

from omdev.tui import textual as tx
from omlish import check


##


class StatusBar(tx.Static):
    def __init__(
            self,
            content: str,
    ) -> None:
        super().__init__()

        self._content = content

    def compose(self) -> tx.ComposeResult:
        yield tx.Static(self._content)


class StatusContainer(tx.Static):
    def __init__(self, **kwargs: ta.Any) -> None:
        super().__init__(id='status-container', **kwargs)

    #

    _has_composed = False

    def compose(self) -> tx.ComposeResult:
        check.state(not self._has_composed)
        self._has_composed = True

        #

        with tx.Horizontal(id='status-horizontal'):
            yield StatusBar(' ')

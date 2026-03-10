from omdev.tui import textual as tx


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
    def compose(self) -> tx.ComposeResult:
        with tx.Horizontal(id='status-horizontal'):
            yield StatusBar(' ')

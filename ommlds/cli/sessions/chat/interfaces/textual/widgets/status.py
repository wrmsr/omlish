from omdev.tui import textual as tx


##


class StatusBar(tx.InitAddClass, tx.Static):
    init_add_class = 'status-bar'

    def __init__(
            self,
            content: str,
    ) -> None:
        super().__init__()

        self._content = content

    def compose(self) -> tx.ComposeResult:
        yield tx.Static(self._content)


class StatusContainer(tx.InitAddClass, tx.ComposeOnce, tx.Static):
    init_add_class = 'status-container'

    #

    def _compose_once(self) -> tx.ComposeResult:
        with tx.Horizontal(classes='status-horizontal'):
            yield StatusBar(' ')

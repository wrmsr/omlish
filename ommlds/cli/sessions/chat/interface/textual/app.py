from omdev.tui import textual as tx


##


class ChatApp(tx.App):
    def __init__(
            self,
    ) -> None:
        super().__init__()

    def compose(self) -> tx.ComposeResult:
        yield tx.Static('app goes here lol')

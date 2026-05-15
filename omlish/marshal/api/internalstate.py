from ... import lang


##


class InternalStateEntry(lang.Abstract):
    pass


class InternalState:
    def __init__(self) -> None:
        super().__init__()

        self._entries: dict[type[InternalStateEntry], InternalStateEntry] = {}

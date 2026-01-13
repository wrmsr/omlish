class InputHistoryManager:
    def add(self) -> None:
        pass

    def get_next(self, text: str | None = None) -> str | None:
        raise NotImplementedError

    def get_previous(self, text: str | None = None) -> str | None:
        raise NotImplementedError

    def reset_position(self) -> None:
        pass

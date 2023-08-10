from .. import reflect as rfl


class UnhandledTypeException(Exception):
    @property
    def rty(self) -> rfl.Type:
        return self.args[0]

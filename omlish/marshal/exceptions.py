from .. import reflect as rfl


class UnhandledTypeError(Exception):
    @property
    def rty(self) -> rfl.Type:
        return self.args[0]

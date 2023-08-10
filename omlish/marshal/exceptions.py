from .. import reflect as rfl


class UnhandledTypeException(Exception):
    @property
    def rty(self) -> rfl.Reflected:
        return self.args[0]

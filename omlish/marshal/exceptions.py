from .. import reflect as rfl


class MarshalError(Exception):
    pass


class UnhandledTypeError(MarshalError):
    @property
    def rty(self) -> rfl.Type:
        return self.args[0]


class ForbiddenTypeError(MarshalError):
    @property
    def rty(self) -> rfl.Type:
        return self.args[0]

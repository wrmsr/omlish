from .specs import Spec


class UnhandledSpecException(Exception):
    @property
    def spec(self) -> Spec:
        return self.args[0]

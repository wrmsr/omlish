import abc
import typing as ta


class Templater(abc.ABC):
    @abc.abstractmethod
    def escape(self, s: str) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def apply(self, s: str) -> str:
        raise NotImplementedError


class DictTemplater(Templater):
    def __init__(
            self,
            env: ta.Mapping[str, str],
    ) -> None:
        super().__init__()
        self._env = env

    def escape(self, s: str) -> str:
        return s.replace('{', '{{').replace('}', '}}')

    def apply(self, s: str) -> str:
        return s.format(**self._env)

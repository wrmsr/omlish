import abc
import typing as ta

from .models import Model
from .models import Request
from .models import Response
from .strings import transform_strings
from .wrappers import WrapperModel


##


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


##


class TemplatingModel(WrapperModel):
    def __init__(self, underlying: Model, templater: Templater) -> None:
        super().__init__(underlying)
        self._templater = templater

    def invoke(self, request: Request) -> Response:
        out_request = transform_strings(self._templater.apply, request)
        return super().invoke(out_request)

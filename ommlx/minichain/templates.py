import abc
import typing as ta

from .services import Service
from .services import ServiceRequest
from .services import ServiceResponse
from .strings import transform_strings
from .wrappers import WrapperService


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


class TemplatingService(WrapperService):
    def __init__(self, underlying: Service, templater: Templater) -> None:
        super().__init__(underlying)
        self._templater = templater

    def invoke(self, request: ServiceRequest) -> ServiceResponse:
        out_request = transform_strings(self._templater.apply, request)
        return super().invoke(out_request)

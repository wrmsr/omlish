import abc
import typing as ta

from omlish import lang

from .content import Content
from .models import Model
from .models import Request
from .models import Response
from .vectors import Vector


##


EmbeddingModel: ta.TypeAlias = Model[Content, Vector]


class EmbeddingModel_(EmbeddingModel, lang.Abstract):  # noqa
    @abc.abstractmethod
    def generate(self, request: Request[Content]) -> Response[Vector]:
        raise NotImplementedError

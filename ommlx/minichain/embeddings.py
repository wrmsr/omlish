import abc
import dataclasses as dc
import typing as ta

from omlish import lang

from .content import Content
from .models import Model
from .models import Request
from .models import Response


##


@dc.dataclass(frozen=True)
class Embedding:
    """array.array('f' | 'd', ...) preferred"""

    v: ta.Sequence[float]


EmbeddingModel: ta.TypeAlias = Model[Content, Embedding]


class EmbeddingModel_(EmbeddingModel, lang.Abstract):  # noqa
    @abc.abstractmethod
    def generate(self, request: Request[Content]) -> Response[Embedding]:
        raise NotImplementedError

import dataclasses as dc
import typing as ta

from .models import Model


##


@dc.dataclass(frozen=True)
class Embedding:
    """array.array('f' | 'd', ...) preferred"""

    v: ta.Sequence[float]


EmbeddingModel: ta.TypeAlias = Model[str, Embedding]

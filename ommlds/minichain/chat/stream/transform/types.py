import abc
import typing as ta

from omlish import lang

from ....transform.general import CompositeGeneralTransform
from ....transform.general import FnGeneralTransform
from ....transform.general import GeneralTransform
from ....transform.general import TypeFilteredGeneralTransform
from ..types import AiDelta


##


class AiDeltaTransform(GeneralTransform[AiDelta], lang.Abstract):
    @abc.abstractmethod
    def transform(self, d: AiDelta) -> ta.Sequence[AiDelta]:
        raise NotImplementedError


##


class CompositeAiDeltaTransform(CompositeGeneralTransform[AiDelta], AiDeltaTransform):
    pass


class FnAiDeltaTransform(FnGeneralTransform[AiDelta], AiDeltaTransform):
    pass


class TypeFilteredAiDeltaTransform(TypeFilteredGeneralTransform[AiDelta], AiDeltaTransform):
    pass

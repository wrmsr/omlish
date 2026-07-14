import abc
import typing as ta

from omlish import lang

from ....transform.general import CompositeGeneralTransform
from ....transform.general import FnGeneralTransform
from ....transform.general import GeneralTransform
from ....transform.general import TypeFilteredGeneralTransform
from ....transform.sequence import CompositeSequenceTransform
from ....transform.sequence import FnSequenceTransform
from ....transform.sequence import GeneralTransformSequenceTransform
from ....transform.sequence import SequenceTransform
from ..types import AiDelta
from ..types import AiDeltas


##


class AiDeltaTransform(GeneralTransform[AiDelta], lang.Abstract):
    @abc.abstractmethod
    def transform(self, d: AiDelta) -> ta.Sequence[AiDelta]:
        raise NotImplementedError


#


class CompositeAiDeltaTransform(CompositeGeneralTransform[AiDelta], AiDeltaTransform):
    pass


class FnAiDeltaTransform(FnGeneralTransform[AiDelta], AiDeltaTransform):
    pass


class TypeFilteredAiDeltaTransform(TypeFilteredGeneralTransform[AiDelta], AiDeltaTransform):
    pass


##


class AiDeltasTransform(SequenceTransform[AiDelta], lang.Abstract):
    @abc.abstractmethod
    def transform(self, ds: AiDeltas) -> AiDeltas:
        raise NotImplementedError


#


class CompositeAiDeltasTransform(CompositeSequenceTransform[AiDelta], AiDeltasTransform):
    pass


class FnAiDeltasTransform(FnSequenceTransform[AiDelta], AiDeltasTransform):
    pass


class AiDeltaTransformAiDeltasTransform(GeneralTransformSequenceTransform[AiDelta], AiDeltasTransform):
    pass

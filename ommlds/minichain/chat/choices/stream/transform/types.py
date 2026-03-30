# import abc
# import typing as ta
#
# from omlish import lang
#
# from .....transform.general import CompositeGeneralTransform
# from .....transform.general import FnGeneralTransform
# from .....transform.general import GeneralTransform
# from .....transform.general import TypeFilteredGeneralTransform
# from ..types import AiDeltas
#
#
# ##
#
#
# class AiDeltasTransform(GeneralTransform[AiDeltas], lang.Abstract):
#     @abc.abstractmethod
#     def transform(self, d: AiDeltas) -> ta.Sequence[AiDeltas]:
#         raise NotImplementedError
#
#
# ##
#
#
# class CompositeAiDeltasTransform(CompositeGeneralTransform[AiDeltas], AiDeltasTransform):
#     pass
#
#
# class FnAiDeltasTransform(FnGeneralTransform[AiDeltas], AiDeltasTransform):
#     pass
#
#
# class TypeFilteredAiDeltasTransform(TypeFilteredGeneralTransform[AiDeltas], AiDeltasTransform):
#     pass

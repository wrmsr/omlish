# import abc
#
# from omlish import lang
#
# from .....transform.sequence import CompositeSequenceTransform
# from .....transform.sequence import FnSequenceTransform
# from .....transform.sequence import SequenceTransform
# from ...stream.types import AiDelta
# from ...stream.types import AiDeltas
#
#
# ##
#
#
# class AiDeltasTransform(SequenceTransform[AiDelta], lang.Abstract):
#     @abc.abstractmethod
#     def transform(self, d: AiDeltas) -> AiDeltas:
#         raise NotImplementedError
#
#
# ##
#
#
# class CompositeAiDeltasTransform(CompositeSequenceTransform[AiDelta], AiDeltasTransform):
#     pass
#
#
# class FnAiDeltasTransform(FnSequenceTransform[AiDelta], AiDeltasTransform):
#     pass

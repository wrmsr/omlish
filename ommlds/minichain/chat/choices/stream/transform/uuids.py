# import uuid
# import typing as ta
#
# from ...metadata import MessageUuid
# from ..types import AiDelta
# from .types import AiDeltaTransform
#
#
# ##
#
#
# class TypeSequentialMessageUuidAddingAiDeltaTransform(AiDeltaTransform):
#     def __init__(self) -> None:
#         super().__init__()
#
#         self._last: tuple[type[AiDelta], MessageUuid] | None = None
#
#     def transform(self, d: AiDelta) -> ta.Sequence[AiDelta]:
#         dty = type(d)
#         dmu = d.metadata.get(MessageUuid)
#
#         last = self._last
#         if last == (dty, dmu):
#             return [d]
#
#         if last is not None and last[0] == dty and dmu is None:
#             d = d.with_metadata(last[1])
#             return [d]
#
#         if dmu is None:
#             dmu = MessageUuid(uuid.uuid4())
#             d = d.with_metadata(dmu)
#
#         self._last = (dty, dmu)
#         return [d]

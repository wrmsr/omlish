# """
# FIXME:
#  - replace ..content with this
# """
# import typing as ta
#
# from omlish import lang
#
# from ..messages import Message
#
#
# MessageF = ta.TypeVar('MessageF', bound=Message)
# MessageT = ta.TypeVar('MessageT', bound=Message)
#
#
# ##
#
#
# class ContentTransformMessageTransform(lang.Abstract, ta.Generic[MessageF, MessageT]):
#     def transform_message(self, message: MessageF) -> ta.Sequence[MessageT]:
#         raise NotImplementedError

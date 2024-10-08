# import abc
# import collections.abc
# import typing as ta
#
# T = ta.TypeVar('T')
#
#
# class Templater(abc.ABC):
#     @abc.abstractmethod
#     def escape(self, s: str) -> str:
#         raise NotImplementedError
#
#     @abc.abstractmethod
#     def apply(self, s: TemplatableT) -> TemplatableT:
#         raise NotImplementedError
#
#
# class StringTemplater(Templater):
#     @abc.abstractmethod
#     def apply_string(self, s: str) -> str:
#         raise NotImplementedError

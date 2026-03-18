# import abc
# import enum
# import fnmatch
# import re
# import typing as ta
#
# from omlish import dataclasses as dc
# from omlish import lang
#
# from ..permissions import ToolPermissionState
#
#
# ##
#
#
# @dc.dataclass(frozen=True)
# class ToolPermissionTarget(lang.Abstract, lang.Sealed):
#     pass
#
#
# @dc.dataclass(frozen=True)
# class FsToolPermissionTarget(ToolPermissionTarget, lang.Final):
#     path: str
#
#
# @dc.dataclass(frozen=True)
# class UrlToolPermissionTarget(ToolPermissionTarget, lang.Final):
#     url: str
#
#     _: dc.KW_ONLY
#
#     method: str | None = None
#
#
# ##
#
#
# class ToolPermissionMatcher(lang.Abstract):
#     @abc.abstractmethod
#     def match(self, target: ToolPermissionTarget) -> bool:
#         raise NotImplementedError
#
#
# @dc.dataclass(frozen=True)
# class GlobToolPermissionMatcher(ToolPermissionMatcher, lang.Final):
#     s: str
#
#     def match(self, target: ToolPermissionTarget) -> bool:
#         return fnmatch.fnmatch(target, self.s)
#
#
# @dc.dataclass(frozen=True)
# class RegexToolPermissionMatcher(ToolPermissionMatcher, lang.Final):
#     s: str
#
#     @lang.cached_property
#     def pat(self) -> re.Pattern:
#         return re.compile(self.s)
#
#     def match(self, target: ToolPermissionTarget) -> bool:
#         return self.pat.fullmatch(target) is not None
#
#
# ##
#
#
# class ToolPermissionAction(enum.Enum):
#     DENIED = enum.auto()
#     CONFIRM = enum.auto()
#     ALLOWED = enum.auto()
#
#
# ##
#
#
# @dc.dataclass(frozen=True)
# class ToolPermissionRule(lang.Final):
#     # subject: ?
#     targets: ta.Sequence[ToolPermissionTarget]
#     actions: ta.AbstractSet[ToolPermissionAction]
#     result: ToolPermissionState

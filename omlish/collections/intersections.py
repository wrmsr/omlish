"""
https://github.com/python/typing/issues/213
"""
import typing as ta

from .. import lang
from .persistent import PersistentMapping
from .sorted import SortedMapping


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class PersistentSortedMapping(
    PersistentMapping[K, V],
    SortedMapping[K, V],
    lang.Abstract,
    ta.Generic[K, V],
):
    pass

import typing as ta

from ._compat import compat


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


@compat
class ImmutableMultiDict(ta.Mapping[K, V]):
    pass

import typing as ta

from .. import lang
from .proxy import ProxyMapping
from .proxy import ProxySequence
from .proxy import ProxySet


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class Unmodifiable(lang.Abstract, lang.Sealed):
    pass


@ta.final
class UnmodifiableSequence(ProxySequence[T], Unmodifiable, lang.Final):
    pass


@ta.final
class UnmodifiableSet(ProxySet[T], Unmodifiable, lang.Final):
    pass


@ta.final
class UnmodifiableMapping(ProxyMapping[K, V], Unmodifiable, lang.Final):
    pass

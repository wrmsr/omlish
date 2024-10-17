import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


Value: ta.TypeAlias = ta.Any


##


class Node(dc.Frozen, lang.Abstract, cache_hash=True):
    pass


class Builder(lang.Abstract):
    pass

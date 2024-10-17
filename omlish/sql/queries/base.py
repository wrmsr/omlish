import typing as ta

from ... import dataclasses as dc
from ... import lang


##


Value: ta.TypeAlias = ta.Any


##


class Node(dc.Frozen, lang.Abstract, cache_hash=True):
    pass


class Builder(lang.Abstract):
    pass

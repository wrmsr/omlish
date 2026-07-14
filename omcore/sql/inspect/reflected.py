"""
Pure IR describing what was reflected from a live database. This layer does no IO and knows no dialect - it is just a
neutral, lossy snapshot. Reflection deliberately fails *open*: a real table may carry things we don't model (extension
artifacts, exotic constraints), and an inspector should record what it understands and ignore the rest rather than
refuse.
"""
import typing as ta

from ... import dataclasses as dc
from ... import lang


##


@dc.dataclass(frozen=True)
class ReflectedColumn(lang.Final):
    name: str
    type: str  # the raw dialect type string, verbatim from the db

    _: dc.KW_ONLY

    nullable: bool = True
    primary_key: bool = False


@dc.dataclass(frozen=True)
class ReflectedIndex(lang.Final):
    name: str
    columns: ta.Sequence[str]

    _: dc.KW_ONLY

    unique: bool = False


@dc.dataclass(frozen=True)
class ReflectedTable(lang.Final):
    name: str
    columns: ta.Sequence[ReflectedColumn]

    _: dc.KW_ONLY

    indexes: ta.Sequence[ReflectedIndex] = ()

"""
https://github.com/wrmsr/tokamak/blob/3ebf3395c5bb78b80e0445199958cb81f4cf9be8/tokamak-core/src/main/java/com/wrmsr/tokamak/core/plan/node/visitor/PNodeVisitor.java

Node
  Cache
  Extract
  Filter
  Group
  Join
  Lookup
  Output
  Project
  Scan
  Scope
  ScopeExit
  Search
  State
  Struct
  Unify
  Union
  Unnest
  Values
"""
import abc
import typing as ta

from omlish import dataclasses as dc
from omlish import lang


##


class PFunc(dc.Frozen, lang.Final):
    name: str
    type: ta.Any
    purity: ta.Any


##


class PNode(lang.Abstract):
    pass


##


class PAggregate(PNode, lang.Abstract):
    pass


class PSingleSource(PNode, lang.Abstract):
    pass


class PIndexable(PNode, lang.Abstract):
    pass


##


class PBaseNode(PNode, dc.Frozen, lang.Abstract):
    name: str

    _: dc.KW_ONLY

    anns: ta.Any = None
    fld_anns: ta.Any = None


##


class PCache(PBaseNode, PSingleSource, lang.Final):
    src: PNode


class PExtract(PBaseNode, PSingleSource, lang.Final):
    src: PNode
    src_fld: str
    sct_mbr: str
    out_fld: str


class PFilter(PBaseNode, PSingleSource, lang.Final):
    src: PNode
    fld: str
    lnk: ta.Literal['linked', 'unlinked']


class PGroup(PBaseNode, PAggregate, PSingleSource, lang.Final):
    src: PBaseNode
    key_flds: ta.Sequence[str]
    lst_fld: str

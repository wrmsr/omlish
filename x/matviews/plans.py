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


VNode: ta.TypeAlias = ta.Any
Dtype: ta.TypeAlias = ta.Any
SNode: ta.TypeAlias = ta.Any
StructType: ta.TypeAlias = ta.Any


##


class PFunc(dc.Frozen, lang.Final, reorder=True, cache_hash=True):
    name: str
    type: ta.Any
    purity: ta.Any


class PInvalidations(dc.Frozen, lang.Final):
    class Invalidation(dc.Frozen, lang.Final):
        keys_by_src: ta.Mapping[str, str]
        upd_mask: ta.AbstractSet[str] | None
        strength: ta.Literal['strong', 'weak']

    class NodeEntry(dc.Frozen, lang.Final):
        lst: ta.Sequence['PInvalidations.Invalidation']
        upd_mask: ta.AbstractSet[str] | None

    dct: ta.Mapping[str, NodeEntry]


class PNodeField(dc.Frozen, lang.Final):
    node: 'PNode'
    fld: str


class PNodeId(dc.Frozen, lang.Final):
    i: int


class PProjection(dc.Frozen, lang.Final):
    ins_by_out: ta.Mapping[str, VNode]


class SchemaTable(dc.Frozen, lang.Final):
    s: str
    t: str


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


class PInternal(PNode, lang.Abstract):
    pass


class PInvalidatable(PNode, lang.Abstract):
    pass


class PInvalidator(PNode, lang.Abstract):
    pass


class PJoinLike(PNode, lang.Abstract):
    pass


class PLeaf(PNode, lang.Abstract):
    pass


##


class PBaseNode(PNode, dc.Frozen, lang.Abstract):
    _: dc.KW_ONLY

    name: str = '?'
    anns: ta.Any = dc.xfield(None, repr=False)
    fld_anns: ta.Any = dc.xfield(None, repr=False)


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


class PJoin(PBaseNode, PJoinLike, lang.Final):
    class Branch(dc.Frozen, lang.Final):
        node: PNode
        flds: ta.Sequence[str]

    branches: ta.Sequence[Branch]
    mode: ta.Literal['inner', 'left', 'full']


class PLookup(PBaseNode, PInternal, PJoinLike, lang.Final):
    class Branch(dc.Frozen, lang.Final):
        node: PNode
        flds: ta.AbstractSet[str]

    src: PNode
    src_keys: ta.AbstractSet[str]
    branches: ta.Sequence[PBaseNode]


class POutput(PBaseNode, PInvalidatable, PSingleSource, lang.Final):
    src: PNode
    tgts: ta.Sequence[str]


class PProject(PBaseNode, PSingleSource, lang.Final):
    src: PNode
    prj: PProjection


class PScan(PBaseNode, PLeaf, lang.Final):
    st: SchemaTable
    flds: ta.Mapping[str, Dtype]
    invs: PInvalidations


class PScope(PBaseNode, PSingleSource, lang.Final):
    src: PNode


class PScopeExit(PBaseNode, PSingleSource, lang.Final):
    src: PNode
    scope: str


class PSearch(PBaseNode, PSingleSource, lang.Final):
    src: PNode
    sch: SNode
    out: str
    type: Dtype


class PState(PBaseNode, PInvalidatable, PInvalidator, PSingleSource, lang.Final):
    src: PNode
    denorm: ta.Literal['input'] | None
    ivs: PInvalidations


class PStruct(PBaseNode, PSingleSource, lang.Final):
    src: PNode
    type: StructType
    in_flds: ta.Sequence[str]
    out: str


class PUnify(PBaseNode, PSingleSource, lang.Final):
    src: PNode
    uni_flds: ta.AbstractSet[str]
    out: str


class PUnion(PBaseNode, lang.Final):
    srcs: ta.Sequence[PNode]
    idx_fld: str | None


class PUnnest(PBaseNode, PIndexable, PSingleSource, lang.Final):
    src: PNode
    lst_fld: str
    unnest_flds: ta.Mapping[str, Dtype]
    idx_fld: str | None


class PValues(PBaseNode, PLeaf, PIndexable, lang.Final):
    flds: ta.Mapping[str, Dtype]
    vals: ta.Sequence[ta.Sequence[ta.Any]]
    idx_fld: str | None
    strict: ta.Literal['strict', 'nonstrict']


##


def _main() -> None:
    x: PNode = PScan(SchemaTable('foo', 'bar'), {}, None)
    x = POutput(x, [])
    print(x)


if __name__ == '__main__':
    _main()

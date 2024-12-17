"""
TODO:
 - hints:
  - build full node -> comments map without dumb scans
  - comma etc. as terminators
  - detect orphan hot comments
  - enforce unique binding
  - hints.py?
"""
import typing as ta

from omnibus import check
from omnibus import collections as ocol
from omnibus import properties
from omnibus._vendor import antlr4

from . import analysis as ana
from . import nodes as no


class TokenAnalysis:

    def __init__(self, root: no.Node) -> None:
        super().__init__()

        self._root = check.isinstance(root, no.Node)

        self._basic = ana.basic(self._root)

    @properties.cached
    @property
    def toks(self) -> ocol.IndexedSeq[antlr4.Token]:
        return ocol.IndexedSeq(self._root.meta[antlr4.ParserRuleContext].parser.getInputStream().tokens, identity=True)

    @properties.cached
    @property
    def pctxs(self) -> ocol.SortedMapping[int, ta.AbstractSet[antlr4.ParserRuleContext]]:
        def rec(pctx):
            if isinstance(pctx, antlr4.TerminalNode):
                tok = pctx.symbol
            else:
                tok = pctx.start
            check.isinstance(tok, antlr4.Token)
            dct.setdefault(self.toks.idx(tok), ocol.IdentitySet()).add(pctx)

            for cpctx in getattr(pctx, 'children', []):
                rec(cpctx)

        dct = ocol.SkipListDict()
        rec(self._root.meta[antlr4.ParserRuleContext])
        return dct

    @properties.cached
    @property
    def rpctxs(self) -> ta.Mapping[antlr4.ParserRuleContext, int]:
        return ocol.IdentityKeyDict((c, i) for i, cs in self.pctxs.items() for c in cs)

    @properties.cached
    @property
    def rnodes(self) -> ta.Mapping[no.Node, int]:
        return ocol.IdentityKeyDict((n, self.rpctxs[n.meta[antlr4.ParserRuleContext]]) for n in self._basic.nodes)

    def get_node_toks(self, node: no.Node) -> ta.Sequence[antlr4.Token]:
        l = self.rnodes[node]
        try:
            r = next(self.pctxs.itemsfrom(l + 1))[0]
        except StopIteration:
            r = -1
        return self.toks[l:r]

    def get_node_comments(self, node: no.Node) -> ta.Sequence[str]:
        return [t.text for t in self.get_node_toks(node) if t.channel == 1]

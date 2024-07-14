import typing as ta

from .. import check
from .. import collections as ocol
from .. import properties
from .._vendor import antlr4


class TokenAnalysis:

    def __init__(self, root: antlr4.ParserRuleContext) -> None:
        super().__init__()

        self._root = check.isinstance(root, antlr4.ParserRuleContext)

    @properties.cached
    @property
    def toks(self) -> ocol.IndexedSeq[antlr4.Token]:
        return ocol.IndexedSeq(self._root.parser.getInputStream().tokens, identity=True)

    @properties.cached
    @property
    def ctxs(self) -> ocol.SortedMapping[int, ta.AbstractSet[antlr4.ParserRuleContext]]:
        def rec(ctx):
            if isinstance(ctx, antlr4.TerminalNode):
                tok = ctx.symbol  # noqa
            else:
                tok = ctx.start
            check.isinstance(tok, antlr4.Token)
            dct.setdefault(self.toks.idx(tok), ocol.IdentitySet()).add(ctx)

            if not isinstance(ctx, antlr4.TerminalNode):
                for cctx in ctx.children or []:
                    rec(cctx)

        dct = ocol.SkipListDict()
        rec(self._root)
        return dct

    @properties.cached
    @property
    def rctxs(self) -> ta.Mapping[antlr4.ParserRuleContext, int]:
        return ocol.IdentityKeyDict((c, i) for i, cs in self.ctxs.items() for c in cs)

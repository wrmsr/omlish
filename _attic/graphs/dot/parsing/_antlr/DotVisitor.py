# flake8: noqa
# type: ignore
# Generated from Dot.g4 by ANTLR 4.8
from ....._vendor.antlr4 import *
if __name__ is not None and "." in __name__:
    from .DotParser import DotParser
else:
    from DotParser import DotParser

# This class defines a complete generic visitor for a parse tree produced by DotParser.

class DotVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by DotParser#graph.
    def visitGraph(self, ctx:DotParser.GraphContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#stmtList.
    def visitStmtList(self, ctx:DotParser.StmtListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#stmt.
    def visitStmt(self, ctx:DotParser.StmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#attrStmt.
    def visitAttrStmt(self, ctx:DotParser.AttrStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#attrList.
    def visitAttrList(self, ctx:DotParser.AttrListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#aList.
    def visitAList(self, ctx:DotParser.AListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#edgeStmt.
    def visitEdgeStmt(self, ctx:DotParser.EdgeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#edgeRHS.
    def visitEdgeRHS(self, ctx:DotParser.EdgeRHSContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#edgeop.
    def visitEdgeop(self, ctx:DotParser.EdgeopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#nodeStmt.
    def visitNodeStmt(self, ctx:DotParser.NodeStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#nodeId.
    def visitNodeId(self, ctx:DotParser.NodeIdContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#port.
    def visitPort(self, ctx:DotParser.PortContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#subgraph.
    def visitSubgraph(self, ctx:DotParser.SubgraphContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by DotParser#ident.
    def visitIdent(self, ctx:DotParser.IdentContext):
        return self.visitChildren(ctx)



del DotParser

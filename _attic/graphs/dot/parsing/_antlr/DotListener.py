# flake8: noqa
# type: ignore
# Generated from Dot.g4 by ANTLR 4.8
from ....._vendor.antlr4 import *
if __name__ is not None and "." in __name__:
    from .DotParser import DotParser
else:
    from DotParser import DotParser

# This class defines a complete listener for a parse tree produced by DotParser.
class DotListener(ParseTreeListener):

    # Enter a parse tree produced by DotParser#graph.
    def enterGraph(self, ctx:DotParser.GraphContext):
        pass

    # Exit a parse tree produced by DotParser#graph.
    def exitGraph(self, ctx:DotParser.GraphContext):
        pass


    # Enter a parse tree produced by DotParser#stmtList.
    def enterStmtList(self, ctx:DotParser.StmtListContext):
        pass

    # Exit a parse tree produced by DotParser#stmtList.
    def exitStmtList(self, ctx:DotParser.StmtListContext):
        pass


    # Enter a parse tree produced by DotParser#stmt.
    def enterStmt(self, ctx:DotParser.StmtContext):
        pass

    # Exit a parse tree produced by DotParser#stmt.
    def exitStmt(self, ctx:DotParser.StmtContext):
        pass


    # Enter a parse tree produced by DotParser#attrStmt.
    def enterAttrStmt(self, ctx:DotParser.AttrStmtContext):
        pass

    # Exit a parse tree produced by DotParser#attrStmt.
    def exitAttrStmt(self, ctx:DotParser.AttrStmtContext):
        pass


    # Enter a parse tree produced by DotParser#attrList.
    def enterAttrList(self, ctx:DotParser.AttrListContext):
        pass

    # Exit a parse tree produced by DotParser#attrList.
    def exitAttrList(self, ctx:DotParser.AttrListContext):
        pass


    # Enter a parse tree produced by DotParser#aList.
    def enterAList(self, ctx:DotParser.AListContext):
        pass

    # Exit a parse tree produced by DotParser#aList.
    def exitAList(self, ctx:DotParser.AListContext):
        pass


    # Enter a parse tree produced by DotParser#edgeStmt.
    def enterEdgeStmt(self, ctx:DotParser.EdgeStmtContext):
        pass

    # Exit a parse tree produced by DotParser#edgeStmt.
    def exitEdgeStmt(self, ctx:DotParser.EdgeStmtContext):
        pass


    # Enter a parse tree produced by DotParser#edgeRHS.
    def enterEdgeRHS(self, ctx:DotParser.EdgeRHSContext):
        pass

    # Exit a parse tree produced by DotParser#edgeRHS.
    def exitEdgeRHS(self, ctx:DotParser.EdgeRHSContext):
        pass


    # Enter a parse tree produced by DotParser#edgeop.
    def enterEdgeop(self, ctx:DotParser.EdgeopContext):
        pass

    # Exit a parse tree produced by DotParser#edgeop.
    def exitEdgeop(self, ctx:DotParser.EdgeopContext):
        pass


    # Enter a parse tree produced by DotParser#nodeStmt.
    def enterNodeStmt(self, ctx:DotParser.NodeStmtContext):
        pass

    # Exit a parse tree produced by DotParser#nodeStmt.
    def exitNodeStmt(self, ctx:DotParser.NodeStmtContext):
        pass


    # Enter a parse tree produced by DotParser#nodeId.
    def enterNodeId(self, ctx:DotParser.NodeIdContext):
        pass

    # Exit a parse tree produced by DotParser#nodeId.
    def exitNodeId(self, ctx:DotParser.NodeIdContext):
        pass


    # Enter a parse tree produced by DotParser#port.
    def enterPort(self, ctx:DotParser.PortContext):
        pass

    # Exit a parse tree produced by DotParser#port.
    def exitPort(self, ctx:DotParser.PortContext):
        pass


    # Enter a parse tree produced by DotParser#subgraph.
    def enterSubgraph(self, ctx:DotParser.SubgraphContext):
        pass

    # Exit a parse tree produced by DotParser#subgraph.
    def exitSubgraph(self, ctx:DotParser.SubgraphContext):
        pass


    # Enter a parse tree produced by DotParser#ident.
    def enterIdent(self, ctx:DotParser.IdentContext):
        pass

    # Exit a parse tree produced by DotParser#ident.
    def exitIdent(self, ctx:DotParser.IdentContext):
        pass



del DotParser

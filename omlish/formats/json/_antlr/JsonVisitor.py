# type: ignore
# ruff: noqa
# flake8: noqa
# @omlish-generated
# Generated from Json.g4 by ANTLR 4.13.2
from ....text.antlr._runtime._all import *
if "." in __name__:
    from .JsonParser import JsonParser
else:
    from JsonParser import JsonParser

# This class defines a complete generic visitor for a parse tree produced by JsonParser.

class JsonVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by JsonParser#json.
    def visitJson(self, ctx:JsonParser.JsonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JsonParser#obj.
    def visitObj(self, ctx:JsonParser.ObjContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JsonParser#pair.
    def visitPair(self, ctx:JsonParser.PairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JsonParser#arr.
    def visitArr(self, ctx:JsonParser.ArrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JsonParser#value.
    def visitValue(self, ctx:JsonParser.ValueContext):
        return self.visitChildren(ctx)



del JsonParser
# type: ignore
# ruff: noqa
# flake8: noqa
# Generated from Json5.g4 by ANTLR 4.13.2
from omlish.antlr._runtime._all import *
if "." in __name__:
    from .Json5Parser import Json5Parser
else:
    from Json5Parser import Json5Parser

# This class defines a complete generic visitor for a parse tree produced by Json5Parser.

class Json5Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by Json5Parser#json5.
    def visitJson5(self, ctx:Json5Parser.Json5Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Json5Parser#obj.
    def visitObj(self, ctx:Json5Parser.ObjContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Json5Parser#pair.
    def visitPair(self, ctx:Json5Parser.PairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Json5Parser#key.
    def visitKey(self, ctx:Json5Parser.KeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Json5Parser#value.
    def visitValue(self, ctx:Json5Parser.ValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Json5Parser#arr.
    def visitArr(self, ctx:Json5Parser.ArrContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Json5Parser#number.
    def visitNumber(self, ctx:Json5Parser.NumberContext):
        return self.visitChildren(ctx)



del Json5Parser
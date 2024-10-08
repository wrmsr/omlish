# Generated from /Users/spinlock/src/wrmsr/omlish/x/antlr_dev/tests/Json.g4 by ANTLR 4.13.2
from x.antlr_dev._runtime import *
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


    # Visit a parse tree produced by JsonParser#key.
    def visitKey(self, ctx:JsonParser.KeyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JsonParser#array.
    def visitArray(self, ctx:JsonParser.ArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JsonParser#value.
    def visitValue(self, ctx:JsonParser.ValueContext):
        return self.visitChildren(ctx)



del JsonParser
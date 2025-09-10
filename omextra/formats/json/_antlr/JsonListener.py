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

# This class defines a complete listener for a parse tree produced by JsonParser.
class JsonListener(ParseTreeListener):

    # Enter a parse tree produced by JsonParser#json.
    def enterJson(self, ctx:JsonParser.JsonContext):
        pass

    # Exit a parse tree produced by JsonParser#json.
    def exitJson(self, ctx:JsonParser.JsonContext):
        pass


    # Enter a parse tree produced by JsonParser#obj.
    def enterObj(self, ctx:JsonParser.ObjContext):
        pass

    # Exit a parse tree produced by JsonParser#obj.
    def exitObj(self, ctx:JsonParser.ObjContext):
        pass


    # Enter a parse tree produced by JsonParser#pair.
    def enterPair(self, ctx:JsonParser.PairContext):
        pass

    # Exit a parse tree produced by JsonParser#pair.
    def exitPair(self, ctx:JsonParser.PairContext):
        pass


    # Enter a parse tree produced by JsonParser#arr.
    def enterArr(self, ctx:JsonParser.ArrContext):
        pass

    # Exit a parse tree produced by JsonParser#arr.
    def exitArr(self, ctx:JsonParser.ArrContext):
        pass


    # Enter a parse tree produced by JsonParser#value.
    def enterValue(self, ctx:JsonParser.ValueContext):
        pass

    # Exit a parse tree produced by JsonParser#value.
    def exitValue(self, ctx:JsonParser.ValueContext):
        pass



del JsonParser
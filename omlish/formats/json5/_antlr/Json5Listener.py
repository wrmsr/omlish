# type: ignore
# ruff: noqa
# flake8: noqa
# @omlish-generated
# Generated from Json5.g4 by ANTLR 4.13.2
from ....text.antlr._runtime._all import *
if "." in __name__:
    from .Json5Parser import Json5Parser
else:
    from Json5Parser import Json5Parser

# This class defines a complete listener for a parse tree produced by Json5Parser.
class Json5Listener(ParseTreeListener):

    # Enter a parse tree produced by Json5Parser#json5.
    def enterJson5(self, ctx:Json5Parser.Json5Context):
        pass

    # Exit a parse tree produced by Json5Parser#json5.
    def exitJson5(self, ctx:Json5Parser.Json5Context):
        pass


    # Enter a parse tree produced by Json5Parser#obj.
    def enterObj(self, ctx:Json5Parser.ObjContext):
        pass

    # Exit a parse tree produced by Json5Parser#obj.
    def exitObj(self, ctx:Json5Parser.ObjContext):
        pass


    # Enter a parse tree produced by Json5Parser#pair.
    def enterPair(self, ctx:Json5Parser.PairContext):
        pass

    # Exit a parse tree produced by Json5Parser#pair.
    def exitPair(self, ctx:Json5Parser.PairContext):
        pass


    # Enter a parse tree produced by Json5Parser#key.
    def enterKey(self, ctx:Json5Parser.KeyContext):
        pass

    # Exit a parse tree produced by Json5Parser#key.
    def exitKey(self, ctx:Json5Parser.KeyContext):
        pass


    # Enter a parse tree produced by Json5Parser#value.
    def enterValue(self, ctx:Json5Parser.ValueContext):
        pass

    # Exit a parse tree produced by Json5Parser#value.
    def exitValue(self, ctx:Json5Parser.ValueContext):
        pass


    # Enter a parse tree produced by Json5Parser#arr.
    def enterArr(self, ctx:Json5Parser.ArrContext):
        pass

    # Exit a parse tree produced by Json5Parser#arr.
    def exitArr(self, ctx:Json5Parser.ArrContext):
        pass


    # Enter a parse tree produced by Json5Parser#number.
    def enterNumber(self, ctx:Json5Parser.NumberContext):
        pass

    # Exit a parse tree produced by Json5Parser#number.
    def exitNumber(self, ctx:Json5Parser.NumberContext):
        pass



del Json5Parser
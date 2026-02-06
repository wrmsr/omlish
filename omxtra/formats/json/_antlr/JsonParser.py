# type: ignore
# ruff: noqa
# flake8: noqa
# @omlish-generated
# Generated from Json.g4 by ANTLR 4.13.2
# encoding: utf-8
from ....text.antlr._runtime._all import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,12,57,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,1,0,1,0,1,0,1,
        1,1,1,1,1,1,1,5,1,18,8,1,10,1,12,1,21,9,1,1,1,1,1,1,1,1,1,3,1,27,
        8,1,1,2,1,2,1,2,1,2,1,3,1,3,1,3,1,3,5,3,37,8,3,10,3,12,3,40,9,3,
        1,3,1,3,1,3,1,3,3,3,46,8,3,1,4,1,4,1,4,1,4,1,4,1,4,1,4,3,4,55,8,
        4,1,4,0,0,5,0,2,4,6,8,0,0,61,0,10,1,0,0,0,2,26,1,0,0,0,4,28,1,0,
        0,0,6,45,1,0,0,0,8,54,1,0,0,0,10,11,3,8,4,0,11,12,5,0,0,1,12,1,1,
        0,0,0,13,14,5,1,0,0,14,19,3,4,2,0,15,16,5,2,0,0,16,18,3,4,2,0,17,
        15,1,0,0,0,18,21,1,0,0,0,19,17,1,0,0,0,19,20,1,0,0,0,20,22,1,0,0,
        0,21,19,1,0,0,0,22,23,5,3,0,0,23,27,1,0,0,0,24,25,5,1,0,0,25,27,
        5,3,0,0,26,13,1,0,0,0,26,24,1,0,0,0,27,3,1,0,0,0,28,29,5,10,0,0,
        29,30,5,4,0,0,30,31,3,8,4,0,31,5,1,0,0,0,32,33,5,5,0,0,33,38,3,8,
        4,0,34,35,5,2,0,0,35,37,3,8,4,0,36,34,1,0,0,0,37,40,1,0,0,0,38,36,
        1,0,0,0,38,39,1,0,0,0,39,41,1,0,0,0,40,38,1,0,0,0,41,42,5,6,0,0,
        42,46,1,0,0,0,43,44,5,5,0,0,44,46,5,6,0,0,45,32,1,0,0,0,45,43,1,
        0,0,0,46,7,1,0,0,0,47,55,5,10,0,0,48,55,5,11,0,0,49,55,3,2,1,0,50,
        55,3,6,3,0,51,55,5,7,0,0,52,55,5,8,0,0,53,55,5,9,0,0,54,47,1,0,0,
        0,54,48,1,0,0,0,54,49,1,0,0,0,54,50,1,0,0,0,54,51,1,0,0,0,54,52,
        1,0,0,0,54,53,1,0,0,0,55,9,1,0,0,0,5,19,26,38,45,54
    ]

class JsonParser ( Parser ):

    grammarFileName = "Json.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'{'", "','", "'}'", "':'", "'['", "']'", 
                     "'true'", "'false'", "'null'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "STRING", "NUMBER", "WS" ]

    RULE_json = 0
    RULE_obj = 1
    RULE_pair = 2
    RULE_arr = 3
    RULE_value = 4

    ruleNames =  [ "json", "obj", "pair", "arr", "value" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    STRING=10
    NUMBER=11
    WS=12

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class JsonContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value(self):
            return self.getTypedRuleContext(JsonParser.ValueContext,0)


        def EOF(self):
            return self.getToken(JsonParser.EOF, 0)

        def getRuleIndex(self):
            return JsonParser.RULE_json

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson" ):
                listener.enterJson(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson" ):
                listener.exitJson(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitJson" ):
                return visitor.visitJson(self)
            else:
                return visitor.visitChildren(self)




    def json(self):

        localctx = JsonParser.JsonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_json)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 10
            self.value()
            self.state = 11
            self.match(JsonParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ObjContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pair(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(JsonParser.PairContext)
            else:
                return self.getTypedRuleContext(JsonParser.PairContext,i)


        def getRuleIndex(self):
            return JsonParser.RULE_obj

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterObj" ):
                listener.enterObj(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitObj" ):
                listener.exitObj(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitObj" ):
                return visitor.visitObj(self)
            else:
                return visitor.visitChildren(self)




    def obj(self):

        localctx = JsonParser.ObjContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_obj)
        self._la = 0 # Token type
        try:
            self.state = 26
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 13
                self.match(JsonParser.T__0)
                self.state = 14
                self.pair()
                self.state = 19
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 15
                    self.match(JsonParser.T__1)
                    self.state = 16
                    self.pair()
                    self.state = 21
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 22
                self.match(JsonParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 24
                self.match(JsonParser.T__0)
                self.state = 25
                self.match(JsonParser.T__2)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class PairContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(JsonParser.STRING, 0)

        def value(self):
            return self.getTypedRuleContext(JsonParser.ValueContext,0)


        def getRuleIndex(self):
            return JsonParser.RULE_pair

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterPair" ):
                listener.enterPair(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitPair" ):
                listener.exitPair(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPair" ):
                return visitor.visitPair(self)
            else:
                return visitor.visitChildren(self)




    def pair(self):

        localctx = JsonParser.PairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 28
            self.match(JsonParser.STRING)
            self.state = 29
            self.match(JsonParser.T__3)
            self.state = 30
            self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(JsonParser.ValueContext)
            else:
                return self.getTypedRuleContext(JsonParser.ValueContext,i)


        def getRuleIndex(self):
            return JsonParser.RULE_arr

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArr" ):
                listener.enterArr(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArr" ):
                listener.exitArr(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArr" ):
                return visitor.visitArr(self)
            else:
                return visitor.visitChildren(self)




    def arr(self):

        localctx = JsonParser.ArrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_arr)
        self._la = 0 # Token type
        try:
            self.state = 45
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 32
                self.match(JsonParser.T__4)
                self.state = 33
                self.value()
                self.state = 38
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 34
                    self.match(JsonParser.T__1)
                    self.state = 35
                    self.value()
                    self.state = 40
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 41
                self.match(JsonParser.T__5)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 43
                self.match(JsonParser.T__4)
                self.state = 44
                self.match(JsonParser.T__5)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ValueContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(JsonParser.STRING, 0)

        def NUMBER(self):
            return self.getToken(JsonParser.NUMBER, 0)

        def obj(self):
            return self.getTypedRuleContext(JsonParser.ObjContext,0)


        def arr(self):
            return self.getTypedRuleContext(JsonParser.ArrContext,0)


        def getRuleIndex(self):
            return JsonParser.RULE_value

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterValue" ):
                listener.enterValue(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitValue" ):
                listener.exitValue(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitValue" ):
                return visitor.visitValue(self)
            else:
                return visitor.visitChildren(self)




    def value(self):

        localctx = JsonParser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_value)
        try:
            self.state = 54
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [10]:
                self.enterOuterAlt(localctx, 1)
                self.state = 47
                self.match(JsonParser.STRING)
                pass
            elif token in [11]:
                self.enterOuterAlt(localctx, 2)
                self.state = 48
                self.match(JsonParser.NUMBER)
                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 3)
                self.state = 49
                self.obj()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 4)
                self.state = 50
                self.arr()
                pass
            elif token in [7]:
                self.enterOuterAlt(localctx, 5)
                self.state = 51
                self.match(JsonParser.T__6)
                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 6)
                self.state = 52
                self.match(JsonParser.T__7)
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 7)
                self.state = 53
                self.match(JsonParser.T__8)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx






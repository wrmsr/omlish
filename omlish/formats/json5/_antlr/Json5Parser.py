# type: ignore
# ruff: noqa
# flake8: noqa
# Generated from Json5.g4 by ANTLR 4.13.2
# encoding: utf-8
from omlish.antlr._runtime._all import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,15,74,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,1,0,3,0,16,8,0,1,0,1,0,1,1,1,1,1,1,1,1,5,1,24,8,1,10,1,12,1,27,
        9,1,1,1,3,1,30,8,1,1,1,1,1,1,1,1,1,3,1,36,8,1,1,2,1,2,1,2,1,2,1,
        3,1,3,1,4,1,4,1,4,1,4,1,4,3,4,49,8,4,1,5,1,5,1,5,1,5,5,5,55,8,5,
        10,5,12,5,58,9,5,1,5,3,5,61,8,5,1,5,1,5,1,5,1,5,3,5,67,8,5,1,6,3,
        6,70,8,6,1,6,1,6,1,6,0,0,7,0,2,4,6,8,10,12,0,2,3,0,9,10,12,12,14,
        14,1,0,11,12,78,0,15,1,0,0,0,2,35,1,0,0,0,4,37,1,0,0,0,6,41,1,0,
        0,0,8,48,1,0,0,0,10,66,1,0,0,0,12,69,1,0,0,0,14,16,3,8,4,0,15,14,
        1,0,0,0,15,16,1,0,0,0,16,17,1,0,0,0,17,18,5,0,0,1,18,1,1,0,0,0,19,
        20,5,1,0,0,20,25,3,4,2,0,21,22,5,2,0,0,22,24,3,4,2,0,23,21,1,0,0,
        0,24,27,1,0,0,0,25,23,1,0,0,0,25,26,1,0,0,0,26,29,1,0,0,0,27,25,
        1,0,0,0,28,30,5,2,0,0,29,28,1,0,0,0,29,30,1,0,0,0,30,31,1,0,0,0,
        31,32,5,3,0,0,32,36,1,0,0,0,33,34,5,1,0,0,34,36,5,3,0,0,35,19,1,
        0,0,0,35,33,1,0,0,0,36,3,1,0,0,0,37,38,3,6,3,0,38,39,5,4,0,0,39,
        40,3,8,4,0,40,5,1,0,0,0,41,42,7,0,0,0,42,7,1,0,0,0,43,49,5,10,0,
        0,44,49,3,12,6,0,45,49,3,2,1,0,46,49,3,10,5,0,47,49,5,9,0,0,48,43,
        1,0,0,0,48,44,1,0,0,0,48,45,1,0,0,0,48,46,1,0,0,0,48,47,1,0,0,0,
        49,9,1,0,0,0,50,51,5,5,0,0,51,56,3,8,4,0,52,53,5,2,0,0,53,55,3,8,
        4,0,54,52,1,0,0,0,55,58,1,0,0,0,56,54,1,0,0,0,56,57,1,0,0,0,57,60,
        1,0,0,0,58,56,1,0,0,0,59,61,5,2,0,0,60,59,1,0,0,0,60,61,1,0,0,0,
        61,62,1,0,0,0,62,63,5,6,0,0,63,67,1,0,0,0,64,65,5,5,0,0,65,67,5,
        6,0,0,66,50,1,0,0,0,66,64,1,0,0,0,67,11,1,0,0,0,68,70,5,13,0,0,69,
        68,1,0,0,0,69,70,1,0,0,0,70,71,1,0,0,0,71,72,7,1,0,0,72,13,1,0,0,
        0,9,15,25,29,35,48,56,60,66,69
    ]

class Json5Parser ( Parser ):

    grammarFileName = "Json5.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'{'", "','", "'}'", "':'", "'['", "']'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "SINGLE_LINE_COMMENT", 
                      "MULTI_LINE_COMMENT", "LITERAL", "STRING", "NUMBER", 
                      "NUMERIC_LITERAL", "SYMBOL", "IDENTIFIER", "WS" ]

    RULE_json5 = 0
    RULE_obj = 1
    RULE_pair = 2
    RULE_key = 3
    RULE_value = 4
    RULE_arr = 5
    RULE_number = 6

    ruleNames =  [ "json5", "obj", "pair", "key", "value", "arr", "number" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    SINGLE_LINE_COMMENT=7
    MULTI_LINE_COMMENT=8
    LITERAL=9
    STRING=10
    NUMBER=11
    NUMERIC_LITERAL=12
    SYMBOL=13
    IDENTIFIER=14
    WS=15

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.13.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class Json5Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(Json5Parser.EOF, 0)

        def value(self):
            return self.getTypedRuleContext(Json5Parser.ValueContext,0)


        def getRuleIndex(self):
            return Json5Parser.RULE_json5

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterJson5" ):
                listener.enterJson5(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitJson5" ):
                listener.exitJson5(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitJson5" ):
                return visitor.visitJson5(self)
            else:
                return visitor.visitChildren(self)




    def json5(self):

        localctx = Json5Parser.Json5Context(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_json5)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 15
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if (((_la) & ~0x3f) == 0 and ((1 << _la) & 15906) != 0):
                self.state = 14
                self.value()


            self.state = 17
            self.match(Json5Parser.EOF)
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
                return self.getTypedRuleContexts(Json5Parser.PairContext)
            else:
                return self.getTypedRuleContext(Json5Parser.PairContext,i)


        def getRuleIndex(self):
            return Json5Parser.RULE_obj

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

        localctx = Json5Parser.ObjContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_obj)
        self._la = 0 # Token type
        try:
            self.state = 35
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 19
                self.match(Json5Parser.T__0)
                self.state = 20
                self.pair()
                self.state = 25
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,1,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 21
                        self.match(Json5Parser.T__1)
                        self.state = 22
                        self.pair() 
                    self.state = 27
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,1,self._ctx)

                self.state = 29
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==2:
                    self.state = 28
                    self.match(Json5Parser.T__1)


                self.state = 31
                self.match(Json5Parser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 33
                self.match(Json5Parser.T__0)
                self.state = 34
                self.match(Json5Parser.T__2)
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

        def key(self):
            return self.getTypedRuleContext(Json5Parser.KeyContext,0)


        def value(self):
            return self.getTypedRuleContext(Json5Parser.ValueContext,0)


        def getRuleIndex(self):
            return Json5Parser.RULE_pair

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

        localctx = Json5Parser.PairContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_pair)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 37
            self.key()
            self.state = 38
            self.match(Json5Parser.T__3)
            self.state = 39
            self.value()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class KeyContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def STRING(self):
            return self.getToken(Json5Parser.STRING, 0)

        def IDENTIFIER(self):
            return self.getToken(Json5Parser.IDENTIFIER, 0)

        def LITERAL(self):
            return self.getToken(Json5Parser.LITERAL, 0)

        def NUMERIC_LITERAL(self):
            return self.getToken(Json5Parser.NUMERIC_LITERAL, 0)

        def getRuleIndex(self):
            return Json5Parser.RULE_key

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterKey" ):
                listener.enterKey(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitKey" ):
                listener.exitKey(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitKey" ):
                return visitor.visitKey(self)
            else:
                return visitor.visitChildren(self)




    def key(self):

        localctx = Json5Parser.KeyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_key)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 41
            _la = self._input.LA(1)
            if not((((_la) & ~0x3f) == 0 and ((1 << _la) & 22016) != 0)):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
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
            return self.getToken(Json5Parser.STRING, 0)

        def number(self):
            return self.getTypedRuleContext(Json5Parser.NumberContext,0)


        def obj(self):
            return self.getTypedRuleContext(Json5Parser.ObjContext,0)


        def arr(self):
            return self.getTypedRuleContext(Json5Parser.ArrContext,0)


        def LITERAL(self):
            return self.getToken(Json5Parser.LITERAL, 0)

        def getRuleIndex(self):
            return Json5Parser.RULE_value

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

        localctx = Json5Parser.ValueContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_value)
        try:
            self.state = 48
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [10]:
                self.enterOuterAlt(localctx, 1)
                self.state = 43
                self.match(Json5Parser.STRING)
                pass
            elif token in [11, 12, 13]:
                self.enterOuterAlt(localctx, 2)
                self.state = 44
                self.number()
                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 3)
                self.state = 45
                self.obj()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 4)
                self.state = 46
                self.arr()
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 5)
                self.state = 47
                self.match(Json5Parser.LITERAL)
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


    class ArrContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def value(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(Json5Parser.ValueContext)
            else:
                return self.getTypedRuleContext(Json5Parser.ValueContext,i)


        def getRuleIndex(self):
            return Json5Parser.RULE_arr

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

        localctx = Json5Parser.ArrContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_arr)
        self._la = 0 # Token type
        try:
            self.state = 66
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,7,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 50
                self.match(Json5Parser.T__4)
                self.state = 51
                self.value()
                self.state = 56
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,5,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 52
                        self.match(Json5Parser.T__1)
                        self.state = 53
                        self.value() 
                    self.state = 58
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,5,self._ctx)

                self.state = 60
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==2:
                    self.state = 59
                    self.match(Json5Parser.T__1)


                self.state = 62
                self.match(Json5Parser.T__5)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 64
                self.match(Json5Parser.T__4)
                self.state = 65
                self.match(Json5Parser.T__5)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NumberContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMERIC_LITERAL(self):
            return self.getToken(Json5Parser.NUMERIC_LITERAL, 0)

        def NUMBER(self):
            return self.getToken(Json5Parser.NUMBER, 0)

        def SYMBOL(self):
            return self.getToken(Json5Parser.SYMBOL, 0)

        def getRuleIndex(self):
            return Json5Parser.RULE_number

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterNumber" ):
                listener.enterNumber(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitNumber" ):
                listener.exitNumber(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNumber" ):
                return visitor.visitNumber(self)
            else:
                return visitor.visitChildren(self)




    def number(self):

        localctx = Json5Parser.NumberContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_number)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 69
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==13:
                self.state = 68
                self.match(Json5Parser.SYMBOL)


            self.state = 71
            _la = self._input.LA(1)
            if not(_la==11 or _la==12):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx






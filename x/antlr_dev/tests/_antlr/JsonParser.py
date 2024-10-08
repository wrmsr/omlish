# Generated from /Users/spinlock/src/wrmsr/omlish/x/antlr_dev/tests/Json.g4 by ANTLR 4.13.2
# encoding: utf-8
from x.antlr_dev._runtime import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,12,60,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,1,0,1,
        0,1,1,1,1,1,1,1,1,5,1,19,8,1,10,1,12,1,22,9,1,1,1,1,1,1,1,1,1,3,
        1,28,8,1,1,2,1,2,1,2,1,2,1,3,1,3,1,4,1,4,1,4,1,4,5,4,40,8,4,10,4,
        12,4,43,9,4,1,4,1,4,1,4,1,4,3,4,49,8,4,1,5,1,5,1,5,1,5,1,5,1,5,1,
        5,3,5,58,8,5,1,5,0,0,6,0,2,4,6,8,10,0,0,63,0,12,1,0,0,0,2,27,1,0,
        0,0,4,29,1,0,0,0,6,33,1,0,0,0,8,48,1,0,0,0,10,57,1,0,0,0,12,13,3,
        10,5,0,13,1,1,0,0,0,14,15,5,1,0,0,15,20,3,4,2,0,16,17,5,2,0,0,17,
        19,3,4,2,0,18,16,1,0,0,0,19,22,1,0,0,0,20,18,1,0,0,0,20,21,1,0,0,
        0,21,23,1,0,0,0,22,20,1,0,0,0,23,24,5,3,0,0,24,28,1,0,0,0,25,26,
        5,1,0,0,26,28,5,3,0,0,27,14,1,0,0,0,27,25,1,0,0,0,28,3,1,0,0,0,29,
        30,3,6,3,0,30,31,5,4,0,0,31,32,3,10,5,0,32,5,1,0,0,0,33,34,5,7,0,
        0,34,7,1,0,0,0,35,36,5,5,0,0,36,41,3,10,5,0,37,38,5,2,0,0,38,40,
        3,10,5,0,39,37,1,0,0,0,40,43,1,0,0,0,41,39,1,0,0,0,41,42,1,0,0,0,
        42,44,1,0,0,0,43,41,1,0,0,0,44,45,5,6,0,0,45,49,1,0,0,0,46,47,5,
        5,0,0,47,49,5,6,0,0,48,35,1,0,0,0,48,46,1,0,0,0,49,9,1,0,0,0,50,
        58,5,7,0,0,51,58,5,8,0,0,52,58,3,2,1,0,53,58,3,8,4,0,54,58,5,9,0,
        0,55,58,5,10,0,0,56,58,5,11,0,0,57,50,1,0,0,0,57,51,1,0,0,0,57,52,
        1,0,0,0,57,53,1,0,0,0,57,54,1,0,0,0,57,55,1,0,0,0,57,56,1,0,0,0,
        58,11,1,0,0,0,5,20,27,41,48,57
    ]

class JsonParser ( Parser ):

    grammarFileName = "Json.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'{'", "','", "'}'", "':'", "'['", "']'", 
                     "<INVALID>", "<INVALID>", "'true'", "'false'", "'null'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "STRING", "NUMBER", 
                      "TRUE", "FALSE", "NULL", "WS" ]

    RULE_json = 0
    RULE_obj = 1
    RULE_pair = 2
    RULE_key = 3
    RULE_array = 4
    RULE_value = 5

    ruleNames =  [ "json", "obj", "pair", "key", "array", "value" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    STRING=7
    NUMBER=8
    TRUE=9
    FALSE=10
    NULL=11
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
            self.state = 12
            self.value()
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
            self.state = 27
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,1,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 14
                self.match(JsonParser.T__0)
                self.state = 15
                self.pair()
                self.state = 20
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 16
                    self.match(JsonParser.T__1)
                    self.state = 17
                    self.pair()
                    self.state = 22
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 23
                self.match(JsonParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 25
                self.match(JsonParser.T__0)
                self.state = 26
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

        def key(self):
            return self.getTypedRuleContext(JsonParser.KeyContext,0)


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
            self.state = 29
            self.key()
            self.state = 30
            self.match(JsonParser.T__3)
            self.state = 31
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
            return self.getToken(JsonParser.STRING, 0)

        def getRuleIndex(self):
            return JsonParser.RULE_key

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

        localctx = JsonParser.KeyContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_key)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 33
            self.match(JsonParser.STRING)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ArrayContext(ParserRuleContext):
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
            return JsonParser.RULE_array

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterArray" ):
                listener.enterArray(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitArray" ):
                listener.exitArray(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitArray" ):
                return visitor.visitArray(self)
            else:
                return visitor.visitChildren(self)




    def array(self):

        localctx = JsonParser.ArrayContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_array)
        self._la = 0 # Token type
        try:
            self.state = 48
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,3,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 35
                self.match(JsonParser.T__4)
                self.state = 36
                self.value()
                self.state = 41
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==2:
                    self.state = 37
                    self.match(JsonParser.T__1)
                    self.state = 38
                    self.value()
                    self.state = 43
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                self.state = 44
                self.match(JsonParser.T__5)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 46
                self.match(JsonParser.T__4)
                self.state = 47
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


        def array(self):
            return self.getTypedRuleContext(JsonParser.ArrayContext,0)


        def TRUE(self):
            return self.getToken(JsonParser.TRUE, 0)

        def FALSE(self):
            return self.getToken(JsonParser.FALSE, 0)

        def NULL(self):
            return self.getToken(JsonParser.NULL, 0)

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
        self.enterRule(localctx, 10, self.RULE_value)
        try:
            self.state = 57
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [7]:
                self.enterOuterAlt(localctx, 1)
                self.state = 50
                self.match(JsonParser.STRING)
                pass
            elif token in [8]:
                self.enterOuterAlt(localctx, 2)
                self.state = 51
                self.match(JsonParser.NUMBER)
                pass
            elif token in [1]:
                self.enterOuterAlt(localctx, 3)
                self.state = 52
                self.obj()
                pass
            elif token in [5]:
                self.enterOuterAlt(localctx, 4)
                self.state = 53
                self.array()
                pass
            elif token in [9]:
                self.enterOuterAlt(localctx, 5)
                self.state = 54
                self.match(JsonParser.TRUE)
                pass
            elif token in [10]:
                self.enterOuterAlt(localctx, 6)
                self.state = 55
                self.match(JsonParser.FALSE)
                pass
            elif token in [11]:
                self.enterOuterAlt(localctx, 7)
                self.state = 56
                self.match(JsonParser.NULL)
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






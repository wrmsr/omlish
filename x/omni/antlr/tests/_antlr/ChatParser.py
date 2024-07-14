# flake8: noqa
# type: ignore
# Generated from Chat.g4 by ANTLR 4.8
# encoding: utf-8
from ...._vendor.antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\20")
        buf.write("M\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b")
        buf.write("\t\b\4\t\t\t\4\n\t\n\3\2\6\2\26\n\2\r\2\16\2\27\3\2\3")
        buf.write("\2\3\3\3\3\3\3\3\3\5\3 \n\3\3\3\3\3\3\4\3\4\3\4\3\5\3")
        buf.write("\5\3\5\3\5\3\6\3\6\3\6\3\6\3\6\3\6\6\6\61\n\6\r\6\16\6")
        buf.write("\62\3\7\3\7\5\7\67\n\7\3\7\3\7\3\7\5\7<\n\7\3\7\5\7?\n")
        buf.write("\7\3\b\3\b\3\b\3\t\3\t\3\t\3\t\3\t\3\t\3\n\3\n\3\n\3\n")
        buf.write("\2\2\13\2\4\6\b\n\f\16\20\22\2\3\3\2\t\n\2N\2\25\3\2\2")
        buf.write("\2\4\37\3\2\2\2\6#\3\2\2\2\b&\3\2\2\2\n\60\3\2\2\2\f>")
        buf.write("\3\2\2\2\16@\3\2\2\2\20C\3\2\2\2\22I\3\2\2\2\24\26\5\4")
        buf.write("\3\2\25\24\3\2\2\2\26\27\3\2\2\2\27\25\3\2\2\2\27\30\3")
        buf.write("\2\2\2\30\31\3\2\2\2\31\32\7\2\2\3\32\3\3\2\2\2\33\34")
        buf.write("\5\6\4\2\34\35\5\b\5\2\35\36\5\n\6\2\36 \3\2\2\2\37\33")
        buf.write("\3\2\2\2\37 \3\2\2\2 !\3\2\2\2!\"\7\r\2\2\"\5\3\2\2\2")
        buf.write("#$\7\13\2\2$%\7\f\2\2%\7\3\2\2\2&\'\t\2\2\2\'(\7\3\2\2")
        buf.write("()\7\f\2\2)\t\3\2\2\2*\61\5\f\7\2+\61\5\16\b\2,\61\5\20")
        buf.write("\t\2-\61\5\22\n\2.\61\7\13\2\2/\61\7\f\2\2\60*\3\2\2\2")
        buf.write("\60+\3\2\2\2\60,\3\2\2\2\60-\3\2\2\2\60.\3\2\2\2\60/\3")
        buf.write("\2\2\2\61\62\3\2\2\2\62\60\3\2\2\2\62\63\3\2\2\2\63\13")
        buf.write("\3\2\2\2\64\66\7\3\2\2\65\67\7\4\2\2\66\65\3\2\2\2\66")
        buf.write("\67\3\2\2\2\678\3\2\2\28?\7\5\2\29;\7\3\2\2:<\7\4\2\2")
        buf.write(";:\3\2\2\2;<\3\2\2\2<=\3\2\2\2=?\7\6\2\2>\64\3\2\2\2>")
        buf.write("9\3\2\2\2?\r\3\2\2\2@A\7\16\2\2AB\7\16\2\2B\17\3\2\2\2")
        buf.write("CD\7\7\2\2DE\7\13\2\2EF\7\7\2\2FG\5\n\6\2GH\7\7\2\2H\21")
        buf.write("\3\2\2\2IJ\7\b\2\2JK\7\13\2\2K\23\3\2\2\2\t\27\37\60\62")
        buf.write("\66;>")
        return buf.getvalue()


class ChatParser ( Parser ):

    grammarFileName = "Chat.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "':'", "'-'", "')'", "'('", "'/'", "'@'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "SAYS", "SHOUTS", 
                      "WORD", "WHITESPACE", "NEWLINE", "TEXT", "BLOCK_COMMENT", 
                      "COMMENT" ]

    RULE_chat = 0
    RULE_line = 1
    RULE_name = 2
    RULE_command = 3
    RULE_message = 4
    RULE_emoticon = 5
    RULE_link = 6
    RULE_color = 7
    RULE_mention = 8

    ruleNames =  [ "chat", "line", "name", "command", "message", "emoticon", 
                   "link", "color", "mention" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    SAYS=7
    SHOUTS=8
    WORD=9
    WHITESPACE=10
    NEWLINE=11
    TEXT=12
    BLOCK_COMMENT=13
    COMMENT=14

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.8")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class ChatContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(ChatParser.EOF, 0)

        def line(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ChatParser.LineContext)
            else:
                return self.getTypedRuleContext(ChatParser.LineContext,i)


        def getRuleIndex(self):
            return ChatParser.RULE_chat

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterChat" ):
                listener.enterChat(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitChat" ):
                listener.exitChat(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitChat" ):
                return visitor.visitChat(self)
            else:
                return visitor.visitChildren(self)




    def chat(self):

        localctx = ChatParser.ChatContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_chat)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 19 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 18
                self.line()
                self.state = 21 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==ChatParser.WORD or _la==ChatParser.NEWLINE):
                    break

            self.state = 23
            self.match(ChatParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LineContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NEWLINE(self):
            return self.getToken(ChatParser.NEWLINE, 0)

        def name(self):
            return self.getTypedRuleContext(ChatParser.NameContext,0)


        def command(self):
            return self.getTypedRuleContext(ChatParser.CommandContext,0)


        def message(self):
            return self.getTypedRuleContext(ChatParser.MessageContext,0)


        def getRuleIndex(self):
            return ChatParser.RULE_line

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLine" ):
                listener.enterLine(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLine" ):
                listener.exitLine(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLine" ):
                return visitor.visitLine(self)
            else:
                return visitor.visitChildren(self)




    def line(self):

        localctx = ChatParser.LineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_line)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 29
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==ChatParser.WORD:
                self.state = 25
                self.name()
                self.state = 26
                self.command()
                self.state = 27
                self.message()


            self.state = 31
            self.match(ChatParser.NEWLINE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class NameContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(ChatParser.WORD, 0)

        def WHITESPACE(self):
            return self.getToken(ChatParser.WHITESPACE, 0)

        def getRuleIndex(self):
            return ChatParser.RULE_name

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterName" ):
                listener.enterName(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitName" ):
                listener.exitName(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitName" ):
                return visitor.visitName(self)
            else:
                return visitor.visitChildren(self)




    def name(self):

        localctx = ChatParser.NameContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_name)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 33
            self.match(ChatParser.WORD)
            self.state = 34
            self.match(ChatParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class CommandContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WHITESPACE(self):
            return self.getToken(ChatParser.WHITESPACE, 0)

        def SAYS(self):
            return self.getToken(ChatParser.SAYS, 0)

        def SHOUTS(self):
            return self.getToken(ChatParser.SHOUTS, 0)

        def getRuleIndex(self):
            return ChatParser.RULE_command

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterCommand" ):
                listener.enterCommand(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitCommand" ):
                listener.exitCommand(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCommand" ):
                return visitor.visitCommand(self)
            else:
                return visitor.visitChildren(self)




    def command(self):

        localctx = ChatParser.CommandContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_command)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 36
            _la = self._input.LA(1)
            if not(_la==ChatParser.SAYS or _la==ChatParser.SHOUTS):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
            self.state = 37
            self.match(ChatParser.T__0)
            self.state = 38
            self.match(ChatParser.WHITESPACE)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MessageContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def emoticon(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ChatParser.EmoticonContext)
            else:
                return self.getTypedRuleContext(ChatParser.EmoticonContext,i)


        def link(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ChatParser.LinkContext)
            else:
                return self.getTypedRuleContext(ChatParser.LinkContext,i)


        def color(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ChatParser.ColorContext)
            else:
                return self.getTypedRuleContext(ChatParser.ColorContext,i)


        def mention(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(ChatParser.MentionContext)
            else:
                return self.getTypedRuleContext(ChatParser.MentionContext,i)


        def WORD(self, i:int=None):
            if i is None:
                return self.getTokens(ChatParser.WORD)
            else:
                return self.getToken(ChatParser.WORD, i)

        def WHITESPACE(self, i:int=None):
            if i is None:
                return self.getTokens(ChatParser.WHITESPACE)
            else:
                return self.getToken(ChatParser.WHITESPACE, i)

        def getRuleIndex(self):
            return ChatParser.RULE_message

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMessage" ):
                listener.enterMessage(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMessage" ):
                listener.exitMessage(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMessage" ):
                return visitor.visitMessage(self)
            else:
                return visitor.visitChildren(self)




    def message(self):

        localctx = ChatParser.MessageContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_message)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 46 
            self._errHandler.sync(self)
            _alt = 1
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt == 1:
                    self.state = 46
                    self._errHandler.sync(self)
                    token = self._input.LA(1)
                    if token in [ChatParser.T__0]:
                        self.state = 40
                        self.emoticon()
                        pass
                    elif token in [ChatParser.TEXT]:
                        self.state = 41
                        self.link()
                        pass
                    elif token in [ChatParser.T__4]:
                        self.state = 42
                        self.color()
                        pass
                    elif token in [ChatParser.T__5]:
                        self.state = 43
                        self.mention()
                        pass
                    elif token in [ChatParser.WORD]:
                        self.state = 44
                        self.match(ChatParser.WORD)
                        pass
                    elif token in [ChatParser.WHITESPACE]:
                        self.state = 45
                        self.match(ChatParser.WHITESPACE)
                        pass
                    else:
                        raise NoViableAltException(self)


                else:
                    raise NoViableAltException(self)
                self.state = 48 
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,3,self._ctx)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class EmoticonContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return ChatParser.RULE_emoticon

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterEmoticon" ):
                listener.enterEmoticon(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitEmoticon" ):
                listener.exitEmoticon(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEmoticon" ):
                return visitor.visitEmoticon(self)
            else:
                return visitor.visitChildren(self)




    def emoticon(self):

        localctx = ChatParser.EmoticonContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_emoticon)
        self._la = 0 # Token type
        try:
            self.state = 60
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,6,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 50
                self.match(ChatParser.T__0)
                self.state = 52
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ChatParser.T__1:
                    self.state = 51
                    self.match(ChatParser.T__1)


                self.state = 54
                self.match(ChatParser.T__2)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 55
                self.match(ChatParser.T__0)
                self.state = 57
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==ChatParser.T__1:
                    self.state = 56
                    self.match(ChatParser.T__1)


                self.state = 59
                self.match(ChatParser.T__3)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LinkContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def TEXT(self, i:int=None):
            if i is None:
                return self.getTokens(ChatParser.TEXT)
            else:
                return self.getToken(ChatParser.TEXT, i)

        def getRuleIndex(self):
            return ChatParser.RULE_link

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLink" ):
                listener.enterLink(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLink" ):
                listener.exitLink(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitLink" ):
                return visitor.visitLink(self)
            else:
                return visitor.visitChildren(self)




    def link(self):

        localctx = ChatParser.LinkContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_link)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 62
            self.match(ChatParser.TEXT)
            self.state = 63
            self.match(ChatParser.TEXT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ColorContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(ChatParser.WORD, 0)

        def message(self):
            return self.getTypedRuleContext(ChatParser.MessageContext,0)


        def getRuleIndex(self):
            return ChatParser.RULE_color

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterColor" ):
                listener.enterColor(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitColor" ):
                listener.exitColor(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitColor" ):
                return visitor.visitColor(self)
            else:
                return visitor.visitChildren(self)




    def color(self):

        localctx = ChatParser.ColorContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_color)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 65
            self.match(ChatParser.T__4)
            self.state = 66
            self.match(ChatParser.WORD)
            self.state = 67
            self.match(ChatParser.T__4)
            self.state = 68
            self.message()
            self.state = 69
            self.match(ChatParser.T__4)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class MentionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def WORD(self):
            return self.getToken(ChatParser.WORD, 0)

        def getRuleIndex(self):
            return ChatParser.RULE_mention

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterMention" ):
                listener.enterMention(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitMention" ):
                listener.exitMention(self)

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMention" ):
                return visitor.visitMention(self)
            else:
                return visitor.visitChildren(self)




    def mention(self):

        localctx = ChatParser.MentionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_mention)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 71
            self.match(ChatParser.T__5)
            self.state = 72
            self.match(ChatParser.WORD)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx

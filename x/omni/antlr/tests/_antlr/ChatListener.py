# flake8: noqa
# type: ignore
# Generated from Chat.g4 by ANTLR 4.8
from ...._vendor.antlr4 import *
if __name__ is not None and "." in __name__:
    from .ChatParser import ChatParser
else:
    from ChatParser import ChatParser

# This class defines a complete listener for a parse tree produced by ChatParser.
class ChatListener(ParseTreeListener):

    # Enter a parse tree produced by ChatParser#chat.
    def enterChat(self, ctx:ChatParser.ChatContext):
        pass

    # Exit a parse tree produced by ChatParser#chat.
    def exitChat(self, ctx:ChatParser.ChatContext):
        pass


    # Enter a parse tree produced by ChatParser#line.
    def enterLine(self, ctx:ChatParser.LineContext):
        pass

    # Exit a parse tree produced by ChatParser#line.
    def exitLine(self, ctx:ChatParser.LineContext):
        pass


    # Enter a parse tree produced by ChatParser#name.
    def enterName(self, ctx:ChatParser.NameContext):
        pass

    # Exit a parse tree produced by ChatParser#name.
    def exitName(self, ctx:ChatParser.NameContext):
        pass


    # Enter a parse tree produced by ChatParser#command.
    def enterCommand(self, ctx:ChatParser.CommandContext):
        pass

    # Exit a parse tree produced by ChatParser#command.
    def exitCommand(self, ctx:ChatParser.CommandContext):
        pass


    # Enter a parse tree produced by ChatParser#message.
    def enterMessage(self, ctx:ChatParser.MessageContext):
        pass

    # Exit a parse tree produced by ChatParser#message.
    def exitMessage(self, ctx:ChatParser.MessageContext):
        pass


    # Enter a parse tree produced by ChatParser#emoticon.
    def enterEmoticon(self, ctx:ChatParser.EmoticonContext):
        pass

    # Exit a parse tree produced by ChatParser#emoticon.
    def exitEmoticon(self, ctx:ChatParser.EmoticonContext):
        pass


    # Enter a parse tree produced by ChatParser#link.
    def enterLink(self, ctx:ChatParser.LinkContext):
        pass

    # Exit a parse tree produced by ChatParser#link.
    def exitLink(self, ctx:ChatParser.LinkContext):
        pass


    # Enter a parse tree produced by ChatParser#color.
    def enterColor(self, ctx:ChatParser.ColorContext):
        pass

    # Exit a parse tree produced by ChatParser#color.
    def exitColor(self, ctx:ChatParser.ColorContext):
        pass


    # Enter a parse tree produced by ChatParser#mention.
    def enterMention(self, ctx:ChatParser.MentionContext):
        pass

    # Exit a parse tree produced by ChatParser#mention.
    def exitMention(self, ctx:ChatParser.MentionContext):
        pass



del ChatParser

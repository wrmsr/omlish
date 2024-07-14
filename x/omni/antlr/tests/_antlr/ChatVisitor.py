# flake8: noqa
# type: ignore
# Generated from Chat.g4 by ANTLR 4.8
from ...._vendor.antlr4 import *
if __name__ is not None and "." in __name__:
    from .ChatParser import ChatParser
else:
    from ChatParser import ChatParser

# This class defines a complete generic visitor for a parse tree produced by ChatParser.

class ChatVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by ChatParser#chat.
    def visitChat(self, ctx:ChatParser.ChatContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ChatParser#line.
    def visitLine(self, ctx:ChatParser.LineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ChatParser#name.
    def visitName(self, ctx:ChatParser.NameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ChatParser#command.
    def visitCommand(self, ctx:ChatParser.CommandContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ChatParser#message.
    def visitMessage(self, ctx:ChatParser.MessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ChatParser#emoticon.
    def visitEmoticon(self, ctx:ChatParser.EmoticonContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ChatParser#link.
    def visitLink(self, ctx:ChatParser.LinkContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ChatParser#color.
    def visitColor(self, ctx:ChatParser.ColorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by ChatParser#mention.
    def visitMention(self, ctx:ChatParser.MentionContext):
        return self.visitChildren(ctx)



del ChatParser

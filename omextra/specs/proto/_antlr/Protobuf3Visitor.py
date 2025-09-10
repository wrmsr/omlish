# type: ignore
# ruff: noqa
# flake8: noqa
# @omlish-generated
# Generated from Protobuf3.g4 by ANTLR 4.13.2
from ....text.antlr._runtime._all import *
if "." in __name__:
    from .Protobuf3Parser import Protobuf3Parser
else:
    from Protobuf3Parser import Protobuf3Parser

# This class defines a complete generic visitor for a parse tree produced by Protobuf3Parser.

class Protobuf3Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by Protobuf3Parser#proto.
    def visitProto(self, ctx:Protobuf3Parser.ProtoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#syntax.
    def visitSyntax(self, ctx:Protobuf3Parser.SyntaxContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#syntaxExtra.
    def visitSyntaxExtra(self, ctx:Protobuf3Parser.SyntaxExtraContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#importStmt.
    def visitImportStmt(self, ctx:Protobuf3Parser.ImportStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#packageStmt.
    def visitPackageStmt(self, ctx:Protobuf3Parser.PackageStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#option.
    def visitOption(self, ctx:Protobuf3Parser.OptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#optionName.
    def visitOptionName(self, ctx:Protobuf3Parser.OptionNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#optionBody.
    def visitOptionBody(self, ctx:Protobuf3Parser.OptionBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#optionBodyVariable.
    def visitOptionBodyVariable(self, ctx:Protobuf3Parser.OptionBodyVariableContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#topLevelDef.
    def visitTopLevelDef(self, ctx:Protobuf3Parser.TopLevelDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#message.
    def visitMessage(self, ctx:Protobuf3Parser.MessageContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#messageBody.
    def visitMessageBody(self, ctx:Protobuf3Parser.MessageBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#messageBodyContent.
    def visitMessageBodyContent(self, ctx:Protobuf3Parser.MessageBodyContentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#enumDef.
    def visitEnumDef(self, ctx:Protobuf3Parser.EnumDefContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#enumBody.
    def visitEnumBody(self, ctx:Protobuf3Parser.EnumBodyContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#enumField.
    def visitEnumField(self, ctx:Protobuf3Parser.EnumFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#enumValueOption.
    def visitEnumValueOption(self, ctx:Protobuf3Parser.EnumValueOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#extend.
    def visitExtend(self, ctx:Protobuf3Parser.ExtendContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#service.
    def visitService(self, ctx:Protobuf3Parser.ServiceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#rpc.
    def visitRpc(self, ctx:Protobuf3Parser.RpcContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#reserved.
    def visitReserved(self, ctx:Protobuf3Parser.ReservedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#ranges.
    def visitRanges(self, ctx:Protobuf3Parser.RangesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#rangeRule.
    def visitRangeRule(self, ctx:Protobuf3Parser.RangeRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#fieldNames.
    def visitFieldNames(self, ctx:Protobuf3Parser.FieldNamesContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#typeRule.
    def visitTypeRule(self, ctx:Protobuf3Parser.TypeRuleContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#simpleType.
    def visitSimpleType(self, ctx:Protobuf3Parser.SimpleTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#fieldNumber.
    def visitFieldNumber(self, ctx:Protobuf3Parser.FieldNumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#field.
    def visitField(self, ctx:Protobuf3Parser.FieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#fieldOptions.
    def visitFieldOptions(self, ctx:Protobuf3Parser.FieldOptionsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#fieldOption.
    def visitFieldOption(self, ctx:Protobuf3Parser.FieldOptionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#oneof.
    def visitOneof(self, ctx:Protobuf3Parser.OneofContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#oneofField.
    def visitOneofField(self, ctx:Protobuf3Parser.OneofFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#mapField.
    def visitMapField(self, ctx:Protobuf3Parser.MapFieldContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#keyType.
    def visitKeyType(self, ctx:Protobuf3Parser.KeyTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#reservedWord.
    def visitReservedWord(self, ctx:Protobuf3Parser.ReservedWordContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#fullIdent.
    def visitFullIdent(self, ctx:Protobuf3Parser.FullIdentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#messageName.
    def visitMessageName(self, ctx:Protobuf3Parser.MessageNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#enumName.
    def visitEnumName(self, ctx:Protobuf3Parser.EnumNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#messageOrEnumName.
    def visitMessageOrEnumName(self, ctx:Protobuf3Parser.MessageOrEnumNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#fieldName.
    def visitFieldName(self, ctx:Protobuf3Parser.FieldNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#oneofName.
    def visitOneofName(self, ctx:Protobuf3Parser.OneofNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#mapName.
    def visitMapName(self, ctx:Protobuf3Parser.MapNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#serviceName.
    def visitServiceName(self, ctx:Protobuf3Parser.ServiceNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#rpcName.
    def visitRpcName(self, ctx:Protobuf3Parser.RpcNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#messageType.
    def visitMessageType(self, ctx:Protobuf3Parser.MessageTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#messageOrEnumType.
    def visitMessageOrEnumType(self, ctx:Protobuf3Parser.MessageOrEnumTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#emptyStmt.
    def visitEmptyStmt(self, ctx:Protobuf3Parser.EmptyStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by Protobuf3Parser#constant.
    def visitConstant(self, ctx:Protobuf3Parser.ConstantContext):
        return self.visitChildren(ctx)



del Protobuf3Parser
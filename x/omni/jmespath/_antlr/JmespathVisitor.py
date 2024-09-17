# flake8: noqa
# type: ignore
# Generated from Jmespath.g4 by ANTLR 4.8
from ..._vendor.antlr4 import *
if __name__ is not None and "." in __name__:
    from .JmespathParser import JmespathParser
else:
    from JmespathParser import JmespathParser

# This class defines a complete generic visitor for a parse tree produced by JmespathParser.

class JmespathVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by JmespathParser#singleExpression.
    def visitSingleExpression(self, ctx:JmespathParser.SingleExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#pipeExpression.
    def visitPipeExpression(self, ctx:JmespathParser.PipeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#parameterExpression.
    def visitParameterExpression(self, ctx:JmespathParser.ParameterExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#identifierExpression.
    def visitIdentifierExpression(self, ctx:JmespathParser.IdentifierExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#notExpression.
    def visitNotExpression(self, ctx:JmespathParser.NotExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#rawStringExpression.
    def visitRawStringExpression(self, ctx:JmespathParser.RawStringExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#comparisonExpression.
    def visitComparisonExpression(self, ctx:JmespathParser.ComparisonExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#parenExpression.
    def visitParenExpression(self, ctx:JmespathParser.ParenExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#bracketExpression.
    def visitBracketExpression(self, ctx:JmespathParser.BracketExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#orExpression.
    def visitOrExpression(self, ctx:JmespathParser.OrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#currentNodeExpression.
    def visitCurrentNodeExpression(self, ctx:JmespathParser.CurrentNodeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#chainExpression.
    def visitChainExpression(self, ctx:JmespathParser.ChainExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#andExpression.
    def visitAndExpression(self, ctx:JmespathParser.AndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#multiSelectHashExpression.
    def visitMultiSelectHashExpression(self, ctx:JmespathParser.MultiSelectHashExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#wildcardExpression.
    def visitWildcardExpression(self, ctx:JmespathParser.WildcardExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#functionCallExpression.
    def visitFunctionCallExpression(self, ctx:JmespathParser.FunctionCallExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#multiSelectListExpression.
    def visitMultiSelectListExpression(self, ctx:JmespathParser.MultiSelectListExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#bracketedExpression.
    def visitBracketedExpression(self, ctx:JmespathParser.BracketedExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#literalExpression.
    def visitLiteralExpression(self, ctx:JmespathParser.LiteralExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#chainedExpression.
    def visitChainedExpression(self, ctx:JmespathParser.ChainedExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#wildcard.
    def visitWildcard(self, ctx:JmespathParser.WildcardContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#bracketIndex.
    def visitBracketIndex(self, ctx:JmespathParser.BracketIndexContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#bracketStar.
    def visitBracketStar(self, ctx:JmespathParser.BracketStarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#bracketSlice.
    def visitBracketSlice(self, ctx:JmespathParser.BracketSliceContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#bracketFlatten.
    def visitBracketFlatten(self, ctx:JmespathParser.BracketFlattenContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#select.
    def visitSelect(self, ctx:JmespathParser.SelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#multiSelectList.
    def visitMultiSelectList(self, ctx:JmespathParser.MultiSelectListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#multiSelectHash.
    def visitMultiSelectHash(self, ctx:JmespathParser.MultiSelectHashContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#keyvalExpr.
    def visitKeyvalExpr(self, ctx:JmespathParser.KeyvalExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#sliceNode.
    def visitSliceNode(self, ctx:JmespathParser.SliceNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#nameParameter.
    def visitNameParameter(self, ctx:JmespathParser.NameParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#numberParameter.
    def visitNumberParameter(self, ctx:JmespathParser.NumberParameterContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#functionExpression.
    def visitFunctionExpression(self, ctx:JmespathParser.FunctionExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#functionArg.
    def visitFunctionArg(self, ctx:JmespathParser.FunctionArgContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#currentNode.
    def visitCurrentNode(self, ctx:JmespathParser.CurrentNodeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#expressionType.
    def visitExpressionType(self, ctx:JmespathParser.ExpressionTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#literal.
    def visitLiteral(self, ctx:JmespathParser.LiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#identifier.
    def visitIdentifier(self, ctx:JmespathParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#jsonObject.
    def visitJsonObject(self, ctx:JmespathParser.JsonObjectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#jsonObjectPair.
    def visitJsonObjectPair(self, ctx:JmespathParser.JsonObjectPairContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#jsonArray.
    def visitJsonArray(self, ctx:JmespathParser.JsonArrayContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#jsonStringValue.
    def visitJsonStringValue(self, ctx:JmespathParser.JsonStringValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#jsonNumberValue.
    def visitJsonNumberValue(self, ctx:JmespathParser.JsonNumberValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#jsonObjectValue.
    def visitJsonObjectValue(self, ctx:JmespathParser.JsonObjectValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#jsonArrayValue.
    def visitJsonArrayValue(self, ctx:JmespathParser.JsonArrayValueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by JmespathParser#jsonConstantValue.
    def visitJsonConstantValue(self, ctx:JmespathParser.JsonConstantValueContext):
        return self.visitChildren(ctx)



del JmespathParser

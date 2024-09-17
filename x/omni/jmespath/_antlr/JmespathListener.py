# flake8: noqa
# type: ignore
# Generated from Jmespath.g4 by ANTLR 4.8
from ..._vendor.antlr4 import *
if __name__ is not None and "." in __name__:
    from .JmespathParser import JmespathParser
else:
    from JmespathParser import JmespathParser

# This class defines a complete listener for a parse tree produced by JmespathParser.
class JmespathListener(ParseTreeListener):

    # Enter a parse tree produced by JmespathParser#singleExpression.
    def enterSingleExpression(self, ctx:JmespathParser.SingleExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#singleExpression.
    def exitSingleExpression(self, ctx:JmespathParser.SingleExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#pipeExpression.
    def enterPipeExpression(self, ctx:JmespathParser.PipeExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#pipeExpression.
    def exitPipeExpression(self, ctx:JmespathParser.PipeExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#parameterExpression.
    def enterParameterExpression(self, ctx:JmespathParser.ParameterExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#parameterExpression.
    def exitParameterExpression(self, ctx:JmespathParser.ParameterExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#identifierExpression.
    def enterIdentifierExpression(self, ctx:JmespathParser.IdentifierExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#identifierExpression.
    def exitIdentifierExpression(self, ctx:JmespathParser.IdentifierExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#notExpression.
    def enterNotExpression(self, ctx:JmespathParser.NotExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#notExpression.
    def exitNotExpression(self, ctx:JmespathParser.NotExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#rawStringExpression.
    def enterRawStringExpression(self, ctx:JmespathParser.RawStringExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#rawStringExpression.
    def exitRawStringExpression(self, ctx:JmespathParser.RawStringExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#comparisonExpression.
    def enterComparisonExpression(self, ctx:JmespathParser.ComparisonExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#comparisonExpression.
    def exitComparisonExpression(self, ctx:JmespathParser.ComparisonExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#parenExpression.
    def enterParenExpression(self, ctx:JmespathParser.ParenExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#parenExpression.
    def exitParenExpression(self, ctx:JmespathParser.ParenExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#bracketExpression.
    def enterBracketExpression(self, ctx:JmespathParser.BracketExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#bracketExpression.
    def exitBracketExpression(self, ctx:JmespathParser.BracketExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#orExpression.
    def enterOrExpression(self, ctx:JmespathParser.OrExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#orExpression.
    def exitOrExpression(self, ctx:JmespathParser.OrExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#currentNodeExpression.
    def enterCurrentNodeExpression(self, ctx:JmespathParser.CurrentNodeExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#currentNodeExpression.
    def exitCurrentNodeExpression(self, ctx:JmespathParser.CurrentNodeExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#chainExpression.
    def enterChainExpression(self, ctx:JmespathParser.ChainExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#chainExpression.
    def exitChainExpression(self, ctx:JmespathParser.ChainExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#andExpression.
    def enterAndExpression(self, ctx:JmespathParser.AndExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#andExpression.
    def exitAndExpression(self, ctx:JmespathParser.AndExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#multiSelectHashExpression.
    def enterMultiSelectHashExpression(self, ctx:JmespathParser.MultiSelectHashExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#multiSelectHashExpression.
    def exitMultiSelectHashExpression(self, ctx:JmespathParser.MultiSelectHashExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#wildcardExpression.
    def enterWildcardExpression(self, ctx:JmespathParser.WildcardExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#wildcardExpression.
    def exitWildcardExpression(self, ctx:JmespathParser.WildcardExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#functionCallExpression.
    def enterFunctionCallExpression(self, ctx:JmespathParser.FunctionCallExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#functionCallExpression.
    def exitFunctionCallExpression(self, ctx:JmespathParser.FunctionCallExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#multiSelectListExpression.
    def enterMultiSelectListExpression(self, ctx:JmespathParser.MultiSelectListExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#multiSelectListExpression.
    def exitMultiSelectListExpression(self, ctx:JmespathParser.MultiSelectListExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#bracketedExpression.
    def enterBracketedExpression(self, ctx:JmespathParser.BracketedExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#bracketedExpression.
    def exitBracketedExpression(self, ctx:JmespathParser.BracketedExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#literalExpression.
    def enterLiteralExpression(self, ctx:JmespathParser.LiteralExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#literalExpression.
    def exitLiteralExpression(self, ctx:JmespathParser.LiteralExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#chainedExpression.
    def enterChainedExpression(self, ctx:JmespathParser.ChainedExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#chainedExpression.
    def exitChainedExpression(self, ctx:JmespathParser.ChainedExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#wildcard.
    def enterWildcard(self, ctx:JmespathParser.WildcardContext):
        pass

    # Exit a parse tree produced by JmespathParser#wildcard.
    def exitWildcard(self, ctx:JmespathParser.WildcardContext):
        pass


    # Enter a parse tree produced by JmespathParser#bracketIndex.
    def enterBracketIndex(self, ctx:JmespathParser.BracketIndexContext):
        pass

    # Exit a parse tree produced by JmespathParser#bracketIndex.
    def exitBracketIndex(self, ctx:JmespathParser.BracketIndexContext):
        pass


    # Enter a parse tree produced by JmespathParser#bracketStar.
    def enterBracketStar(self, ctx:JmespathParser.BracketStarContext):
        pass

    # Exit a parse tree produced by JmespathParser#bracketStar.
    def exitBracketStar(self, ctx:JmespathParser.BracketStarContext):
        pass


    # Enter a parse tree produced by JmespathParser#bracketSlice.
    def enterBracketSlice(self, ctx:JmespathParser.BracketSliceContext):
        pass

    # Exit a parse tree produced by JmespathParser#bracketSlice.
    def exitBracketSlice(self, ctx:JmespathParser.BracketSliceContext):
        pass


    # Enter a parse tree produced by JmespathParser#bracketFlatten.
    def enterBracketFlatten(self, ctx:JmespathParser.BracketFlattenContext):
        pass

    # Exit a parse tree produced by JmespathParser#bracketFlatten.
    def exitBracketFlatten(self, ctx:JmespathParser.BracketFlattenContext):
        pass


    # Enter a parse tree produced by JmespathParser#select.
    def enterSelect(self, ctx:JmespathParser.SelectContext):
        pass

    # Exit a parse tree produced by JmespathParser#select.
    def exitSelect(self, ctx:JmespathParser.SelectContext):
        pass


    # Enter a parse tree produced by JmespathParser#multiSelectList.
    def enterMultiSelectList(self, ctx:JmespathParser.MultiSelectListContext):
        pass

    # Exit a parse tree produced by JmespathParser#multiSelectList.
    def exitMultiSelectList(self, ctx:JmespathParser.MultiSelectListContext):
        pass


    # Enter a parse tree produced by JmespathParser#multiSelectHash.
    def enterMultiSelectHash(self, ctx:JmespathParser.MultiSelectHashContext):
        pass

    # Exit a parse tree produced by JmespathParser#multiSelectHash.
    def exitMultiSelectHash(self, ctx:JmespathParser.MultiSelectHashContext):
        pass


    # Enter a parse tree produced by JmespathParser#keyvalExpr.
    def enterKeyvalExpr(self, ctx:JmespathParser.KeyvalExprContext):
        pass

    # Exit a parse tree produced by JmespathParser#keyvalExpr.
    def exitKeyvalExpr(self, ctx:JmespathParser.KeyvalExprContext):
        pass


    # Enter a parse tree produced by JmespathParser#sliceNode.
    def enterSliceNode(self, ctx:JmespathParser.SliceNodeContext):
        pass

    # Exit a parse tree produced by JmespathParser#sliceNode.
    def exitSliceNode(self, ctx:JmespathParser.SliceNodeContext):
        pass


    # Enter a parse tree produced by JmespathParser#nameParameter.
    def enterNameParameter(self, ctx:JmespathParser.NameParameterContext):
        pass

    # Exit a parse tree produced by JmespathParser#nameParameter.
    def exitNameParameter(self, ctx:JmespathParser.NameParameterContext):
        pass


    # Enter a parse tree produced by JmespathParser#numberParameter.
    def enterNumberParameter(self, ctx:JmespathParser.NumberParameterContext):
        pass

    # Exit a parse tree produced by JmespathParser#numberParameter.
    def exitNumberParameter(self, ctx:JmespathParser.NumberParameterContext):
        pass


    # Enter a parse tree produced by JmespathParser#functionExpression.
    def enterFunctionExpression(self, ctx:JmespathParser.FunctionExpressionContext):
        pass

    # Exit a parse tree produced by JmespathParser#functionExpression.
    def exitFunctionExpression(self, ctx:JmespathParser.FunctionExpressionContext):
        pass


    # Enter a parse tree produced by JmespathParser#functionArg.
    def enterFunctionArg(self, ctx:JmespathParser.FunctionArgContext):
        pass

    # Exit a parse tree produced by JmespathParser#functionArg.
    def exitFunctionArg(self, ctx:JmespathParser.FunctionArgContext):
        pass


    # Enter a parse tree produced by JmespathParser#currentNode.
    def enterCurrentNode(self, ctx:JmespathParser.CurrentNodeContext):
        pass

    # Exit a parse tree produced by JmespathParser#currentNode.
    def exitCurrentNode(self, ctx:JmespathParser.CurrentNodeContext):
        pass


    # Enter a parse tree produced by JmespathParser#expressionType.
    def enterExpressionType(self, ctx:JmespathParser.ExpressionTypeContext):
        pass

    # Exit a parse tree produced by JmespathParser#expressionType.
    def exitExpressionType(self, ctx:JmespathParser.ExpressionTypeContext):
        pass


    # Enter a parse tree produced by JmespathParser#literal.
    def enterLiteral(self, ctx:JmespathParser.LiteralContext):
        pass

    # Exit a parse tree produced by JmespathParser#literal.
    def exitLiteral(self, ctx:JmespathParser.LiteralContext):
        pass


    # Enter a parse tree produced by JmespathParser#identifier.
    def enterIdentifier(self, ctx:JmespathParser.IdentifierContext):
        pass

    # Exit a parse tree produced by JmespathParser#identifier.
    def exitIdentifier(self, ctx:JmespathParser.IdentifierContext):
        pass


    # Enter a parse tree produced by JmespathParser#jsonObject.
    def enterJsonObject(self, ctx:JmespathParser.JsonObjectContext):
        pass

    # Exit a parse tree produced by JmespathParser#jsonObject.
    def exitJsonObject(self, ctx:JmespathParser.JsonObjectContext):
        pass


    # Enter a parse tree produced by JmespathParser#jsonObjectPair.
    def enterJsonObjectPair(self, ctx:JmespathParser.JsonObjectPairContext):
        pass

    # Exit a parse tree produced by JmespathParser#jsonObjectPair.
    def exitJsonObjectPair(self, ctx:JmespathParser.JsonObjectPairContext):
        pass


    # Enter a parse tree produced by JmespathParser#jsonArray.
    def enterJsonArray(self, ctx:JmespathParser.JsonArrayContext):
        pass

    # Exit a parse tree produced by JmespathParser#jsonArray.
    def exitJsonArray(self, ctx:JmespathParser.JsonArrayContext):
        pass


    # Enter a parse tree produced by JmespathParser#jsonStringValue.
    def enterJsonStringValue(self, ctx:JmespathParser.JsonStringValueContext):
        pass

    # Exit a parse tree produced by JmespathParser#jsonStringValue.
    def exitJsonStringValue(self, ctx:JmespathParser.JsonStringValueContext):
        pass


    # Enter a parse tree produced by JmespathParser#jsonNumberValue.
    def enterJsonNumberValue(self, ctx:JmespathParser.JsonNumberValueContext):
        pass

    # Exit a parse tree produced by JmespathParser#jsonNumberValue.
    def exitJsonNumberValue(self, ctx:JmespathParser.JsonNumberValueContext):
        pass


    # Enter a parse tree produced by JmespathParser#jsonObjectValue.
    def enterJsonObjectValue(self, ctx:JmespathParser.JsonObjectValueContext):
        pass

    # Exit a parse tree produced by JmespathParser#jsonObjectValue.
    def exitJsonObjectValue(self, ctx:JmespathParser.JsonObjectValueContext):
        pass


    # Enter a parse tree produced by JmespathParser#jsonArrayValue.
    def enterJsonArrayValue(self, ctx:JmespathParser.JsonArrayValueContext):
        pass

    # Exit a parse tree produced by JmespathParser#jsonArrayValue.
    def exitJsonArrayValue(self, ctx:JmespathParser.JsonArrayValueContext):
        pass


    # Enter a parse tree produced by JmespathParser#jsonConstantValue.
    def enterJsonConstantValue(self, ctx:JmespathParser.JsonConstantValueContext):
        pass

    # Exit a parse tree produced by JmespathParser#jsonConstantValue.
    def exitJsonConstantValue(self, ctx:JmespathParser.JsonConstantValueContext):
        pass



del JmespathParser

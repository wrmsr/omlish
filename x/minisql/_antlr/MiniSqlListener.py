# type: ignore
# ruff: noqa
# flake8: noqa
# Generated from MiniSql.g4 by ANTLR 4.13.2
from omlish.antlr._runtime._all import *
if "." in __name__:
    from .MiniSqlParser import MiniSqlParser
else:
    from MiniSqlParser import MiniSqlParser

# This class defines a complete listener for a parse tree produced by MiniSqlParser.
class MiniSqlListener(ParseTreeListener):

    # Enter a parse tree produced by MiniSqlParser#singleStatement.
    def enterSingleStatement(self, ctx:MiniSqlParser.SingleStatementContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#singleStatement.
    def exitSingleStatement(self, ctx:MiniSqlParser.SingleStatementContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#select.
    def enterSelect(self, ctx:MiniSqlParser.SelectContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#select.
    def exitSelect(self, ctx:MiniSqlParser.SelectContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#cteSelect.
    def enterCteSelect(self, ctx:MiniSqlParser.CteSelectContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#cteSelect.
    def exitCteSelect(self, ctx:MiniSqlParser.CteSelectContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#cte.
    def enterCte(self, ctx:MiniSqlParser.CteContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#cte.
    def exitCte(self, ctx:MiniSqlParser.CteContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#unionSelect.
    def enterUnionSelect(self, ctx:MiniSqlParser.UnionSelectContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#unionSelect.
    def exitUnionSelect(self, ctx:MiniSqlParser.UnionSelectContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#unionItem.
    def enterUnionItem(self, ctx:MiniSqlParser.UnionItemContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#unionItem.
    def exitUnionItem(self, ctx:MiniSqlParser.UnionItemContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#primarySelect.
    def enterPrimarySelect(self, ctx:MiniSqlParser.PrimarySelectContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#primarySelect.
    def exitPrimarySelect(self, ctx:MiniSqlParser.PrimarySelectContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#allSelectItem.
    def enterAllSelectItem(self, ctx:MiniSqlParser.AllSelectItemContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#allSelectItem.
    def exitAllSelectItem(self, ctx:MiniSqlParser.AllSelectItemContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#expressionSelectItem.
    def enterExpressionSelectItem(self, ctx:MiniSqlParser.ExpressionSelectItemContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#expressionSelectItem.
    def exitExpressionSelectItem(self, ctx:MiniSqlParser.ExpressionSelectItemContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#expression.
    def enterExpression(self, ctx:MiniSqlParser.ExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#expression.
    def exitExpression(self, ctx:MiniSqlParser.ExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#binaryBooleanExpression.
    def enterBinaryBooleanExpression(self, ctx:MiniSqlParser.BinaryBooleanExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#binaryBooleanExpression.
    def exitBinaryBooleanExpression(self, ctx:MiniSqlParser.BinaryBooleanExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#predicatedBooleanExpression.
    def enterPredicatedBooleanExpression(self, ctx:MiniSqlParser.PredicatedBooleanExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#predicatedBooleanExpression.
    def exitPredicatedBooleanExpression(self, ctx:MiniSqlParser.PredicatedBooleanExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#unaryBooleanExpression.
    def enterUnaryBooleanExpression(self, ctx:MiniSqlParser.UnaryBooleanExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#unaryBooleanExpression.
    def exitUnaryBooleanExpression(self, ctx:MiniSqlParser.UnaryBooleanExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#castBooleanExpression.
    def enterCastBooleanExpression(self, ctx:MiniSqlParser.CastBooleanExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#castBooleanExpression.
    def exitCastBooleanExpression(self, ctx:MiniSqlParser.CastBooleanExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#cmpPredicate.
    def enterCmpPredicate(self, ctx:MiniSqlParser.CmpPredicateContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#cmpPredicate.
    def exitCmpPredicate(self, ctx:MiniSqlParser.CmpPredicateContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#isNullPredicate.
    def enterIsNullPredicate(self, ctx:MiniSqlParser.IsNullPredicateContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#isNullPredicate.
    def exitIsNullPredicate(self, ctx:MiniSqlParser.IsNullPredicateContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#inListPredicate.
    def enterInListPredicate(self, ctx:MiniSqlParser.InListPredicateContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#inListPredicate.
    def exitInListPredicate(self, ctx:MiniSqlParser.InListPredicateContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#inSelectPredicate.
    def enterInSelectPredicate(self, ctx:MiniSqlParser.InSelectPredicateContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#inSelectPredicate.
    def exitInSelectPredicate(self, ctx:MiniSqlParser.InSelectPredicateContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#likePredicate.
    def enterLikePredicate(self, ctx:MiniSqlParser.LikePredicateContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#likePredicate.
    def exitLikePredicate(self, ctx:MiniSqlParser.LikePredicateContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#primaryValueExpression.
    def enterPrimaryValueExpression(self, ctx:MiniSqlParser.PrimaryValueExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#primaryValueExpression.
    def exitPrimaryValueExpression(self, ctx:MiniSqlParser.PrimaryValueExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#unaryValueExpression.
    def enterUnaryValueExpression(self, ctx:MiniSqlParser.UnaryValueExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#unaryValueExpression.
    def exitUnaryValueExpression(self, ctx:MiniSqlParser.UnaryValueExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#arithValueExpression.
    def enterArithValueExpression(self, ctx:MiniSqlParser.ArithValueExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#arithValueExpression.
    def exitArithValueExpression(self, ctx:MiniSqlParser.ArithValueExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#functionCallExpression.
    def enterFunctionCallExpression(self, ctx:MiniSqlParser.FunctionCallExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#functionCallExpression.
    def exitFunctionCallExpression(self, ctx:MiniSqlParser.FunctionCallExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#starFunctionCallExpression.
    def enterStarFunctionCallExpression(self, ctx:MiniSqlParser.StarFunctionCallExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#starFunctionCallExpression.
    def exitStarFunctionCallExpression(self, ctx:MiniSqlParser.StarFunctionCallExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#caseExpression.
    def enterCaseExpression(self, ctx:MiniSqlParser.CaseExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#caseExpression.
    def exitCaseExpression(self, ctx:MiniSqlParser.CaseExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#selectExpression.
    def enterSelectExpression(self, ctx:MiniSqlParser.SelectExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#selectExpression.
    def exitSelectExpression(self, ctx:MiniSqlParser.SelectExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#parenExpression.
    def enterParenExpression(self, ctx:MiniSqlParser.ParenExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#parenExpression.
    def exitParenExpression(self, ctx:MiniSqlParser.ParenExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#simplePrimaryExpression.
    def enterSimplePrimaryExpression(self, ctx:MiniSqlParser.SimplePrimaryExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#simplePrimaryExpression.
    def exitSimplePrimaryExpression(self, ctx:MiniSqlParser.SimplePrimaryExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#simpleExpression.
    def enterSimpleExpression(self, ctx:MiniSqlParser.SimpleExpressionContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#simpleExpression.
    def exitSimpleExpression(self, ctx:MiniSqlParser.SimpleExpressionContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#caseItem.
    def enterCaseItem(self, ctx:MiniSqlParser.CaseItemContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#caseItem.
    def exitCaseItem(self, ctx:MiniSqlParser.CaseItemContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#over.
    def enterOver(self, ctx:MiniSqlParser.OverContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#over.
    def exitOver(self, ctx:MiniSqlParser.OverContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#sortItem.
    def enterSortItem(self, ctx:MiniSqlParser.SortItemContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#sortItem.
    def exitSortItem(self, ctx:MiniSqlParser.SortItemContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#aliasedRelation.
    def enterAliasedRelation(self, ctx:MiniSqlParser.AliasedRelationContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#aliasedRelation.
    def exitAliasedRelation(self, ctx:MiniSqlParser.AliasedRelationContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#joinRelation.
    def enterJoinRelation(self, ctx:MiniSqlParser.JoinRelationContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#joinRelation.
    def exitJoinRelation(self, ctx:MiniSqlParser.JoinRelationContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#selectRelation.
    def enterSelectRelation(self, ctx:MiniSqlParser.SelectRelationContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#selectRelation.
    def exitSelectRelation(self, ctx:MiniSqlParser.SelectRelationContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#tableRelation.
    def enterTableRelation(self, ctx:MiniSqlParser.TableRelationContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#tableRelation.
    def exitTableRelation(self, ctx:MiniSqlParser.TableRelationContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#parenRelation.
    def enterParenRelation(self, ctx:MiniSqlParser.ParenRelationContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#parenRelation.
    def exitParenRelation(self, ctx:MiniSqlParser.ParenRelationContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#groupBy.
    def enterGroupBy(self, ctx:MiniSqlParser.GroupByContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#groupBy.
    def exitGroupBy(self, ctx:MiniSqlParser.GroupByContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#qualifiedName.
    def enterQualifiedName(self, ctx:MiniSqlParser.QualifiedNameContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#qualifiedName.
    def exitQualifiedName(self, ctx:MiniSqlParser.QualifiedNameContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#identifierList.
    def enterIdentifierList(self, ctx:MiniSqlParser.IdentifierListContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#identifierList.
    def exitIdentifierList(self, ctx:MiniSqlParser.IdentifierListContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#identifier.
    def enterIdentifier(self, ctx:MiniSqlParser.IdentifierContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#identifier.
    def exitIdentifier(self, ctx:MiniSqlParser.IdentifierContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#quotedIdentifier.
    def enterQuotedIdentifier(self, ctx:MiniSqlParser.QuotedIdentifierContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#quotedIdentifier.
    def exitQuotedIdentifier(self, ctx:MiniSqlParser.QuotedIdentifierContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#integerNumber.
    def enterIntegerNumber(self, ctx:MiniSqlParser.IntegerNumberContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#integerNumber.
    def exitIntegerNumber(self, ctx:MiniSqlParser.IntegerNumberContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#decimalNumber.
    def enterDecimalNumber(self, ctx:MiniSqlParser.DecimalNumberContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#decimalNumber.
    def exitDecimalNumber(self, ctx:MiniSqlParser.DecimalNumberContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#floatNumber.
    def enterFloatNumber(self, ctx:MiniSqlParser.FloatNumberContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#floatNumber.
    def exitFloatNumber(self, ctx:MiniSqlParser.FloatNumberContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#string.
    def enterString(self, ctx:MiniSqlParser.StringContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#string.
    def exitString(self, ctx:MiniSqlParser.StringContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#null.
    def enterNull(self, ctx:MiniSqlParser.NullContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#null.
    def exitNull(self, ctx:MiniSqlParser.NullContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#true.
    def enterTrue(self, ctx:MiniSqlParser.TrueContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#true.
    def exitTrue(self, ctx:MiniSqlParser.TrueContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#false.
    def enterFalse(self, ctx:MiniSqlParser.FalseContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#false.
    def exitFalse(self, ctx:MiniSqlParser.FalseContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#setQuantifier.
    def enterSetQuantifier(self, ctx:MiniSqlParser.SetQuantifierContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#setQuantifier.
    def exitSetQuantifier(self, ctx:MiniSqlParser.SetQuantifierContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#joinType.
    def enterJoinType(self, ctx:MiniSqlParser.JoinTypeContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#joinType.
    def exitJoinType(self, ctx:MiniSqlParser.JoinTypeContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#cmpOp.
    def enterCmpOp(self, ctx:MiniSqlParser.CmpOpContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#cmpOp.
    def exitCmpOp(self, ctx:MiniSqlParser.CmpOpContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#arithOp.
    def enterArithOp(self, ctx:MiniSqlParser.ArithOpContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#arithOp.
    def exitArithOp(self, ctx:MiniSqlParser.ArithOpContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#unaryOp.
    def enterUnaryOp(self, ctx:MiniSqlParser.UnaryOpContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#unaryOp.
    def exitUnaryOp(self, ctx:MiniSqlParser.UnaryOpContext):
        pass


    # Enter a parse tree produced by MiniSqlParser#unquotedIdentifier.
    def enterUnquotedIdentifier(self, ctx:MiniSqlParser.UnquotedIdentifierContext):
        pass

    # Exit a parse tree produced by MiniSqlParser#unquotedIdentifier.
    def exitUnquotedIdentifier(self, ctx:MiniSqlParser.UnquotedIdentifierContext):
        pass



del MiniSqlParser
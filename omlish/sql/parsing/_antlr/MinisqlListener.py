# type: ignore
# ruff: noqa
# flake8: noqa
# Generated from Minisql.g4 by ANTLR 4.13.2
from omlish.antlr._runtime._all import *
if "." in __name__:
    from .MinisqlParser import MinisqlParser
else:
    from MinisqlParser import MinisqlParser

# This class defines a complete listener for a parse tree produced by MinisqlParser.
class MinisqlListener(ParseTreeListener):

    # Enter a parse tree produced by MinisqlParser#singleStmt.
    def enterSingleStmt(self, ctx:MinisqlParser.SingleStmtContext):
        pass

    # Exit a parse tree produced by MinisqlParser#singleStmt.
    def exitSingleStmt(self, ctx:MinisqlParser.SingleStmtContext):
        pass


    # Enter a parse tree produced by MinisqlParser#select.
    def enterSelect(self, ctx:MinisqlParser.SelectContext):
        pass

    # Exit a parse tree produced by MinisqlParser#select.
    def exitSelect(self, ctx:MinisqlParser.SelectContext):
        pass


    # Enter a parse tree produced by MinisqlParser#cteSelect.
    def enterCteSelect(self, ctx:MinisqlParser.CteSelectContext):
        pass

    # Exit a parse tree produced by MinisqlParser#cteSelect.
    def exitCteSelect(self, ctx:MinisqlParser.CteSelectContext):
        pass


    # Enter a parse tree produced by MinisqlParser#cte.
    def enterCte(self, ctx:MinisqlParser.CteContext):
        pass

    # Exit a parse tree produced by MinisqlParser#cte.
    def exitCte(self, ctx:MinisqlParser.CteContext):
        pass


    # Enter a parse tree produced by MinisqlParser#unionSelect.
    def enterUnionSelect(self, ctx:MinisqlParser.UnionSelectContext):
        pass

    # Exit a parse tree produced by MinisqlParser#unionSelect.
    def exitUnionSelect(self, ctx:MinisqlParser.UnionSelectContext):
        pass


    # Enter a parse tree produced by MinisqlParser#unionItem.
    def enterUnionItem(self, ctx:MinisqlParser.UnionItemContext):
        pass

    # Exit a parse tree produced by MinisqlParser#unionItem.
    def exitUnionItem(self, ctx:MinisqlParser.UnionItemContext):
        pass


    # Enter a parse tree produced by MinisqlParser#primarySelect.
    def enterPrimarySelect(self, ctx:MinisqlParser.PrimarySelectContext):
        pass

    # Exit a parse tree produced by MinisqlParser#primarySelect.
    def exitPrimarySelect(self, ctx:MinisqlParser.PrimarySelectContext):
        pass


    # Enter a parse tree produced by MinisqlParser#allSelectItem.
    def enterAllSelectItem(self, ctx:MinisqlParser.AllSelectItemContext):
        pass

    # Exit a parse tree produced by MinisqlParser#allSelectItem.
    def exitAllSelectItem(self, ctx:MinisqlParser.AllSelectItemContext):
        pass


    # Enter a parse tree produced by MinisqlParser#exprSelectItem.
    def enterExprSelectItem(self, ctx:MinisqlParser.ExprSelectItemContext):
        pass

    # Exit a parse tree produced by MinisqlParser#exprSelectItem.
    def exitExprSelectItem(self, ctx:MinisqlParser.ExprSelectItemContext):
        pass


    # Enter a parse tree produced by MinisqlParser#expr.
    def enterExpr(self, ctx:MinisqlParser.ExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#expr.
    def exitExpr(self, ctx:MinisqlParser.ExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#unaryBooleanExpr.
    def enterUnaryBooleanExpr(self, ctx:MinisqlParser.UnaryBooleanExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#unaryBooleanExpr.
    def exitUnaryBooleanExpr(self, ctx:MinisqlParser.UnaryBooleanExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#predicatedBooleanExpr.
    def enterPredicatedBooleanExpr(self, ctx:MinisqlParser.PredicatedBooleanExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#predicatedBooleanExpr.
    def exitPredicatedBooleanExpr(self, ctx:MinisqlParser.PredicatedBooleanExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#binaryBooleanExpr.
    def enterBinaryBooleanExpr(self, ctx:MinisqlParser.BinaryBooleanExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#binaryBooleanExpr.
    def exitBinaryBooleanExpr(self, ctx:MinisqlParser.BinaryBooleanExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#castBooleanExpr.
    def enterCastBooleanExpr(self, ctx:MinisqlParser.CastBooleanExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#castBooleanExpr.
    def exitCastBooleanExpr(self, ctx:MinisqlParser.CastBooleanExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#cmpPredicate.
    def enterCmpPredicate(self, ctx:MinisqlParser.CmpPredicateContext):
        pass

    # Exit a parse tree produced by MinisqlParser#cmpPredicate.
    def exitCmpPredicate(self, ctx:MinisqlParser.CmpPredicateContext):
        pass


    # Enter a parse tree produced by MinisqlParser#isNullPredicate.
    def enterIsNullPredicate(self, ctx:MinisqlParser.IsNullPredicateContext):
        pass

    # Exit a parse tree produced by MinisqlParser#isNullPredicate.
    def exitIsNullPredicate(self, ctx:MinisqlParser.IsNullPredicateContext):
        pass


    # Enter a parse tree produced by MinisqlParser#inListPredicate.
    def enterInListPredicate(self, ctx:MinisqlParser.InListPredicateContext):
        pass

    # Exit a parse tree produced by MinisqlParser#inListPredicate.
    def exitInListPredicate(self, ctx:MinisqlParser.InListPredicateContext):
        pass


    # Enter a parse tree produced by MinisqlParser#inSelectPredicate.
    def enterInSelectPredicate(self, ctx:MinisqlParser.InSelectPredicateContext):
        pass

    # Exit a parse tree produced by MinisqlParser#inSelectPredicate.
    def exitInSelectPredicate(self, ctx:MinisqlParser.InSelectPredicateContext):
        pass


    # Enter a parse tree produced by MinisqlParser#likePredicate.
    def enterLikePredicate(self, ctx:MinisqlParser.LikePredicateContext):
        pass

    # Exit a parse tree produced by MinisqlParser#likePredicate.
    def exitLikePredicate(self, ctx:MinisqlParser.LikePredicateContext):
        pass


    # Enter a parse tree produced by MinisqlParser#arithValueExpr.
    def enterArithValueExpr(self, ctx:MinisqlParser.ArithValueExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#arithValueExpr.
    def exitArithValueExpr(self, ctx:MinisqlParser.ArithValueExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#unaryValueExpr.
    def enterUnaryValueExpr(self, ctx:MinisqlParser.UnaryValueExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#unaryValueExpr.
    def exitUnaryValueExpr(self, ctx:MinisqlParser.UnaryValueExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#primaryValueExpr.
    def enterPrimaryValueExpr(self, ctx:MinisqlParser.PrimaryValueExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#primaryValueExpr.
    def exitPrimaryValueExpr(self, ctx:MinisqlParser.PrimaryValueExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#functionCallExpr.
    def enterFunctionCallExpr(self, ctx:MinisqlParser.FunctionCallExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#functionCallExpr.
    def exitFunctionCallExpr(self, ctx:MinisqlParser.FunctionCallExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#starFunctionCallExpr.
    def enterStarFunctionCallExpr(self, ctx:MinisqlParser.StarFunctionCallExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#starFunctionCallExpr.
    def exitStarFunctionCallExpr(self, ctx:MinisqlParser.StarFunctionCallExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#caseExpr.
    def enterCaseExpr(self, ctx:MinisqlParser.CaseExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#caseExpr.
    def exitCaseExpr(self, ctx:MinisqlParser.CaseExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#selectExpr.
    def enterSelectExpr(self, ctx:MinisqlParser.SelectExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#selectExpr.
    def exitSelectExpr(self, ctx:MinisqlParser.SelectExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#parenExpr.
    def enterParenExpr(self, ctx:MinisqlParser.ParenExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#parenExpr.
    def exitParenExpr(self, ctx:MinisqlParser.ParenExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#simplePrimaryExpr.
    def enterSimplePrimaryExpr(self, ctx:MinisqlParser.SimplePrimaryExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#simplePrimaryExpr.
    def exitSimplePrimaryExpr(self, ctx:MinisqlParser.SimplePrimaryExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#simpleExpr.
    def enterSimpleExpr(self, ctx:MinisqlParser.SimpleExprContext):
        pass

    # Exit a parse tree produced by MinisqlParser#simpleExpr.
    def exitSimpleExpr(self, ctx:MinisqlParser.SimpleExprContext):
        pass


    # Enter a parse tree produced by MinisqlParser#caseItem.
    def enterCaseItem(self, ctx:MinisqlParser.CaseItemContext):
        pass

    # Exit a parse tree produced by MinisqlParser#caseItem.
    def exitCaseItem(self, ctx:MinisqlParser.CaseItemContext):
        pass


    # Enter a parse tree produced by MinisqlParser#over.
    def enterOver(self, ctx:MinisqlParser.OverContext):
        pass

    # Exit a parse tree produced by MinisqlParser#over.
    def exitOver(self, ctx:MinisqlParser.OverContext):
        pass


    # Enter a parse tree produced by MinisqlParser#sortItem.
    def enterSortItem(self, ctx:MinisqlParser.SortItemContext):
        pass

    # Exit a parse tree produced by MinisqlParser#sortItem.
    def exitSortItem(self, ctx:MinisqlParser.SortItemContext):
        pass


    # Enter a parse tree produced by MinisqlParser#aliasedRelation.
    def enterAliasedRelation(self, ctx:MinisqlParser.AliasedRelationContext):
        pass

    # Exit a parse tree produced by MinisqlParser#aliasedRelation.
    def exitAliasedRelation(self, ctx:MinisqlParser.AliasedRelationContext):
        pass


    # Enter a parse tree produced by MinisqlParser#joinRelation.
    def enterJoinRelation(self, ctx:MinisqlParser.JoinRelationContext):
        pass

    # Exit a parse tree produced by MinisqlParser#joinRelation.
    def exitJoinRelation(self, ctx:MinisqlParser.JoinRelationContext):
        pass


    # Enter a parse tree produced by MinisqlParser#selectRelation.
    def enterSelectRelation(self, ctx:MinisqlParser.SelectRelationContext):
        pass

    # Exit a parse tree produced by MinisqlParser#selectRelation.
    def exitSelectRelation(self, ctx:MinisqlParser.SelectRelationContext):
        pass


    # Enter a parse tree produced by MinisqlParser#tableRelation.
    def enterTableRelation(self, ctx:MinisqlParser.TableRelationContext):
        pass

    # Exit a parse tree produced by MinisqlParser#tableRelation.
    def exitTableRelation(self, ctx:MinisqlParser.TableRelationContext):
        pass


    # Enter a parse tree produced by MinisqlParser#parenRelation.
    def enterParenRelation(self, ctx:MinisqlParser.ParenRelationContext):
        pass

    # Exit a parse tree produced by MinisqlParser#parenRelation.
    def exitParenRelation(self, ctx:MinisqlParser.ParenRelationContext):
        pass


    # Enter a parse tree produced by MinisqlParser#groupBy.
    def enterGroupBy(self, ctx:MinisqlParser.GroupByContext):
        pass

    # Exit a parse tree produced by MinisqlParser#groupBy.
    def exitGroupBy(self, ctx:MinisqlParser.GroupByContext):
        pass


    # Enter a parse tree produced by MinisqlParser#qualifiedName.
    def enterQualifiedName(self, ctx:MinisqlParser.QualifiedNameContext):
        pass

    # Exit a parse tree produced by MinisqlParser#qualifiedName.
    def exitQualifiedName(self, ctx:MinisqlParser.QualifiedNameContext):
        pass


    # Enter a parse tree produced by MinisqlParser#identList.
    def enterIdentList(self, ctx:MinisqlParser.IdentListContext):
        pass

    # Exit a parse tree produced by MinisqlParser#identList.
    def exitIdentList(self, ctx:MinisqlParser.IdentListContext):
        pass


    # Enter a parse tree produced by MinisqlParser#ident.
    def enterIdent(self, ctx:MinisqlParser.IdentContext):
        pass

    # Exit a parse tree produced by MinisqlParser#ident.
    def exitIdent(self, ctx:MinisqlParser.IdentContext):
        pass


    # Enter a parse tree produced by MinisqlParser#quotedIdent.
    def enterQuotedIdent(self, ctx:MinisqlParser.QuotedIdentContext):
        pass

    # Exit a parse tree produced by MinisqlParser#quotedIdent.
    def exitQuotedIdent(self, ctx:MinisqlParser.QuotedIdentContext):
        pass


    # Enter a parse tree produced by MinisqlParser#integerNumber.
    def enterIntegerNumber(self, ctx:MinisqlParser.IntegerNumberContext):
        pass

    # Exit a parse tree produced by MinisqlParser#integerNumber.
    def exitIntegerNumber(self, ctx:MinisqlParser.IntegerNumberContext):
        pass


    # Enter a parse tree produced by MinisqlParser#decimalNumber.
    def enterDecimalNumber(self, ctx:MinisqlParser.DecimalNumberContext):
        pass

    # Exit a parse tree produced by MinisqlParser#decimalNumber.
    def exitDecimalNumber(self, ctx:MinisqlParser.DecimalNumberContext):
        pass


    # Enter a parse tree produced by MinisqlParser#floatNumber.
    def enterFloatNumber(self, ctx:MinisqlParser.FloatNumberContext):
        pass

    # Exit a parse tree produced by MinisqlParser#floatNumber.
    def exitFloatNumber(self, ctx:MinisqlParser.FloatNumberContext):
        pass


    # Enter a parse tree produced by MinisqlParser#string.
    def enterString(self, ctx:MinisqlParser.StringContext):
        pass

    # Exit a parse tree produced by MinisqlParser#string.
    def exitString(self, ctx:MinisqlParser.StringContext):
        pass


    # Enter a parse tree produced by MinisqlParser#null.
    def enterNull(self, ctx:MinisqlParser.NullContext):
        pass

    # Exit a parse tree produced by MinisqlParser#null.
    def exitNull(self, ctx:MinisqlParser.NullContext):
        pass


    # Enter a parse tree produced by MinisqlParser#true.
    def enterTrue(self, ctx:MinisqlParser.TrueContext):
        pass

    # Exit a parse tree produced by MinisqlParser#true.
    def exitTrue(self, ctx:MinisqlParser.TrueContext):
        pass


    # Enter a parse tree produced by MinisqlParser#false.
    def enterFalse(self, ctx:MinisqlParser.FalseContext):
        pass

    # Exit a parse tree produced by MinisqlParser#false.
    def exitFalse(self, ctx:MinisqlParser.FalseContext):
        pass


    # Enter a parse tree produced by MinisqlParser#setQuantifier.
    def enterSetQuantifier(self, ctx:MinisqlParser.SetQuantifierContext):
        pass

    # Exit a parse tree produced by MinisqlParser#setQuantifier.
    def exitSetQuantifier(self, ctx:MinisqlParser.SetQuantifierContext):
        pass


    # Enter a parse tree produced by MinisqlParser#joinType.
    def enterJoinType(self, ctx:MinisqlParser.JoinTypeContext):
        pass

    # Exit a parse tree produced by MinisqlParser#joinType.
    def exitJoinType(self, ctx:MinisqlParser.JoinTypeContext):
        pass


    # Enter a parse tree produced by MinisqlParser#cmpOp.
    def enterCmpOp(self, ctx:MinisqlParser.CmpOpContext):
        pass

    # Exit a parse tree produced by MinisqlParser#cmpOp.
    def exitCmpOp(self, ctx:MinisqlParser.CmpOpContext):
        pass


    # Enter a parse tree produced by MinisqlParser#arithOp.
    def enterArithOp(self, ctx:MinisqlParser.ArithOpContext):
        pass

    # Exit a parse tree produced by MinisqlParser#arithOp.
    def exitArithOp(self, ctx:MinisqlParser.ArithOpContext):
        pass


    # Enter a parse tree produced by MinisqlParser#unaryOp.
    def enterUnaryOp(self, ctx:MinisqlParser.UnaryOpContext):
        pass

    # Exit a parse tree produced by MinisqlParser#unaryOp.
    def exitUnaryOp(self, ctx:MinisqlParser.UnaryOpContext):
        pass


    # Enter a parse tree produced by MinisqlParser#unquotedIdent.
    def enterUnquotedIdent(self, ctx:MinisqlParser.UnquotedIdentContext):
        pass

    # Exit a parse tree produced by MinisqlParser#unquotedIdent.
    def exitUnquotedIdent(self, ctx:MinisqlParser.UnquotedIdentContext):
        pass



del MinisqlParser
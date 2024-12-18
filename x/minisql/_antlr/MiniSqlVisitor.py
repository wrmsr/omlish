# type: ignore
# ruff: noqa
# flake8: noqa
# Generated from MiniSql.g4 by ANTLR 4.13.2
from omlish.antlr._runtime._all import *
if "." in __name__:
    from .MiniSqlParser import MiniSqlParser
else:
    from MiniSqlParser import MiniSqlParser

# This class defines a complete generic visitor for a parse tree produced by MiniSqlParser.

class MiniSqlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MiniSqlParser#singleStatement.
    def visitSingleStatement(self, ctx:MiniSqlParser.SingleStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#select.
    def visitSelect(self, ctx:MiniSqlParser.SelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#cteSelect.
    def visitCteSelect(self, ctx:MiniSqlParser.CteSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#cte.
    def visitCte(self, ctx:MiniSqlParser.CteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#unionSelect.
    def visitUnionSelect(self, ctx:MiniSqlParser.UnionSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#unionItem.
    def visitUnionItem(self, ctx:MiniSqlParser.UnionItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#primarySelect.
    def visitPrimarySelect(self, ctx:MiniSqlParser.PrimarySelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#allSelectItem.
    def visitAllSelectItem(self, ctx:MiniSqlParser.AllSelectItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#expressionSelectItem.
    def visitExpressionSelectItem(self, ctx:MiniSqlParser.ExpressionSelectItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#expression.
    def visitExpression(self, ctx:MiniSqlParser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#binaryBooleanExpression.
    def visitBinaryBooleanExpression(self, ctx:MiniSqlParser.BinaryBooleanExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#predicatedBooleanExpression.
    def visitPredicatedBooleanExpression(self, ctx:MiniSqlParser.PredicatedBooleanExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#unaryBooleanExpression.
    def visitUnaryBooleanExpression(self, ctx:MiniSqlParser.UnaryBooleanExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#castBooleanExpression.
    def visitCastBooleanExpression(self, ctx:MiniSqlParser.CastBooleanExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#cmpPredicate.
    def visitCmpPredicate(self, ctx:MiniSqlParser.CmpPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#isNullPredicate.
    def visitIsNullPredicate(self, ctx:MiniSqlParser.IsNullPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#inListPredicate.
    def visitInListPredicate(self, ctx:MiniSqlParser.InListPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#inSelectPredicate.
    def visitInSelectPredicate(self, ctx:MiniSqlParser.InSelectPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#likePredicate.
    def visitLikePredicate(self, ctx:MiniSqlParser.LikePredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#primaryValueExpression.
    def visitPrimaryValueExpression(self, ctx:MiniSqlParser.PrimaryValueExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#unaryValueExpression.
    def visitUnaryValueExpression(self, ctx:MiniSqlParser.UnaryValueExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#arithValueExpression.
    def visitArithValueExpression(self, ctx:MiniSqlParser.ArithValueExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#functionCallExpression.
    def visitFunctionCallExpression(self, ctx:MiniSqlParser.FunctionCallExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#starFunctionCallExpression.
    def visitStarFunctionCallExpression(self, ctx:MiniSqlParser.StarFunctionCallExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#caseExpression.
    def visitCaseExpression(self, ctx:MiniSqlParser.CaseExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#selectExpression.
    def visitSelectExpression(self, ctx:MiniSqlParser.SelectExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#parenExpression.
    def visitParenExpression(self, ctx:MiniSqlParser.ParenExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#simplePrimaryExpression.
    def visitSimplePrimaryExpression(self, ctx:MiniSqlParser.SimplePrimaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#simpleExpression.
    def visitSimpleExpression(self, ctx:MiniSqlParser.SimpleExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#caseItem.
    def visitCaseItem(self, ctx:MiniSqlParser.CaseItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#over.
    def visitOver(self, ctx:MiniSqlParser.OverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#sortItem.
    def visitSortItem(self, ctx:MiniSqlParser.SortItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#aliasedRelation.
    def visitAliasedRelation(self, ctx:MiniSqlParser.AliasedRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#joinRelation.
    def visitJoinRelation(self, ctx:MiniSqlParser.JoinRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#selectRelation.
    def visitSelectRelation(self, ctx:MiniSqlParser.SelectRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#tableRelation.
    def visitTableRelation(self, ctx:MiniSqlParser.TableRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#parenRelation.
    def visitParenRelation(self, ctx:MiniSqlParser.ParenRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#groupBy.
    def visitGroupBy(self, ctx:MiniSqlParser.GroupByContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#qualifiedName.
    def visitQualifiedName(self, ctx:MiniSqlParser.QualifiedNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#identifierList.
    def visitIdentifierList(self, ctx:MiniSqlParser.IdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#identifier.
    def visitIdentifier(self, ctx:MiniSqlParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#quotedIdentifier.
    def visitQuotedIdentifier(self, ctx:MiniSqlParser.QuotedIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#integerNumber.
    def visitIntegerNumber(self, ctx:MiniSqlParser.IntegerNumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#decimalNumber.
    def visitDecimalNumber(self, ctx:MiniSqlParser.DecimalNumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#floatNumber.
    def visitFloatNumber(self, ctx:MiniSqlParser.FloatNumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#string.
    def visitString(self, ctx:MiniSqlParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#null.
    def visitNull(self, ctx:MiniSqlParser.NullContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#true.
    def visitTrue(self, ctx:MiniSqlParser.TrueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#false.
    def visitFalse(self, ctx:MiniSqlParser.FalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#setQuantifier.
    def visitSetQuantifier(self, ctx:MiniSqlParser.SetQuantifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#joinType.
    def visitJoinType(self, ctx:MiniSqlParser.JoinTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#cmpOp.
    def visitCmpOp(self, ctx:MiniSqlParser.CmpOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#arithOp.
    def visitArithOp(self, ctx:MiniSqlParser.ArithOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#unaryOp.
    def visitUnaryOp(self, ctx:MiniSqlParser.UnaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MiniSqlParser#unquotedIdentifier.
    def visitUnquotedIdentifier(self, ctx:MiniSqlParser.UnquotedIdentifierContext):
        return self.visitChildren(ctx)



del MiniSqlParser
# type: ignore
# ruff: noqa
# flake8: noqa
# Generated from Minisql.g4 by ANTLR 4.13.2
from omlish.antlr._runtime._all import *
if "." in __name__:
    from .MinisqlParser import MinisqlParser
else:
    from MinisqlParser import MinisqlParser

# This class defines a complete generic visitor for a parse tree produced by MinisqlParser.

class MinisqlVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by MinisqlParser#singleStmt.
    def visitSingleStmt(self, ctx:MinisqlParser.SingleStmtContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#select.
    def visitSelect(self, ctx:MinisqlParser.SelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#cteSelect.
    def visitCteSelect(self, ctx:MinisqlParser.CteSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#cte.
    def visitCte(self, ctx:MinisqlParser.CteContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#unionSelect.
    def visitUnionSelect(self, ctx:MinisqlParser.UnionSelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#unionItem.
    def visitUnionItem(self, ctx:MinisqlParser.UnionItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#primarySelect.
    def visitPrimarySelect(self, ctx:MinisqlParser.PrimarySelectContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#allSelectItem.
    def visitAllSelectItem(self, ctx:MinisqlParser.AllSelectItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#exprSelectItem.
    def visitExprSelectItem(self, ctx:MinisqlParser.ExprSelectItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#expr.
    def visitExpr(self, ctx:MinisqlParser.ExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#unaryBooleanExpr.
    def visitUnaryBooleanExpr(self, ctx:MinisqlParser.UnaryBooleanExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#predicatedBooleanExpr.
    def visitPredicatedBooleanExpr(self, ctx:MinisqlParser.PredicatedBooleanExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#binaryBooleanExpr.
    def visitBinaryBooleanExpr(self, ctx:MinisqlParser.BinaryBooleanExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#castBooleanExpr.
    def visitCastBooleanExpr(self, ctx:MinisqlParser.CastBooleanExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#cmpPredicate.
    def visitCmpPredicate(self, ctx:MinisqlParser.CmpPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#isNullPredicate.
    def visitIsNullPredicate(self, ctx:MinisqlParser.IsNullPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#inListPredicate.
    def visitInListPredicate(self, ctx:MinisqlParser.InListPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#inSelectPredicate.
    def visitInSelectPredicate(self, ctx:MinisqlParser.InSelectPredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#likePredicate.
    def visitLikePredicate(self, ctx:MinisqlParser.LikePredicateContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#arithValueExpr.
    def visitArithValueExpr(self, ctx:MinisqlParser.ArithValueExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#unaryValueExpr.
    def visitUnaryValueExpr(self, ctx:MinisqlParser.UnaryValueExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#primaryValueExpr.
    def visitPrimaryValueExpr(self, ctx:MinisqlParser.PrimaryValueExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#functionCallExpr.
    def visitFunctionCallExpr(self, ctx:MinisqlParser.FunctionCallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#starFunctionCallExpr.
    def visitStarFunctionCallExpr(self, ctx:MinisqlParser.StarFunctionCallExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#caseExpr.
    def visitCaseExpr(self, ctx:MinisqlParser.CaseExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#selectExpr.
    def visitSelectExpr(self, ctx:MinisqlParser.SelectExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#parenExpr.
    def visitParenExpr(self, ctx:MinisqlParser.ParenExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#simplePrimaryExpr.
    def visitSimplePrimaryExpr(self, ctx:MinisqlParser.SimplePrimaryExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#simpleExpr.
    def visitSimpleExpr(self, ctx:MinisqlParser.SimpleExprContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#caseItem.
    def visitCaseItem(self, ctx:MinisqlParser.CaseItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#over.
    def visitOver(self, ctx:MinisqlParser.OverContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#sortItem.
    def visitSortItem(self, ctx:MinisqlParser.SortItemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#aliasedRelation.
    def visitAliasedRelation(self, ctx:MinisqlParser.AliasedRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#joinRelation.
    def visitJoinRelation(self, ctx:MinisqlParser.JoinRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#selectRelation.
    def visitSelectRelation(self, ctx:MinisqlParser.SelectRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#tableRelation.
    def visitTableRelation(self, ctx:MinisqlParser.TableRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#parenRelation.
    def visitParenRelation(self, ctx:MinisqlParser.ParenRelationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#groupBy.
    def visitGroupBy(self, ctx:MinisqlParser.GroupByContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#qualifiedName.
    def visitQualifiedName(self, ctx:MinisqlParser.QualifiedNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#identList.
    def visitIdentList(self, ctx:MinisqlParser.IdentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#ident.
    def visitIdent(self, ctx:MinisqlParser.IdentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#quotedIdent.
    def visitQuotedIdent(self, ctx:MinisqlParser.QuotedIdentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#integerNumber.
    def visitIntegerNumber(self, ctx:MinisqlParser.IntegerNumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#decimalNumber.
    def visitDecimalNumber(self, ctx:MinisqlParser.DecimalNumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#floatNumber.
    def visitFloatNumber(self, ctx:MinisqlParser.FloatNumberContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#string.
    def visitString(self, ctx:MinisqlParser.StringContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#null.
    def visitNull(self, ctx:MinisqlParser.NullContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#true.
    def visitTrue(self, ctx:MinisqlParser.TrueContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#false.
    def visitFalse(self, ctx:MinisqlParser.FalseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#setQuantifier.
    def visitSetQuantifier(self, ctx:MinisqlParser.SetQuantifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#joinType.
    def visitJoinType(self, ctx:MinisqlParser.JoinTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#cmpOp.
    def visitCmpOp(self, ctx:MinisqlParser.CmpOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#arithOp.
    def visitArithOp(self, ctx:MinisqlParser.ArithOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#unaryOp.
    def visitUnaryOp(self, ctx:MinisqlParser.UnaryOpContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by MinisqlParser#unquotedIdent.
    def visitUnquotedIdent(self, ctx:MinisqlParser.UnquotedIdentContext):
        return self.visitChildren(ctx)



del MinisqlParser
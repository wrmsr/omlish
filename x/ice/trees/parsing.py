"""
FIXME:
 - caseless parsing (func kwargs? idents? use omni CaseInsens thing)
 - semicolon termination
 - total parsing
 - builtin quoting

TODO:
 - select * from table (f()) - currently parses table as ident?
 - double check nullsFunctionCall rewriting is correct
 - fix UNION ALL ALL
  - ((select 1) union (((select 2)))) ?
 - params
 - https://docs.snowflake.com/en/sql-reference/literals-table.html
 - TABLESAMPLE
 - omni cy
 - confirm l_v(v ignore nulls) == l_v(v) ignore nulls
 - cython, obv
 - parallelize
 - cache?
 - simple language extensions:
  - trailing commas, 'and's, joins?
 - special forms:
  - let, drop
 - $$, create func?
 - ** flink, spark, catalyst in general **

TODO ( https://calcite.apache.org/docs/reference.html ):
 - UNNEST '(' expression ')' [ WITH ORDINALITY ]
 - MATCH_RECOGNIZE

http://snowflake.net/blog/snowflake-sql-making-schema-on-read-a-reality-part-1-2/
"""
import typing as ta

from omnibus import antlr
from omnibus import check
from omnibus import dataclasses as dc
from omnibus._vendor import antlr4

from . import nodes as no
from ._antlr.IceSqlLexer import IceSqlLexer
from ._antlr.IceSqlParser import IceSqlParser
from ._antlr.IceSqlParser import IceSqlParserConfig
from ._antlr.IceSqlVisitor import IceSqlVisitor
from .quoting import unquote
from .types import AstQuery
from .types import Query
from .types import StrQuery


def strip_jinja(text: str) -> str:
    check.arg(text.startswith('{{') and text.endswith('}}'))
    return text[2:-2].strip()


class _ParseVisitor(IceSqlVisitor):

    def visit(self, ctx: antlr4.ParserRuleContext):
        check.isinstance(ctx, antlr4.ParserRuleContext)
        node = ctx.accept(self)
        if node is not None:
            node = check.isinstance(node, no.Node)
            if antlr4.ParserRuleContext not in node.meta:
                node = dc.replace(node, meta={**node.meta, antlr4.ParserRuleContext: ctx})
        return node

    def aggregateResult(self, aggregate, nextResult):
        if aggregate is not None:
            check.none(nextResult)
            return aggregate
        else:
            check.none(aggregate)
            return nextResult

    def visitAliasedRelation(self, ctx: IceSqlParser.AliasedRelationContext):
        relation = self.visit(ctx.relation())
        alias = self.visit(ctx.identifier())
        columns = [self.visit(i) for i in ctx.identifierList().identifier()] if ctx.identifierList() is not None else []
        return no.AliasedRelation(relation, alias, columns)

    def visitAllSelectItem(self, ctx: IceSqlParser.AllSelectItemContext):
        return no.AllSelectItem()

    def visitArithValueExpression(self, ctx: IceSqlParser.ArithValueExpressionContext):
        left, right = [self.visit(e) for e in ctx.valueExpression()]
        op = no.BINARY_OP_MAP[ctx.op.getText().lower()]
        return no.BinaryExpr(left, op, right)

    def visitBetweenPredicate(self, ctx: IceSqlParser.BetweenPredicateContext):
        value = self.visit(ctx.value)
        lower = self.visit(ctx.lower)
        upper = self.visit(ctx.upper)
        return no.Between(value, lower, upper)

    def visitBinaryBooleanExpression(self, ctx: IceSqlParser.BinaryBooleanExpressionContext):
        left, right = [self.visit(e) for e in ctx.booleanExpression()]
        op = no.BINARY_OP_MAP[ctx.op.text.lower()]
        return no.BinaryExpr(left, op, right)

    def visitDoubleFrame(self, ctx: IceSqlParser.DoubleFrameContext):
        rows_or_range = no.RowsOrRange.ROWS if ctx.ROWS() is not None else no.RowsOrRange.RANGE
        min, max = [self.visit(e) for e in ctx.frameBound()]
        return no.DoubleFrame(rows_or_range, min, max)

    def visitCaseItem(self, ctx: IceSqlParser.CaseItemContext):
        when, then = [self.visit(e) for e in ctx.expression()]
        return no.CaseItem(when, then)

    def visitCaseExpression(self, ctx: IceSqlParser.CaseExpressionContext):
        value = self.visit(ctx.val) if ctx.val is not None else None
        items = [self.visit(i) for i in ctx.caseItem()]
        default = self.visit(ctx.default) if ctx.default is not None else None
        return no.Case(value, items, default)

    def visitCastCallExpression(self, ctx: IceSqlParser.CastCallExpressionContext):
        value = self.visit(ctx.expression())
        type = self.visit(ctx.typeSpec())
        return no.CastCall(value, type)

    def visitCastValueExpression(self, ctx: IceSqlParser.CastValueExpressionContext):
        value = self.visit(ctx.valueExpression())
        type = self.visit(ctx.typeSpec())
        return no.Cast(value, type)

    def visitCmpPredicate(self, ctx: IceSqlParser.CmpPredicateContext):
        left = self.visit(ctx.value)
        op = no.BINARY_OP_MAP[ctx.cmpOp().getText().lower()]
        right = self.visit(ctx.valueExpression())
        return no.BinaryExpr(left, op, right)

    def visitColSpec(self, ctx: IceSqlParser.ColSpecContext):
        name = self.visit(ctx.identifier())
        type = self.visit(ctx.typeSpec())
        return no.ColSpec(name, type)

    def visitCreateTable(self, ctx: IceSqlParser.CreateTableContext):
        name = self.visit(ctx.qualifiedName())
        cols = [self.visit(c) for c in ctx.colSpec()]
        select = self.visit(ctx.select()) if ctx.select() is not None else None
        return no.CreateTable(name, cols, select)

    def visitCte(self, ctx: IceSqlParser.CteContext):
        name = self.visit(ctx.identifier())
        select = self.visit(ctx.select())
        return no.Cte(name, select)

    def visitCteSelect(self, ctx: IceSqlParser.CteSelectContext):
        ctes = [self.visit(c) for c in ctx.cte()]
        select = self.visit(ctx.setSelect())
        return no.CteSelect(ctes, select) if ctes else select

    def visitCurrentRowFrameBound(self, ctx: IceSqlParser.CurrentRowFrameBoundContext):
        return no.CurrentRowFrameBound()

    def visitDateExpression(self, ctx: IceSqlParser.DateExpressionContext):
        value = self.visit(ctx.string())
        return no.Date(value)

    def visitDecimalNumber(self, ctx: IceSqlParser.DecimalNumberContext):
        return no.Decimal(ctx.DECIMAL_VALUE().getText())

    def visitDelete(self, ctx: IceSqlParser.DeleteContext):
        name = self.visit(ctx.qualifiedName())
        where = self.visit(ctx.where) if ctx.where is not None else None
        return no.Delete(name, where)

    def visitExpressionFunctionCall(self, ctx:IceSqlParser.ExpressionFunctionCallContext):
        name = self.visit(ctx.qualifiedName())
        args = [self.visit(a) for a in ctx.expression()]
        set_quantifier = no.SET_QUANTIFIER_MAP[ctx.setQuantifier().getText().lower()] \
            if ctx.setQuantifier() is not None else None
        nulls = (no.IgnoreOrRespect.IGNORE if ctx.IGNORE() is not None else no.IgnoreOrRespect.RESPECT) \
            if ctx.NULLS() is not None else None
        within_group = [self.visit(i) for i in ctx.sortItem()]
        over = self.visit(ctx.over()) if ctx.over() is not None else None
        return no.FunctionCall(
            name,
            args=args,
            set_quantifier=set_quantifier,
            nulls=nulls,
            within_group=within_group,
            over=over,
        )

    def visitExpressionSelectItem(self, ctx: IceSqlParser.ExpressionSelectItemContext):
        value = self.visit(ctx.expression())
        label = self.visit(ctx.identifier()) if ctx.identifier() is not None else None
        return no.ExprSelectItem(value, label)

    def visitExtractExpression(self, ctx: IceSqlParser.ExtractExpressionContext):
        part = self.visit(ctx.part)
        value = self.visit(ctx.value)
        return no.Extract(part, value)

    def visitFalse(self, ctx: IceSqlParser.FalseContext):
        return no.EFalse()

    def visitFlatGrouping(self, ctx: IceSqlParser.FlatGroupingContext):
        items = [self.visit(e) for e in ctx.expression()]
        return no.FlatGrouping(items)

    def visitFloatNumber(self, ctx: IceSqlParser.FloatNumberContext):
        return no.Float(ctx.FLOAT_VALUE().getText())

    def visitFunctionCallExpression(self, ctx: IceSqlParser.FunctionCallExpressionContext):
        call = self.visit(ctx.functionCall())
        return no.FunctionCallExpr(call)

    def visitFunctionCallRelation(self, ctx: IceSqlParser.FunctionCallRelationContext):
        call = self.visit(ctx.functionCall())
        return no.FunctionCallRelation(call)

    def visitGroupingSet(self, ctx: IceSqlParser.GroupingSetContext):
        items = [self.visit(e) for e in ctx.expression()]
        return no.GroupingSet(items)

    def visitIdentifierAllSelectItem(self, ctx: IceSqlParser.IdentifierAllSelectItemContext):
        identifier = self.visit(ctx.identifier())
        return no.IdentifierAllSelectItem(identifier)

    def visitInJinjaPredicate(self, ctx: IceSqlParser.InJinjaPredicateContext):
        needle = self.visit(ctx.value)
        text = strip_jinja(ctx.JINJA().getText())
        not_ = ctx.NOT() is not None
        return no.InJinja(needle, text, not_=not_)

    def visitInListPredicate(self, ctx: IceSqlParser.InListPredicateContext):
        needle = self.visit(ctx.value)
        haystack = [self.visit(e) for e in ctx.expression()]
        not_ = ctx.NOT() is not None
        return no.InList(needle, haystack, not_=not_)

    def visitInSelectPredicate(self, ctx: IceSqlParser.InSelectPredicateContext):
        needle = self.visit(ctx.value)
        haystack = self.visit(ctx.select())
        not_ = ctx.NOT() is not None
        return no.InSelect(needle, haystack, not_=not_)

    def visitInsert(self, ctx: IceSqlParser.InsertContext):
        name = self.visit(ctx.qualifiedName())
        select = self.visit(ctx.select()) if ctx.select() is not None else None
        return no.Insert(name, select)

    def visitInteger(self, ctx: IceSqlParser.IntegerContext):
        return no.Integer(int(ctx.INTEGER_VALUE().getText()))

    def visitIntervalExpression(self, ctx: IceSqlParser.IntervalExpressionContext):
        value = self.visit(ctx.expression())
        unit = no.INTERVAL_UNIT_MAP[ctx.intervalUnit().getText()] if ctx.intervalUnit() is not None else None
        return no.Interval(value, unit)

    def visitIsNullPredicate(self, ctx: IceSqlParser.IsNullPredicateContext):
        value = self.visit(ctx.value)
        not_ = ctx.NOT() is not None
        return no.IsNull(value, not_=not_)

    def visitJinjaExpression(self, ctx: IceSqlParser.JinjaExpressionContext):
        text = strip_jinja(ctx.getText())
        return no.JinjaExpr(text)

    def visitJinjaRelation(self, ctx: IceSqlParser.JinjaRelationContext):
        text = strip_jinja(ctx.getText())
        return no.JinjaRelation(text)

    def visitJoinRelation(self, ctx: IceSqlParser.JoinRelationContext):
        left = self.visit(ctx.left)
        type_ = no.JOIN_TYPE_MAP[' '.join(c.getText().lower() for c in ctx.joinType().children)] \
            if ctx.joinType() is not None else no.JoinType.DEFAULT
        right = self.visit(ctx.right)
        condition = self.visit(ctx.cond) if ctx.cond is not None else None
        using = [self.visit(i) for i in ctx.using.identifier()] if ctx.using else None
        return no.Join(
            left,
            type_,
            right,
            condition=condition,
            using=using,
        )

    def visitKwarg(self, ctx: IceSqlParser.KwargContext):
        name = self.visit(ctx.identifier())
        value = self.visit(ctx.expression())
        return no.Kwarg(name, value)

    def visitKwargFunctionCall(self, ctx: IceSqlParser.KwargFunctionCallContext):
        name = self.visit(ctx.qualifiedName())
        kwargs = [self.visit(a) for a in ctx.kwarg()]
        nulls = (no.IgnoreOrRespect.IGNORE if ctx.IGNORE() is not None else no.IgnoreOrRespect.RESPECT) \
            if ctx.NULLS() is not None else None
        within_group = [self.visit(i) for i in ctx.sortItem()]
        over = self.visit(ctx.over()) if ctx.over() is not None else None
        return no.FunctionCall(
            name,
            kwargs=kwargs,
            nulls=nulls,
            within_group=within_group,
            over=over,
        )

    def visitLikePredicate(self, ctx: IceSqlParser.LikePredicateContext):
        kind = no.LIKE_KIND_MAP[ctx.kind.text.lower()]
        value = self.visit(ctx.value)
        patterns = [self.visit(e) for e in ctx.expression()]
        not_ = ctx.NOT() is not None
        escape = self.visit(ctx.esc) if ctx.esc is not None else None
        return no.Like(kind, value, patterns, not_=not_, escape=escape)

    def visitNull(self, ctx: IceSqlParser.NullContext):
        return no.Null()

    def visitNullsFunctionCall(self, ctx: IceSqlParser.NullsFunctionCallContext):
        name = self.visit(ctx.qualifiedName())
        arg = self.visit(ctx.expression())
        set_quantifier = no.SET_QUANTIFIER_MAP[ctx.setQuantifier().getText().lower()] \
            if ctx.setQuantifier() is not None else None
        nulls = no.IgnoreOrRespect.IGNORE if ctx.IGNORE() is not None else no.IgnoreOrRespect.RESPECT
        within_group = [self.visit(i) for i in ctx.sortItem()]
        over = self.visit(ctx.over()) if ctx.over() is not None else None
        return no.FunctionCall(
            name,
            args=[arg],
            set_quantifier=set_quantifier,
            nulls=nulls,
            within_group=within_group,
            over=over,
        )

    def visitNumFrameBound(self, ctx: IceSqlParser.NumFrameBoundContext):
        num = int(ctx.INTEGER_VALUE().getText())
        precedence = no.Precedence.PRECEDING if ctx.PRECEDING() is not None else no.Precedence.FOLLOWING
        return no.NumFrameBound(num, precedence)

    def visitOver(self, ctx: IceSqlParser.OverContext):
        partition_by = [self.visit(p) for p in ctx.expression()]
        order_by = [self.visit(s) for s in ctx.sortItem()]
        frame = self.visit(ctx.frame()) if ctx.frame() is not None else None
        return no.Over(partition_by=partition_by, order_by=order_by, frame=frame)

    def visitParam(self, ctx: IceSqlParser.ParamContext):
        return no.Param(ctx.IDENTIFIER().getText())

    def visitParenRelation(self, ctx: IceSqlParser.ParenRelationContext):
        return self.visit(ctx.relation())

    def visitPivotRelation(self, ctx: IceSqlParser.PivotRelationContext):
        relation = self.visit(ctx.relation())
        func = self.visit(ctx.func)
        pivot_col = self.visit(ctx.pc)
        value_col = self.visit(ctx.vc)
        values = [self.visit(e) for e in ctx.expression()]
        return no.Pivot(
            relation,
            func,
            pivot_col,
            value_col,
            values,
        )

    def visitPredicatedBooleanExpression(self, ctx: IceSqlParser.PredicatedBooleanExpressionContext):
        return self.visit(ctx.predicate()) if ctx.predicate() is not None else self.visit(ctx.valueExpression())

    def visitPrimarySelect(self, ctx: IceSqlParser.PrimarySelectContext):
        items = [self.visit(i) for i in ctx.selectItem()]
        relations = [self.visit(r) for r in ctx.relation()]
        top_n = self.visit(ctx.topN()) if ctx.topN() is not None else None
        set_quantifier = no.SET_QUANTIFIER_MAP[ctx.setQuantifier().getText().lower()] \
            if ctx.setQuantifier() is not None else None
        where = self.visit(ctx.where) if ctx.where is not None else None
        group_by = self.visit(ctx.grouping()) if ctx.grouping() else None
        having = self.visit(ctx.having) if ctx.having is not None else None
        qualify = self.visit(ctx.qualify) if ctx.qualify is not None else None
        order_by = [self.visit(s) for s in ctx.sortItem()] if ctx.sortItem() is not None else None
        limit = int(ctx.INTEGER_VALUE().getText()) if ctx.INTEGER_VALUE() is not None else None
        return no.Select(
            items,
            relations,
            where,
            top_n=top_n,
            set_quantifier=set_quantifier,
            group_by=group_by,
            having=having,
            qualify=qualify,
            order_by=order_by,
            limit=limit,
        )

    def visitQualifiedName(self, ctx: IceSqlParser.QualifiedNameContext):
        parts = [self.visit(i) for i in ctx.identifier()]
        return no.QualifiedNameNode(parts)

    def visitQuotedIdentifier(self, ctx: IceSqlParser.QuotedIdentifierContext):
        name = unquote(ctx.QUOTED_IDENTIFIER().getText(), '"')
        return no.Identifier(name)

    def visitSelectExpression(self, ctx: IceSqlParser.SelectExpressionContext):
        select = self.visit(ctx.select())
        return no.SelectExpr(select)

    def visitSelectRelation(self, ctx: IceSqlParser.SelectRelationContext):
        select = self.visit(ctx.select())
        return no.SelectRelation(select)

    def visitSetSelect(self, ctx: IceSqlParser.SetSelectContext):
        left = self.visit(ctx.parenSelect())
        items = [self.visit(i) for i in ctx.setSelectItem()]
        return no.SetSelect(left, items) if items else left

    def visitSetSelectItem(self, ctx: IceSqlParser.SetSelectItemContext):
        kind = no.SET_SELECT_KIND_MAP[' '.join(c.getText().lower() for c in ctx.setSelectKind().children)]
        right = self.visit(ctx.parenSelect())
        set_quantifier = no.SET_QUANTIFIER_MAP[ctx.setQuantifier().getText().lower()] \
            if ctx.setQuantifier() is not None else None
        return no.SetSelectItem(kind, right, set_quantifier)

    def visitSetsGrouping(self, ctx: IceSqlParser.SetsGroupingContext):
        sets = [self.visit(c) for c in ctx.groupingSet()]
        return no.SetsGrouping(sets)

    def visitSingleFrame(self, ctx: IceSqlParser.SingleFrameContext):
        rows_or_range = no.RowsOrRange.ROWS if ctx.ROWS() is not None else no.RowsOrRange.RANGE
        bound = self.visit(ctx.frameBound())
        return no.SingleFrame(rows_or_range, bound)

    def visitSortItem(self, ctx: IceSqlParser.SortItemContext):
        value = self.visit(ctx.expression())
        direction = no.DIRECTION_MAP[ctx.direction.text.lower()] if ctx.direction is not None else None
        nulls = (no.FirstOrLast.FIRST if ctx.FIRST() is not None else no.FirstOrLast.LAST) \
            if ctx.NULLS() is not None else None
        return no.SortItem(value, direction, nulls)

    def visitStarFunctionCall(self, ctx:IceSqlParser.StarFunctionCallContext):
        name = self.visit(ctx.qualifiedName())
        over = self.visit(ctx.over()) if ctx.over() is not None else None
        return no.FunctionCall(name, args=[no.StarExpr()], over=over)

    def visitString(self, ctx: IceSqlParser.StringContext):
        value = unquote(ctx.STRING().getText(), "'")
        return no.String(value)

    def visitTableRelation(self, ctx: IceSqlParser.TableRelationContext):
        return no.Table(self.visit(ctx.qualifiedName()))

    def visitTrue(self, ctx: IceSqlParser.TrueContext):
        return no.ETrue()

    def visitTraversalValueExpression(self, ctx: IceSqlParser.TraversalValueExpressionContext):
        value = self.visit(ctx.valueExpression())
        keys = [self.visit(k) for k in ctx.traversalKey()]
        return no.Traversal(value, keys)

    def visitTypeSpec(self, ctx: IceSqlParser.TypeSpecContext):
        name = self.visit(ctx.identifier())
        args = [self.visit(a) for a in ctx.simpleExpression()]
        return no.TypeSpec(name, args)

    def visitUnaryValueExpression(self, ctx: IceSqlParser.UnaryValueExpressionContext):
        op = no.UNARY_OP_MAP[ctx.op.getText().lower()]
        value = self.visit(ctx.valueExpression())
        return no.UnaryExpr(op, value)

    def visitUnaryBooleanExpression(self, ctx: IceSqlParser.UnaryBooleanExpressionContext):
        op = no.UNARY_OP_MAP[ctx.op.text.lower()]
        value = self.visit(ctx.booleanExpression())
        return no.UnaryExpr(op, value)

    def visitUnboundedFrameBound(self, ctx: IceSqlParser.UnboundedFrameBoundContext):
        precedence = no.Precedence.PRECEDING if ctx.PRECEDING() is not None else no.Precedence.FOLLOWING
        return no.UnboundedFrameBound(precedence)

    def visitUnpivotRelation(self, ctx: IceSqlParser.UnpivotRelationContext):
        relation = self.visit(ctx.relation())
        name_col = self.visit(ctx.nc)
        value_col = self.visit(ctx.vc)
        pivot_cols = [self.visit(c) for c in ctx.identifierList().identifier()]
        return no.Unpivot(
            relation,
            name_col,
            value_col,
            pivot_cols,
        )

    def visitUnquotedIdentifier(self, ctx: IceSqlParser.UnquotedIdentifierContext):
        return no.Identifier(ctx.getText())

    def visitVar(self, ctx: IceSqlParser.VarContext):
        return no.Var(ctx.IDENTIFIER().getText())


def create_parser(buf: str, *, config: ta.Optional[IceSqlParserConfig] = None) -> IceSqlParser:
    lexer = IceSqlLexer(antlr4.InputStream(buf))
    lexer.removeErrorListeners()
    lexer.addErrorListener(antlr.SilentRaisingErrorListener())

    stream = antlr4.CommonTokenStream(lexer)
    stream.fill()

    parser = IceSqlParser(stream)
    if config is not None:
        parser.config = check.isinstance(config, IceSqlParserConfig)
    parser.removeErrorListeners()
    parser.addErrorListener(antlr.SilentRaisingErrorListener())

    return parser


def parse_stmt(buf: str, **kwargs) -> no.Node:
    parser = create_parser(buf, **kwargs)
    node = _ParseVisitor().visit(parser.singleStatement())
    return check.isinstance(node, no.Node)


def parse_expr(buf: str, **kwargs) -> no.Expr:
    parser = create_parser(buf, **kwargs)
    node = _ParseVisitor().visit(parser.expression())
    return check.isinstance(node, no.Expr)


class _DelimitingLexer(antlr.DelimitingLexer, IceSqlLexer):
    pass


def split_stmts(buf: str) -> ta.Sequence[str]:
    lexer = _DelimitingLexer(
        antlr4.InputStream(buf),
        delimiter_token=IceSqlParser.DELIMITER,
        delimiters=[';'],
    )
    lexer.removeErrorListeners()
    lexer.addErrorListener(antlr.SilentRaisingErrorListener())

    lst, part = lexer.split()
    if part.strip():
        raise ValueError(part)

    return [s for s, _ in lst]


def parse_stmts(buf: str, **kwargs) -> ta.Sequence[no.Stmt]:
    return [parse_stmt(sb, **kwargs) for sb in split_stmts(buf)]


def parse_type_spec(buf: str, **kwargs) -> no.TypeSpec:
    parser = create_parser(buf, **kwargs)
    node = _ParseVisitor().visit(parser.typeSpec())
    return check.isinstance(node, no.TypeSpec)


def parse_col_spec(buf: str, **kwargs) -> no.ColSpec:
    parser = create_parser(buf, **kwargs)
    node = _ParseVisitor().visit(parser.colSpec())
    return check.isinstance(node, no.ColSpec)


def parse_query(query: Query, **kwargs) -> no.Node:
    if isinstance(query, AstQuery):
        return query.root
    elif isinstance(query, StrQuery):
        return parse_stmt(query.src, **kwargs)
    else:
        raise TypeError(query)

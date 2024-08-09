import sqlalchemy as sa
import sqlalchemy.ext.compiler


class ParenExpression(sa.sql.expression.UnaryExpression):
    __visit_name__ = 'paren'
    inherit_cache = True


paren = ParenExpression


@sa.ext.compiler.compiles(ParenExpression)
def visit_paren(element, compiler, **kw):
    return '(%s)' % (element.element._compiler_dispatch(compiler),)  # noqa

import sqlalchemy as sa
import sqlalchemy.ext.compiler


class paren(sa.sql.expression.UnaryExpression):  # noqa
    __visit_name__ = 'paren'
    inherit_cache = True


@sa.ext.compiler.compiles(paren)
def _compile_paren(element, compiler, **kw):
    return '(%s)' % (element.element._compiler_dispatch(compiler),)  # noqa

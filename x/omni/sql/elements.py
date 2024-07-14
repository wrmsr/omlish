import re
import typing as ta

import sqlalchemy.ext.compiler  # noqa
import sqlalchemy as sa

from .. import check


VARIABLE_PATTERN = re.compile(r'[A-Za-z_]+')


def variable(name: str, type=None):
    check.arg(VARIABLE_PATTERN.fullmatch(name) is not None)
    return sa.literal_column('@' + name, type)


class SetVariables(sa.sql.expression.Executable, sa.sql.expression.ClauseElement):

    def __init__(
            self,
            updates: ta.List[ta.Tuple[sa.sql.ColumnElement, sa.sql.Selectable]],
    ) -> None:
        super().__init__()
        self.updates = updates


@sa.ext.compiler.compiles(SetVariables)
def visit_set_variables(element, compiler, **kw):
    stmt = 'SET %s' % (
        ', '.join('%s = %s' % (compiler.preparer.format_column(c), v._compiler_dispatch(compiler))
                  for c, v in element.updates),
    )
    return stmt


class ParenExpression(sa.sql.expression.UnaryExpression):

    __visit_name__ = 'paren'


paren = ParenExpression


@sa.ext.compiler.compiles(ParenExpression)
def visit_paren(element, compiler, **kw):
    return '(%s)' % (element.element._compiler_dispatch(compiler),)

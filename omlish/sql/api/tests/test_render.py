from .... import check
from ...backends.mysql.adapters import mysql_adapter
from ...params import ParamStyle
from ...queries import Q
from ..asquery import as_query
from ..dbapi import DbapiAdapter
from ..queries import Query


def _render(stmt, adapter, params=None) -> str:
    return check.isinstance(as_query(stmt, params, adapter=adapter), Query).text


def test_ansi_qmark():
    a = DbapiAdapter(param_style=ParamStyle.QMARK)
    s = Q.select([Q.i.x], Q.n.t, Q.eq(Q.i.x, Q.p.v))
    assert _render(s, a, {Q.p.v: 1}) == 'select "x" from "t" where "x" = ?'


def test_dollar_numeric():
    a = DbapiAdapter(param_style=ParamStyle.DOLLAR_NUMERIC)
    s = Q.select([Q.i.x], Q.n.t, Q.eq(Q.i.x, Q.p.v))
    assert _render(s, a, {Q.p.v: 1}) == 'select "x" from "t" where "x" = $1'


def test_mysql_backtick_and_concat():
    a = mysql_adapter()
    s = Q.select([Q.concat(Q.i.a, Q.i.b)], Q.n.t)
    assert _render(s, a) == 'select concat(`a`, `b`) from `t`'

import pytest

from ...params import ParamStyle
from ...syntax import QuoteStyles
from .. import Adapter
from .. import Q
from ..rendering import render


def test_quote_and_param_style_are_config():
    sel = Q.select([Q.i.id, Q.i.name], Q.n.users, Q.eq(Q.i.id, Q.p.id))

    # ansi / standard - the default
    assert render(sel, param_style=ParamStyle.QMARK).s == \
        'select "id", "name" from "users" where "id" = ?'

    # backtick quoting + pyformat params, purely via config - no renderer subclass
    assert render(sel, adapter=Adapter(
        param_style=ParamStyle.PYFORMAT,
        quote_style=QuoteStyles.BACKTICK,
    )).s == 'select `id`, `name` from `users` where `id` = %(id)s'


def test_insert_quote_and_param_styles():
    ins = Q.insert(['a', 'b'], Q.n.t, [1, Q.p.x])

    assert render(ins, param_style=ParamStyle.QMARK).s == \
        'insert into "t" ("a", "b") values (1, ?)'

    assert render(ins, adapter=Adapter(
        param_style=ParamStyle.NUMERIC,
        quote_style=QuoteStyles.BRACKET,
    )).s == 'insert into [t] ([a], [b]) values (1, :1)'


def test_adapter_xor_kwargs():
    with pytest.raises(TypeError):
        render(Q.select([1]), adapter=Adapter(), param_style=ParamStyle.QMARK)

import pytest  # noqa

from .... import lang
from ...bindings import bind
from ...injector import create_injector
from ...keys import as_key
from ..scopes import ScopeTag
from ..scopes import bind_scope
from ..scopes import bind_scope_seeds
from ..scopes import scoped


def test_scopes():
    foo = ScopeTag('foo')
    i = create_injector(bind(
        bind_scope(foo),
        scoped(foo, 420),
    ))
    i.provide(foo._scope_key).open({})
    assert i[int] == 420


def test_scope_seed():
    foo = ScopeTag('foo')
    i = create_injector(bind(
        bind_scope(foo),
        scoped(foo, lang.typed_lambda(str, x=int)(lambda x: str(x))),
        bind_scope_seeds(foo, int)
    ))
    i.provide(foo._scope_key).open({
        as_key(int): 420,
    })
    assert i[int] == 420
    assert i[str] == '420'

from .... import dataclasses as dc
from .... import lang
from ...bindings import as_
from ...bindings import bind
from ...injector import create_injector
from ...keys import array
from ..private import expose
from ..private import private


@dc.dataclass(frozen=True)
class Foo:
    s: str


def test_private():
    bs = bind(
        private(
            420,
            12.3,
            expose(int),
        ),
        private(
            lang.typed_lambda(str, f=float, foo=Foo)(lambda f, foo: f'{f}! {foo.s}'),
            32.1,
            expose(str),
        ),
        Foo('foo'),
    )
    i = create_injector(bs)
    assert i.provide(int) == 420
    assert i.provide(str) == '32.1! foo'


def test_private_array():
    bs = bind(
        private(
            as_(array(str), 'hi'),
            12.3,
            expose(array(str)),
        ),
        private(
            as_(array(str), lang.typed_lambda(str, f=float, foo=Foo)(lambda f, foo: f'{f}! {foo.s}')),
            32.1,
            expose(array(str)),
        ),
        Foo('foo'),
    )
    i = create_injector(bs)
    assert sorted(i.provide(array(str))) == ['32.1! foo', 'hi']

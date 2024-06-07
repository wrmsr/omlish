from ..private import expose
from ..private import private
from ...bindings import bind
from ...injector import create_injector
from .... import dataclasses as dc
from .... import lang


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
            12.3,
            expose(str),
        ),
        Foo('foo'),
    )
    i = create_injector(bs)
    assert i.provide(int) == 420
    assert i.provide(str) == '12.3! foo'

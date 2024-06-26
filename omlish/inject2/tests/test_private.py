import contextlib
import typing as ta

from ... import dataclasses as dc
from ... import inject2 as inj
from ... import lang


@dc.dataclass(frozen=True)
class Foo:
    s: str


def test_private():
    es = inj.as_elements(
        inj.private(inj.as_elements(
            inj.as_binding(420),
            inj.as_binding(12.3),
            inj.expose(int),
        )),
        inj.private(inj.as_elements(
            inj.as_binding(lang.typed_lambda(str, f=float, foo=Foo)(lambda f, foo: f'{f}! {foo.s}')),
            inj.as_binding(32.1),
            inj.expose(str),
        )),
        inj.as_binding(Foo('foo')),
    )
    i = inj.create_injector(es)
    assert i.provide(int) == 420
    assert i.provide(str) == '32.1! foo'

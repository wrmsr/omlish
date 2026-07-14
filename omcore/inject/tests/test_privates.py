from ... import dataclasses as dc
from ... import inject as inj
from ... import lang


@dc.dataclass(frozen=True)
class Foo:
    s: str


def test_privates():
    i = inj.create_injector(
        inj.Private(inj.as_elements(
            inj.bind(420, expose=True),
            inj.bind(12.3),
        )),
        inj.Private(inj.as_elements(
            inj.bind(lang.typed_lambda(str, f=float, foo=Foo)(lambda f, foo: f'{f}! {foo.s}'), expose=True),
            inj.bind(32.1),
        )),
        inj.bind(Foo('foo')),
    )
    assert i.provide(int) == 420
    assert i.provide(str) == '32.1! foo'

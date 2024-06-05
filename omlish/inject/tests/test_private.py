import typing as ta

from ... import inject as inj  # noqa


class _PrivateBindings(ta.NamedTuple):
    bs: inj.Bindings


def private(*args: ta.Any) -> inj.Binding:
    return inj.as_(inj.array(_PrivateBindings), _PrivateBindings(inj.bind(*args)))


class _ExposedKey(ta.NamedTuple):
    key: inj.Key


def expose(arg: ta.Any) -> inj.Binding:
    return inj.as_(inj.array(_ExposedKey), _ExposedKey(inj.as_key(arg)))


def process_private_bindings(bs: inj.Bindings) -> inj.Bindings:
    raise NotImplementedError


def test_private():
    bs = inj.bind(
        private(
            420,
            12.3,
            expose(int),
        ),
        private(
            'hi',
            12.3,
            expose(str),
        ),
    )
    bs = process_private_bindings(bs)
    i = inj.create_injector(bs)
    assert i.provide(int) == 420
    assert i.provide(str) == 'hi'

import typing as ta

from ... import check
from ... import inject as inj  # noqa


class _PrivateBindings(ta.NamedTuple):
    bs: inj.Bindings


_PRIVATE_ARRAY_KEY = inj.array(_PrivateBindings)


def private(*args: ta.Any) -> inj.Binding:
    return inj.as_(_PRIVATE_ARRAY_KEY, _PrivateBindings(inj.bind(*args)))


class _ExposedKey(ta.NamedTuple):
    key: inj.Key


_EXPOSED_ARRAY_KEY = inj.array(_ExposedKey)


def expose(arg: ta.Any) -> inj.Binding:
    return inj.as_(_EXPOSED_ARRAY_KEY, _ExposedKey(inj.as_key(arg)))


def process_private_bindings(bs: inj.Bindings) -> inj.Bindings:
    def process_private(p: _PrivateBindings):
        raise NotImplementedError

    for b in bs.bindings():
        if b.key == _PRIVATE_ARRAY_KEY:
            process_private(b.provider.provider_fn()(None))

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

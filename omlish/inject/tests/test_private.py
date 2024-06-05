import typing as ta

from ... import inject as inj  # noqa


def private(*args: ta.Any) -> inj.Bindings:
    raise NotImplementedError


class _ExposedKey(ta.NamedTuple):
    key: inj.Key


def expose(*args: ta.Any) -> inj.Bindings:
    return inj.bind(*[inj.as_(inj.array(_ExposedKey), _ExposedKey(inj.as_key(a))) for a in args])


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
    i = inj.create_injector(bs)
    assert i.provide(int) == 420
    assert i.provide(str) == 'hi'

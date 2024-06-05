import typing as ta

from ... import inject as inj  # noqa


class _Eager(ta.NamedTuple):
    key: inj.Key


_EAGER_ARRAY_KEY = inj.array(_Eager)


def test_eager():
    num_calls = 0

    def provide_barf() -> int:
        nonlocal num_calls
        num_calls += 1
        return num_calls

    i = inj.create_injector(inj.bind(
        inj.singleton(provide_barf),
    ))

    assert i.provide(int) == 1
    assert i.provide(int) == 1
    assert num_calls == 1

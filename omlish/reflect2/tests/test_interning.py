import typing as ta

from ..api import global_api


def test_interning():
    a0 = list[int]
    for i in range(1000):
        ta.Literal[i]  # noqa
    a1 = list[int]
    if a0 is a1:
        raise RuntimeError('failed to exhaust typing cache')

    t0 = global_api().reflect_type(a0)
    t1 = global_api().reflect_type(a1)
    assert t0 is t1

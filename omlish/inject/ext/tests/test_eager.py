from .... import inject as inj
from ..eager import create_eager_injector
from ..eager import eager


def test_eager():
    num_calls = 0

    def provide_barf() -> int:
        nonlocal num_calls
        num_calls += 1
        return num_calls

    bs = inj.bind(
        inj.singleton(provide_barf),
        eager(int),
    )

    i = create_eager_injector(inj.create_injector, bs)

    assert num_calls == 1
    assert i.provide(int) == 1
    assert num_calls == 1
    assert i.provide(int) == 1
    assert num_calls == 1

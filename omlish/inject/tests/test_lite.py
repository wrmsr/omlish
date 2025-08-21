from ...lite import inject as lij
from ..injector import create_injector
from ..lite import convert_from_lite


##


def test_lite():
    ifn_n = 0

    def ifn() -> int:
        nonlocal ifn_n
        ifn_n += 1
        return ifn_n

    sfn_n = 0

    def sfn() -> str:
        nonlocal sfn_n
        sfn_n += 1
        return str(sfn_n)

    bs = lij.inj.as_bindings(
        lij.inj.bind(420.),
        lij.inj.bind(ifn),
        lij.inj.bind(sfn, singleton=True),
    )

    i = create_injector(convert_from_lite(bs))
    assert i.provide(float) == 420.
    assert i.provide(int) == 1
    assert i.provide(int) == 2
    assert i.provide(str) == '1'
    assert i.provide(str) == '1'

    def barf(x: int) -> int:
        return x + 1

    assert i.inject(barf) == 4
    assert i.inject(barf) == 5

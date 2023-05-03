from ..bindings import bind
from ..injector import create_injector
from ..providers import FnProvider
from ..providers import SingletonProvider
from ..types import Binding
from ..types import Key


def test_inject():
    def ifn(_):
        nonlocal ifn_n
        ifn_n += 1
        return ifn_n

    ifn_n = 0

    def sfn(_):
        nonlocal sfn_n
        sfn_n += 1
        return str(sfn_n)

    sfn_n = 0

    bs = bind(
        # _as_binding(420),
        Binding(Key(int), FnProvider(int, ifn)),
        Binding(Key(str), SingletonProvider(FnProvider(str, sfn))),
    )

    i = create_injector(bs)
    assert i.try_provide(Key(int)) == 1
    assert i.try_provide(Key(int)) == 2
    assert i.try_provide(Key(str)) == '1'
    assert i.try_provide(Key(str)) == '1'

    def barf(x: int) -> int:
        return x + 1

    assert i.inject(barf) == 4
    assert i.inject(barf) == 5


def test_inject2():
    i = create_injector(bind(420))
    assert i.provide(int) == 420

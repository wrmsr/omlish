import contextlib

from .... import inject as inj
from ..defer import closing


class ClosingThing:
    def close(self):
        print(f'{self} closed')


def test_defer():
    i = inj.create_injector(inj.bind(
        inj.singleton(contextlib.ExitStack),
        closing(ClosingThing),
    ))

    print()
    with i[contextlib.ExitStack] as es:  # noqa
        print(i[ClosingThing])
        print(i[ClosingThing])

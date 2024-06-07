from .... import inject as inj
from ..defer import create_defer_injector
from ..defer import closing


class ClosingThing:
    def close(self):
        print(f'{self} closed')


def test_defer():
    with create_defer_injector(inj.bind(
        closing(ClosingThing),
    )) as i:
        print(i[ClosingThing])
        print(i[ClosingThing])

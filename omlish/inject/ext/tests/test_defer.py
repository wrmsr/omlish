import contextlib
import typing as ta

from .... import inject as inj
from ...bindings import as_binding


def closing(obj: ta.Any) -> inj.Binding:
    b = as_binding(obj)
    return b


class ClosingThing:
    def close(self):
        print(f'{self} closed')


def test_defer():
    i = inj.create_injector(inj.bind(
        inj.singleton(contextlib.ExitStack),
        # closing()
    ))

    with i[contextlib.ExitStack] as es:  # noqa
        pass

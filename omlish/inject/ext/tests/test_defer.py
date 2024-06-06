import contextlib
import typing as ta

from .... import dataclasses as dc
from .... import inject as inj
from .... import lang
from ...providers import as_provider
from ...types import Injector
from ...types import Key
from ...types import Provider
from ...types import ProviderFn


@dc.dataclass(frozen=True)
class ClosingProvider(Provider):
    p: Provider

    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        return self.p.provided_cls(rec)

    def provider_fn(self) -> ProviderFn:
        def pfn(i: Injector) -> ta.Any:
            v = ufn(i)
            i[contextlib.ExitStack].enter_context(lang.defer(v.close))  # noqa
            return v

        ufn = self.p.provider_fn()
        return pfn


def closing(obj: ta.Any) -> inj.Provider:
    return ClosingProvider(as_provider(obj))


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

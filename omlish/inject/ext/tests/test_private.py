import typing as ta

import pytest  # noqa

from .... import dataclasses as dc
from ...bindings import as_
from ...bindings import as_key
from ...bindings import bind
from ...injector import create_injector
from ...keys import array
from ...types import Binding
from ...types import Bindings
from ...types import Key
from ...types import Provider
from ...types import ProviderFn


class _Exposed(ta.NamedTuple):
    key: Key


_EXPOSED_ARRAY_KEY = array(_Exposed)


def expose(arg: ta.Any) -> Binding:
    return as_(_EXPOSED_ARRAY_KEY, _Exposed(as_key(arg)))


@dc.dataclass(frozen=True)
class ExposedPrivateProvider(Provider):
    def provided_cls(self, rec: ta.Callable[[Key], type]) -> type:
        # return self.p.provided_cls(rec)
        raise NotImplementedError

    def required_keys(self) -> frozenset[Key | None]:
        raise NotImplementedError

    def children(self) -> ta.Iterable[Provider]:
        raise NotImplementedError

    def provider_fn(self) -> ProviderFn:
        raise NotImplementedError


@dc.dataclass(frozen=True, eq=False)
class _PrivateBindings(Bindings):
    pbs: Bindings

    def bindings(self) -> ta.Iterator[Binding]:
        raise NotImplementedError


def private(*args: ta.Any) -> Bindings:
    return _PrivateBindings(bind(*args))


def process_private_bindings(bs: Bindings) -> Bindings:
    def process_private(p: _Private):
        for b in p.bs.bindings():
            if b.key == _EXPOSED_ARRAY_KEY:
                raise NotImplementedError

    for b in bs.bindings():
        if b.key == _PRIVATE_ARRAY_KEY:
            process_private(b.provider.provider_fn()(None))  # type: ignore

    raise NotImplementedError


# @pytest.mark.skip('fixme')
def test_private():
    bs = bind(
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
    bs = process_private_bindings(bs)
    i = create_injector(bs)
    assert i.provide(int) == 420
    assert i.provide(str) == 'hi'

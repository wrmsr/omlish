import typing as ta

from .. import Element
from ... import check
from ... import inject as inj
from ... import lang
from ... import reflect as rfl
from ..elements import ElementGenerator


##


T = ta.TypeVar('T')
K = ta.TypeVar('K')
V = ta.TypeVar('V')


class set_binder(ElementGenerator, ta.Generic[T]):
    def __init__(self, *, tag: ta.Any = None) -> None:
        super().__init__()
        self._tag = tag
        self._keys = []

    @lang.cached_property
    def _multi_key(self) -> inj.Key:
        oty = rfl.type_(self.__orig_class__)  # noqa
        ety = check.single(oty.args)
        return inj.Key(ta.AbstractSet[ety], tag=self._tag)

    def bind(self, *keys: ta.Any) -> ta.Self:
        if not isinstance(self, set_binder):
            raise TypeError
        self._keys.extend(inj.as_key(k) for k in keys)
        return self

    def __iter__(self) -> ta.Iterator[Element]:
        raise NotImplementedError


def test_set_binder():
    sb = set_binder[object]().bind(int)
    print(sb._multi_key)


##


def test_set_multi():
    es = inj.as_elements(
        inj.bind_set_provider(ta.AbstractSet[int]),

        inj.bind(420, tag='four twenty'),
        inj.SetBinding(inj.Key(ta.AbstractSet[int]), inj.Key(int, tag='four twenty')),

        inj.bind(421, tag='four twenty one'),
        inj.SetBinding(inj.Key(ta.AbstractSet[int]), inj.Key(int, tag='four twenty one')),
    )

    i = inj.create_injector(es)
    assert i.provide(inj.Key(ta.AbstractSet[int])) == {420, 421}


def test_map_multi():
    es = inj.as_elements(
        inj.bind_map_provider(ta.Mapping[str, int]),

        inj.bind(420, tag='four twenty'),
        inj.MapBinding(inj.Key(ta.Mapping[str, int]), 'a', inj.Key(int, tag='four twenty')),

        inj.bind(421, tag='four twenty one'),
        inj.MapBinding(inj.Key(ta.Mapping[str, int]), 'b', inj.Key(int, tag='four twenty one')),
    )

    i = inj.create_injector(es)
    assert i.provide(inj.Key(ta.Mapping[str, int])) == {'a': 420, 'b': 421}

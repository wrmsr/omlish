import abc
import functools
import typing as ta

from ... import cached
from ... import dataclasses as dc
from ... import inject as inj
from ... import lang


class ThingDoer(lang.Abstract):
    @abc.abstractmethod
    def do_thing(self) -> ta.Sequence:
        raise NotImplementedError


class ConstThingDoer(ThingDoer):
    def __init__(self, *values) -> None:
        self.values = values

    def do_thing(self) -> ta.Sequence:
        return self.values


class ItemAppendingThingDoer(ThingDoer):
    def __init__(self, wrapped: ThingDoer, item: ta.Any) -> None:
        self.wrapped = wrapped
        self.item = item

    def do_thing(self) -> ta.Sequence:
        return [*self.wrapped.do_thing(), self.item]


class ReversingThingDoer(ThingDoer):
    def __init__(self, wrapped: ThingDoer) -> None:
        self.wrapped = wrapped

    def do_thing(self) -> ta.Sequence:
        return list(reversed(self.wrapped.do_thing()))


class SortingThingDoer(ThingDoer):
    def __init__(self, wrapped: ThingDoer) -> None:
        self.wrapped = wrapped

    def do_thing(self) -> ta.Sequence:
        return sorted(self.wrapped.do_thing())


def test_wrappers() -> None:
    thing_doer = ItemAppendingThingDoer(
        wrapped=ReversingThingDoer(
            wrapped=SortingThingDoer(
                wrapped=ConstThingDoer('2', '1', '3'),
            ),
        ),
        item='foo',
    )

    assert list(thing_doer.do_thing()) == ['3', '2', '1', 'foo']


def test_wrappers_injection():
    injector = inj.create_injector(
        inj.bind(ThingDoer, tag=0, to_const=ConstThingDoer('2', '1', '3')),

        inj.private(
            inj.bind(ThingDoer, to_key=inj.Key(ThingDoer, tag=0)),
            inj.bind(ThingDoer, tag=1, to_ctor=SortingThingDoer, expose=True),
        ),

        inj.private(
            inj.bind(ThingDoer, to_key=inj.Key(ThingDoer, tag=1)),
            inj.bind(ThingDoer, tag=2, to_fn=ReversingThingDoer, expose=True),
        ),

        inj.private(
            inj.bind(ThingDoer, to_key=inj.Key(ThingDoer, tag=2)),
            inj.bind(ThingDoer, tag=3, to_fn=functools.partial(ItemAppendingThingDoer, item='foo'), expose=True),
        ),

        inj.bind(ThingDoer, to_key=inj.Key(ThingDoer, tag=3)),
    )

    assert list(injector.provide(inj.Key(ThingDoer, tag=0)).do_thing()) == ['2', '1', '3']
    assert list(injector.provide(inj.Key(ThingDoer, tag=1)).do_thing()) == ['1', '2', '3']
    assert list(injector.provide(inj.Key(ThingDoer, tag=2)).do_thing()) == ['3', '2', '1']
    assert list(injector.provide(inj.Key(ThingDoer, tag=3)).do_thing()) == ['3', '2', '1', 'foo']
    assert list(injector[ThingDoer].do_thing()) == ['3', '2', '1', 'foo']

    assert injector[ThingDoer] is not injector[ThingDoer]


@ta.final
class WrapperBinderHelper:
    def __init__(self, key: ta.Any) -> None:
        self._key = inj.as_key(key)
        self._root = WrapperBinderHelper._Root()
        self._top = WrapperBinderHelper._Level(self._root, 0)

    @dc.dataclass(frozen=True, eq=False)
    @dc.extra_class_params(repr_id=True)
    class _Root:
        pass

    @dc.dataclass(frozen=True)
    class _Level:
        root: 'WrapperBinderHelper._Root'
        level: int

        def next(self) -> 'WrapperBinderHelper._Level':
            return WrapperBinderHelper._Level(self.root, self.level + 1)

        @cached.property
        def key(self) -> inj.Key:
            return inj.Key(ta.Any, tag=self)

    @property
    def top(self) -> inj.Key:
        return self._top.key

    def push_bind(self, **kwargs: ta.Any) -> inj.Elemental:
        prv = self._top
        nxt = prv.next()
        out = inj.private(
            *([inj.bind(self._key, to_key=prv.key)] if prv.level else []),
            inj.bind(nxt.key, **kwargs, expose=True),
        )
        self._top = nxt
        return out


def test_wrapper_helper():
    wbh = WrapperBinderHelper(ThingDoer)
    injector = inj.create_injector(
        wbh.push_bind(to_const=ConstThingDoer('2', '1', '3')),
        wbh.push_bind(to_ctor=SortingThingDoer),
        wbh.push_bind(to_ctor=SortingThingDoer),
        wbh.push_bind(to_ctor=ReversingThingDoer),
        wbh.push_bind(to_fn=functools.partial(ItemAppendingThingDoer, item='foo')),
        inj.bind(ThingDoer, to_key=wbh.top),
    )

    assert list(injector[ThingDoer].do_thing()) == ['3', '2', '1', 'foo']

    assert injector[ThingDoer] is not injector[ThingDoer]

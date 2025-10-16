import abc
import typing as ta

from ... import lang
from ... import inject as inj


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
        inj.bind(ThingDoer, tag=3, to_const=ConstThingDoer('2', '1', '3')),

        inj.private(
            inj.bind(ThingDoer, to_key=inj.Key(ThingDoer, tag=3)),
            inj.bind(ThingDoer, tag=2, to_ctor=SortingThingDoer, expose=True),
        ),
    )
    assert list(injector.provide(inj.Key(ThingDoer, tag=3)).do_thing()) == ['2', '1', '3']
    assert list(injector.provide(inj.Key(ThingDoer, tag=2)).do_thing()) == ['1', '2', '3']
    # assert list(injector[ThingDoer].do_thing()) == ['3', '2', '1', 'foo']

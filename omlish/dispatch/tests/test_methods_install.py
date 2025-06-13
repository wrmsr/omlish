import dataclasses as dc
import typing as ta

import pytest

from ..methods import install_method
from ..methods import method


##


class FrobError(Exception):
    pass


class Frobber:
    @method(installable=True)
    def frob(self, obj: ta.Any) -> ta.Any:
        raise FrobError(obj)


#


@dc.dataclass()
class ThingA:
    pass


class ThingAFrobber(Frobber):
    @Frobber.frob.register
    def frob_thing_a(self, a: ThingA) -> ta.Any:
        return 'a'


#


@dc.dataclass()
class ThingB:
    pass


class ThingBFrobber(Frobber):
    @Frobber.frob.register
    def frob_thing_b(self, b: ThingB) -> ta.Any:
        return 'b'


#


@dc.dataclass()
class ThingC:
    pass


@install_method(Frobber.frob)
def frob_thing_c(self, c: ThingC) -> ta.Any:
    return 'c'


#


@dc.dataclass()
class ThingD:
    pass


@install_method(Frobber.frob, on=ThingBFrobber)
def frob_thing_d(self: Frobber, c: ThingD) -> ta.Any:
    return 'd'


#


class ThingAThingBFrobber(ThingAFrobber, ThingBFrobber):
    pass


#


def test_methods_install():
    f: Frobber = ThingAFrobber()
    assert f.frob(ThingA()) == 'a'
    with pytest.raises(FrobError):
        f.frob(ThingB())
    assert f.frob(ThingC()) == 'c'
    with pytest.raises(FrobError):
        f.frob(ThingD())

    f = ThingBFrobber()
    with pytest.raises(FrobError):
        f.frob(ThingA())
    assert f.frob(ThingB()) == 'b'
    assert f.frob(ThingC()) == 'c'
    assert f.frob(ThingD()) == 'd'

    f = ThingAThingBFrobber()
    assert f.frob(ThingA()) == 'a'
    assert f.frob(ThingB()) == 'b'
    assert f.frob(ThingC()) == 'c'
    assert f.frob(ThingD()) == 'd'

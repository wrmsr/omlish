import dataclasses as dc
import typing as ta

import pytest

from ..methods import install_method
from ..methods import method


##


class BaseFrobError(Exception):
    pass


class BaseFrobber:
    @method(installable=True)
    def frob(self, obj: ta.Any) -> ta.Any:
        raise BaseFrobError(obj)


#


@dc.dataclass()
class ThingA:
    pass


class BaseThingAFrobber(BaseFrobber):
    @BaseFrobber.frob.register
    def frob_thing_a(self, a: ThingA) -> ta.Any:
        return 'a'


#


@dc.dataclass()
class ThingB:
    pass


class BaseThingBFrobber(BaseFrobber):
    @BaseFrobber.frob.register
    def frob_thing_b(self, b: ThingB) -> ta.Any:
        return 'b'


#


@dc.dataclass()
class ThingC:
    pass


@install_method(BaseFrobber.frob)
def frob_thing_c(self, c: ThingC) -> ta.Any:
    return 'c'


#


@dc.dataclass()
class ThingD:
    pass


@install_method(BaseFrobber.frob)
def frob_thing_d(self: BaseFrobber, c: ThingD) -> ta.Any:
    return 'd'


#


class ThingAThingBFrobber(BaseThingAFrobber, BaseThingBFrobber):
    pass


#


def test_methods_install():
    f: BaseFrobber = BaseThingAFrobber()
    assert f.frob(ThingA()) == 'a'
    with pytest.raises(BaseFrobError):
        f.frob(ThingB())
    assert f.frob(ThingC()) == 'c'
    assert f.frob(ThingD()) == 'd'

    f = BaseThingBFrobber()
    with pytest.raises(BaseFrobError):
        f.frob(ThingA())
    assert f.frob(ThingB()) == 'b'
    assert f.frob(ThingC()) == 'c'
    assert f.frob(ThingD()) == 'd'

    f = ThingAThingBFrobber()
    assert f.frob(ThingA()) == 'a'
    assert f.frob(ThingB()) == 'b'
    assert f.frob(ThingC()) == 'c'
    assert f.frob(ThingD()) == 'd'

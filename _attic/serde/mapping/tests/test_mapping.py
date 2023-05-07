import abc
import datetime
import enum
import typing as ta
import uuid

import pytest

from .. import core
from .. import dataclasses as sdc
from .. import simple
from .. import types
from .... import collections as ocol
from .... import dataclasses as dc
from .... import lang
from .... import properties


class Pt(dc.Pure):
    x: int
    y: int


class Box(dc.Frozen):
    lo: Pt
    hi: Pt


class Zbox(Box):
    z: int


def test_serde():
    def rt(o, t=None):
        s = core.serialize(o, t)
        d = core.deserialize(s, t or type(o))
        assert d == o

    rt(2)
    rt(2, ta.Optional[int])
    rt(None, ta.Optional[int])

    class E(enum.Enum):
        A = 'a'
        B = 'b'

    rt(E.A)
    rt(E.B)

    rt([0, 1], ta.Sequence[int])
    rt([0, None], ta.Sequence[ta.Optional[int]])

    rt({0: 1}, ta.Mapping[int, int])
    rt({0: None}, ta.Mapping[int, ta.Optional[int]])

    rt({1, 2}, ta.AbstractSet[int])

    assert core.deserialize([[0, 1], [2, 3]], ta.Mapping[int, int]) == {0: 1, 2: 3}
    assert core.deserialize({0: 1, 2: 3}, ta.Mapping[int, int]) == {0: 1, 2: 3}

    rt(Pt(1, 2))

    rt(Box(Pt(1, 2), Pt(3, 4)))
    rt(Zbox(Pt(1, 2), Pt(3, 4), 5))

    rt(b'abc\0d')
    rt(datetime.datetime.now().date())
    rt(datetime.datetime.now().time())
    rt(datetime.datetime.now())
    rt(uuid.uuid4())

    core.serialize(ocol.FrozenDict({1: 2, 3: 4}), ta.Mapping[int, int])


def test_reraise():
    with pytest.raises(types.DeserializationException):
        core.deserialize(None, int)


class Code(dc.Enum):

    @abc.abstractproperty
    def fn(self) -> ta.Callable:
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        return self.fn(*args, **kwargs)


class Lambda(Code, allow_setattr=True):
    src: str = dc.field(check=lambda s: isinstance(s, str) and ':' in s)

    @properties.cached
    def fn(self) -> ta.Callable:
        return eval('lambda ' + self.src)


class LambdaSerde(simple.AutoSerde[Lambda]):

    def serialize(self, obj: Lambda) -> ta.Any:
        return sdc.serialize_dataclass_fields(obj)

    def deserialize(self, ser: ta.Any) -> Lambda:
        if isinstance(ser, str):
            return Lambda(ser)
        return sdc.deserialize_dataclass_fields(ser, Lambda)


def test_code_serde():
    src = 'x: x + 2'
    lam = Lambda(src)
    assert lam.fn(420) == 422

    assert core.deserialize('x: x + 10', Lambda).fn(20) == 30
    assert core.deserialize({'lambda': 'x: x + 10'}, Code).fn(20) == 30

    s = core.serialize(lam, Code)
    assert s == {'lambda': {'src': src}}
    d = core.deserialize(s, Code)
    assert d.fn(422) == 424

    class Thing0(dc.Pure):
        code: Code

    s = core.serialize(Thing0(lam))
    assert s == {'code': {'lambda': {'src': src}}}
    d = core.deserialize(s, Thing0)
    assert d.code.fn(424) == 426

    class Thing1(dc.Pure):
        lam: Lambda

    s = core.serialize(Thing1(lam))
    assert s == {'lam': {'src': src}}
    d = core.deserialize(s, Thing1)
    assert d.lam.fn(426) == 428


class A(dc.Pure):
    a: ta.Optional['A'] = None


def test_rec():
    sd = core.serde(A)

    a = A(A())

    s = sd.serialize(a)
    d = sd.deserialize(s)

    assert d == a


def test_redact_serde():
    st = lang.redact(datetime.datetime.now())
    sst = core.serialize(st, lang.Redacted[datetime.datetime])
    print(sst)
    assert isinstance(sst, str)
    dst = core.deserialize(sst, lang.Redacted[datetime.datetime])
    print(dst)
    assert dst == st

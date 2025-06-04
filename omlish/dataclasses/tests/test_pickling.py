import dataclasses as dc
import pickle

from .. import api


@dc.dataclass(frozen=True)
class StdFoo:
    s: str


@api.dataclass(frozen=True)
class OmFoo:
    s: str


def test_pickling():
    sf = StdFoo('foo')
    of = OmFoo('foo')  # type: ignore[call-arg]
    assert sf != of

    object.__setattr__(sf, 'x', 420)
    object.__setattr__(of, 'x', 420)
    assert sf.x == 420  # type: ignore[attr-defined]
    assert of.x == 420  # type: ignore[attr-defined]

    sf2 = pickle.loads(pickle.dumps(sf))  # noqa
    of2 = pickle.loads(pickle.dumps(of))  # noqa
    assert sf2 == sf
    assert of2 == of
    assert sf2 != of2

    assert sf2.x == 420
    assert of2.x == 420

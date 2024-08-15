import sys
import types
import typing as ta

from ... import dataclasses as dc
from ... import lang
from ..origins import HasOrigins
from ..origins import Origin
from ..origins import Origins


HasOriginsT = ta.TypeVar('HasOriginsT', bound=HasOrigins)


##


ORIGIN_NUM_FRAMES = 8
ORIGIN_BASE_OFS = 2

ORIGIN_IGNORED_PACKAGES = frozenset([
    __package__,
    __package__.rpartition('.')[0],

    lang.__name__,
    lang.functions.__name__,

    dc.__name__,
    dc.impl.__name__,  # noqa
])


def is_origin_frame(f: types.FrameType) -> bool:
    gl = f.f_globals
    try:
        pkg = gl['__package__']
    except KeyError:
        pass
    else:
        if pkg in ORIGIN_IGNORED_PACKAGES:
            return False
    return True


def build_origin(ofs: int = 0) -> Origin:
    lst = []  # type: ignore
    cur = sys._getframe(ORIGIN_BASE_OFS + ofs)  # noqa
    while len(lst) < ORIGIN_NUM_FRAMES and cur is not None:
        if is_origin_frame(cur):
            lst.append(cur)
        cur = cur.f_back  # type: ignore
    return Origin(tuple(str(f) for f in lst))


##


ORIGINS_ATTR = '__inject_origins__'


def set_origins(obj: HasOriginsT, origins: Origins) -> HasOriginsT:
    obj.__dict__[ORIGINS_ATTR] = origins
    return obj


class HasOriginsImpl(HasOrigins):
    """Note: inheritors must be dataclasses."""

    @property
    def origins(self) -> Origins:
        return self.__dict__[ORIGINS_ATTR]

    def __post_init__(self) -> None:
        dc.maybe_post_init(super())
        if ORIGINS_ATTR in self.__dict__:
            raise AttributeError('Origin already set')
        set_origins(self, Origins((build_origin(),)))

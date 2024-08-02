import sys
import types
import typing as ta

from .. import dataclasses as dc


_ORIGIN_ATTR = '__inject_origin__'


@dc.dataclass(frozen=True)
class Origin:
    lst: ta.Sequence[str]


_ORIGIN_FRAMES = 5
_ORIGIN_BASE_OFS = 2
_ORIGIN_IGNORED_PACKAGES = frozenset([
    __package__,
    __package__ + '.impl',
])


def _is_origin_frame(f: types.FrameType) -> bool:
    gl = f.f_globals
    try:
        pkg = gl['__package__']
    except KeyError:
        pass
    else:
        if pkg in _ORIGIN_IGNORED_PACKAGES:
            return False
    return True


def _build_origin(ofs: int = 0) -> Origin:
    lst = []  # type: ignore
    cur = sys._getframe(_ORIGIN_BASE_OFS + ofs)  # noqa
    while len(lst) < _ORIGIN_FRAMES and cur is not None:
        if _is_origin_frame(cur):
            lst.append(cur)
        cur = cur.f_back  # type: ignore
    return Origin([str(f) for f in lst])


class HasOrigin:
    @property
    def origin(self) -> Origin:
        raise NotImplementedError

    def __post_init__(self) -> None:
        dc.maybe_post_init(super())
        if _ORIGIN_ATTR in self.__dict__:
            raise KeyError('Origin already set')
        self.__dict__[_ORIGIN_ATTR] = _build_origin()

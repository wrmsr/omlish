# ruff: noqa: SLF001
import abc
import typing as ta

from .. import check
from .. import lang


if ta.TYPE_CHECKING:
    from . import sessions as _sessions
else:
    _sessions = lang.proxy_import('.sessions', __package__)


T = ta.TypeVar('T')


##


class _BoundBackref(lang.Final, ta.Generic[T]):
    def __call__(self) -> ta.Sequence[T]:
        raise NotImplementedError


class Backref(lang.Sealed, lang.Abstract, ta.Generic[T]):
    @ta.overload
    def __get__(self, instance: None, owner: ta.Any = None) -> 'Backref[T]':
        ...

    @ta.overload
    def __get__(self, instance: ta.Any, owner: ta.Any = None) -> _BoundBackref[T]:
        raise NotImplementedError

    @abc.abstractmethod
    def __get__(self, instance, owner=None):
        raise NotImplementedError


#


@ta.final
class _Backref(Backref[T], lang.Final):
    def __init__(self, binder: ta.Callable[[], ta.Any]) -> None:  # noqa
        self._binder = check.callable(binder)

    def __repr__(self) -> str:
        return f'orm.backref@{id(self):x}()'

    def __get__(self, instance, owner=None):
        if instance is None:
            return self

        return _sessions.active_session()._get_backref_objs(self)


##


def backref(binder: ta.Callable[[], ta.Any]) -> Backref:
    return _Backref(binder)


##


_BACKREF_TYPES: tuple[type, ...] = (
    _BoundBackref,
    _Backref,
)

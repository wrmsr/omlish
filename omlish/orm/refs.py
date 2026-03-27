import abc
import typing as ta

from .. import check
from .. import lang
from .keys import _KEY_TYPES
from .keys import Key
from .keys import key


if ta.TYPE_CHECKING:
    from . import sessions as _sessions
else:
    _sessions = lang.proxy_import('.sessions', __package__)


K = ta.TypeVar('K')
T = ta.TypeVar('T')


##


class Ref(lang.Sealed, lang.Abstract, ta.Generic[K, T]):
    @property
    @abc.abstractmethod
    def cls(self) -> type[T]:
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def k(self) -> Key[K]:
        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self) -> T:
        raise NotImplementedError

    _hash: int

    @ta.final
    def __hash__(self):
        try:
            return self._hash
        except AttributeError:
            pass
        self._hash = h = hash((self.cls, self.k))
        return h

    @ta.final
    def __eq__(self, other):
        if self is other:
            return True
        ot = other.__class__
        if ot not in _REF_TYPES:
            return False
        return ot.cls == self.cls and ot.k == self.k


#


class UnloadedRefError(Exception):
    pass


@ta.final
class _LazyRef(Ref[K, T], lang.Final):
    def __init__(self, cls: type[T], k: Key[K]) -> None:  # noqa
        check.in_(k.__class__, _KEY_TYPES)
        self._cls, self._k = cls, k

    def __repr__(self) -> str:
        return f'orm.ref({self._cls.__name__}, {self._k!r})'

    @property
    def cls(self) -> type[T]:
        return self._cls

    @property
    def k(self) -> Key[K]:
        return self._k

    def __call__(self) -> T:
        if (session := _sessions.opt_active_session()) is not None:
            return session._load_lazy_ref(self)  # noqa
        raise UnloadedRefError


##


@ta.overload
def ref(obj: T) -> Ref[K, T]:
    ...


@ta.overload
def ref(cls: type[T], k: Key[K]) -> Ref[K, T]:
    ...


@ta.overload
def ref(cls: type[T], k: K) -> Ref[K, T]:
    ...


def ref(obj, *args):
    if not args:
        check.not_isinstance(obj, type)
        raise NotImplementedError
    else:
        check.isinstance(obj, type)
        [k] = args
        return _LazyRef(obj, key(k))


##


_REF_TYPES: tuple[type[Ref], ...] = (
    _LazyRef,
)

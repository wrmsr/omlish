import typing as ta

from .. import check
from .. import collections as ocol


T = ta.TypeVar('T')
U = ta.TypeVar('U')


class MemoizedUnary(ta.Generic[T, U]):

    def __init__(
            self,
            fn: ta.Callable[[T], U],
            *,
            identity: bool = False,
            on_compute: ta.Optional[ta.Callable[[T], U]] = None,
            name: ta.Optional[str] = None,
            max_recursion: ta.Optional[int] = None,
    ) -> None:
        super().__init__()

        self._fn = check.not_none(fn)
        self._identity = identity
        self._on_compute = on_compute
        self._name = name
        self._max_recursion = max_recursion

        self._dct: ta.MutableMapping[T, U] = ocol.IdentityKeyDict() if identity else {}
        self._recursion = 0

    def __set_name__(self, owner, name):
        if self._name is not None:
            check.state(name == self._name)
        else:
            self._name = check.not_empty(name)

    @property
    def dct(self) -> ta.Mapping[T, U]:
        return self._dct

    def __get__(self, instance, owner=None):
        if self._name:
            try:
                return instance.__dict__[self._name]  # FIXME: why
            except KeyError:
                pass
        obj = type(self)(
            self._fn.__get__(instance, owner),
            identity=self._identity,
            on_compute=self._on_compute,
            name=self._name,
            max_recursion=self._max_recursion,
        )
        if instance is not None:
            check.not_empty(self._name)
            instance.__dict__[self._name] = obj
        return obj

    def __call__(self, arg: T) -> U:
        try:
            return self._dct[arg]
        except KeyError:
            try:
                self._recursion += 1
                if self._max_recursion is not None:
                    check.state(self._recursion < self._max_recursion)
                v = self._dct[arg] = self._fn(arg)
            finally:
                self._recursion -= 1
            if self._on_compute is not None:
                self._on_compute(arg, v)
            return v


memoized_unary = MemoizedUnary

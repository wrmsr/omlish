"""
TODO:
 - patch lock
 - thread / context local gating
"""
import contextlib
import functools
import typing as ta

from omlish import check
from omlish import lang


##


class _PatchedMethodDescriptor:
    def __init__(self, old, new, *, mode) -> None:
        super().__init__()

        self._old = old
        self._new = new
        self._mode = mode

    def __get__(self, instance, owner=None):
        old = self._old.__get__(instance, owner)
        new = self._new.__get__(instance, owner)

        if self._mode == 'partial':
            return functools.partial(new, old)

        elif self._mode == 'inner':
            def inner(*args, **kwargs):
                return new(old, *args, **kwargs)
            return inner

        else:
            raise ValueError(self._mode)


@contextlib.contextmanager
def patch_method_context(
        cls: type,
        name: str,
        new: ta.Any,
        *,
        find_mro: bool = False,
        mode: ta.Literal['partial', 'inner'] = 'partial',
) -> ta.Iterator[None]:
    check.isinstance(cls, type)

    get: ta.Callable[[], tuple[type, ta.Any]]
    rpl: lang.Maybe[ta.Any]

    if find_mro:
        def get():
            mro_dct = lang.mro_owner_dict(cls)
            return mro_dct[name]

        tgt, old = get()
        rpl = lang.just(old)

    else:
        def get():
            return cls, object.__getattribute__(cls, name)

        tgt, old = get()
        if name in cls.__dict__:
            check.is_(cls.__dict__[name], old)
            rpl = lang.just(old)
        else:
            rpl = lang.empty()

    dsc = _PatchedMethodDescriptor(old, new, mode=mode)
    setattr(tgt, name, dsc)

    try:
        yield

    finally:
        _, cur = get()
        check.is_(cur, dsc)

        if rpl.present:
            setattr(tgt, name, rpl.must())
        else:
            delattr(tgt, name)

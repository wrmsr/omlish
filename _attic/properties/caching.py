"""
TODO:
 - ** rename to memoized? does not invalidate.. **
 - properties.init? eager cached, ~ideally~ automatically on __init__
  - not really possible without explicit help/call or baseclass
 - codegen: simp this
  - closure..
"""
import abc
import functools
import textwrap
import typing as ta

from .. import lang
from .. import pydevd
from .base import Property


T = ta.TypeVar('T')


def _mangle(s: str) -> str:
    for r in '.<>$':
        s = s.replace(r, '__')
    return s


class _GetterProperty(Property[T], lang.Abstract):

    def __new__(
            cls,
            func: ta.Callable[[ta.Any], T],
            *args,
            lock: lang.DefaultLockable = None,
            stateful: bool = False,
            **kwargs
    ):
        func = cls._unwrap(func)
        lock = lang.default_lock(lock, False)
        stateful = bool(stateful)

        __get__ = cls._build_getter(
            func,
            *args,
            lock=lock,
            stateful=stateful,
            **kwargs
        )

        bcls = type(
            cls.__name__,
            (cls,),
            {
                '__get__': __get__,
                '__new__': super().__new__,
            },
        )

        return bcls.__new__(bcls)

    def __init__(
            self,
            func: ta.Callable[[ta.Any], T],
            *,
            lock: lang.DefaultLockable = None,
            stateful: bool = False,
    ) -> None:
        super().__init__()

        functools.update_wrapper(self, func)
        self._func = func
        self._lock = lock
        self._stateful = stateful

        self._name: ta.Optional[str] = None

    def __set_name__(self, owner, name):
        if self._name is None:
            self._name = name
        elif name != self._name:
            raise TypeError(f'Cannot assign the two different names ({self._name!r} and {name!r}).')

    @classmethod
    def _name_getter(cls, func: ta.Callable) -> str:
        try:
            co = func.__code__
            glo = func.__globals__
            suffix = f'{glo["__name__"]}__{co.co_firstlineno}'
        except Exception:  # noqa
            suffix = hex(id(func))[2:]
        return _mangle(f'_{cls.__name__}__get__{func.__name__}__{suffix}')

    @abc.abstractclassmethod
    def _build_getter(
            cls,
            func: ta.Callable[[ta.Any], T],
            *args,
            lock: lang.DefaultLockable = None,
            stateful: bool = False,
            **kwargs
    ) -> ta.Callable[[object, object], T]:
        raise NotImplementedError


class CachedProperty(_GetterProperty[T]):

    @classmethod
    def _build_getter(
            cls,
            func: ta.Callable[[ta.Any], T],
            *,
            lock: lang.DefaultLockable = None,
            stateful: bool = False,
    ) -> ta.Callable[[object, object], T]:
        fn_name = cls._name_getter(func)
        ns = {
            'fn_name': fn_name,
            'T': T,
            'forbid_debugger_call': pydevd.forbid_debugger_call,
            'lock': lock,
            'func': func,
        }

        body = (
            f'def {fn_name}(self, instance, owner=None) -> T:\n'
            f'    if instance is None:\n'
            f'        return self\n'
        )

        if stateful:
            body += (
                f'    forbid_debugger_call()\n'
            )

        block = (
            f'    try:\n'
            f'        value = instance.__dict__[self._name]\n'
            f'    except KeyError:\n'
            f'        value = instance.__dict__[self._name] = func(instance)\n'
        )

        if not isinstance(lock, lang.NopContextManager):
            body += (
                f'    with lock():\n'
            )
            body += textwrap.indent(block, '    ')
        else:
            body += block

        body += (
            f'    return value\n'
        )

        exec(body, ns)

        return ns[fn_name]


def cached(fn: ta.Callable[..., T]) -> T:
    return CachedProperty(fn)


def locked_cached(fn: ta.Callable[..., T]) -> T:
    return CachedProperty(fn, lock=True)


def stateful_cached(fn: ta.Callable[..., T]) -> T:
    return CachedProperty(fn, stateful=True)


class CachedClassProperty(_GetterProperty[T]):

    @classmethod
    def _unwrap(cls, fn):
        if isinstance(fn, classmethod):
            return fn.__func__
        return super()._unwrap(fn)

    @classmethod
    def _build_bound(
            cls,
            func: ta.Callable[[ta.Any], T],
            get: ta.Callable,
            owner: type,
            value: T,
    ) -> type:
        fn_name = cls._name_getter(func) + '__bound__' + _mangle(owner.__qualname__)
        ns = {
            'T': T,
            'owner': owner,
            'value': value,
            'get': get,
        }

        exec(
            (
                f'def {fn_name}(self, binstance, bowner=None) -> T:\n'
                f'    if bowner is owner:\n'
                f'        return value\n'
                f'    else:\n'
                f'        return get(binstance, bowner)\n'
            ),
            ns,
        )

        return type(
            fn_name,
            (object,),
            {
                '__get__': ns[fn_name],
                '_value': value,
            }
        )()

    @classmethod
    def _build_getter(
            cls,
            func: ta.Callable[[ta.Any], T],
            *,
            lock: lang.DefaultLockable = None,
            stateful: bool = False,
    ) -> ta.Callable[[object, object], T]:
        fn_name = cls._name_getter(func)
        ns = {
            'T': T,
            'forbid_debugger_call': pydevd.forbid_debugger_call,
            'lock': lock,
            'func': func,
            '_build_bound': cls._build_bound,
            'cls': cls,
        }

        body = (
            f'def {fn_name}(self, instance, owner=None) -> T:\n'
            f'    if owner is None:\n'
            f'        return func(owner)\n'
        )

        if stateful:
            body += (
                f'    forbid_debugger_call()\n'
            )

        block = (
            f'    try:\n'
            f'        bound = owner.__dict__[self._name]\n'
            f'    except KeyError:\n'
            f'        bound = None\n'
            f'    if bound is None or bound is self:\n'
            f'        bound = _build_bound(func, {fn_name}.__get__(self, cls), owner, func(owner))\n'
            f'        setattr(owner, self._name, bound)\n'
        )

        if not isinstance(lock, lang.NopContextManager):
            body += (
                f'    with lock():\n'
            )
            body += textwrap.indent(block, '    ')
        else:
            body += block

        body += (
            f'    return bound._value\n'
        )

        exec(body, ns)

        return ns[fn_name]


def cached_class(fn: ta.Callable[..., T]) -> T:
    return CachedClassProperty(fn)


def locked_cached_class(fn: ta.Callable[..., T]) -> T:
    return CachedClassProperty(fn, lock=True)


def stateful_cached_class(fn: ta.Callable[..., T]) -> T:
    return CachedClassProperty(fn, stateful=True)

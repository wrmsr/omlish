"""
TODO:
 - weakrefs to cells, close over hard owner ref
"""
import functools
import typing as ta
import weakref

from .. import check
from .. import lang
from .dispatch import Dispatcher
from .dispatch import _get_impl_cls_set


T = ta.TypeVar('T')


class Method:
    def __init__(self, func: ta.Callable) -> None:
        if not callable(func) and not hasattr(func, '__get__'):  # type: ignore
            raise TypeError(f'{func!r} is not callable or a descriptor')

        self._func = func

        self._impls: ta.MutableSet[ta.Callable] = weakref.WeakSet()
        self._dispatches_by_cls: ta.MutableMapping[type, ta.Callable[[type], ta.Callable]] = weakref.WeakKeyDictionary()

        # bpo-45678: special-casing for classmethod/staticmethod in Python <=3.9, as functools.update_wrapper doesn't
        # work properly in singledispatchmethod.__get__ if it is applied to an unbound classmethod/staticmethod
        unwrapped_func: ta.Any
        if isinstance(func, (staticmethod, classmethod)):
            unwrapped_func = func.__func__  # type: ignore
        else:
            unwrapped_func = func
        self._unwrapped_func = unwrapped_func

        self._is_abstractmethod = getattr(func, '__isabstractmethod__', False)  # noqa

        self._owner: ta.Any = None
        self._name: ta.Optional[str] = None
        self._accessor_cls: ta.Optional[type] = None

    def __set_name__(self, owner, name):
        check.none(self._owner)
        check.none(self._name)
        check.none(self._accessor_cls)

        check.isinstance(owner, type)
        check.non_empty_str(name)

        ex = owner.__dict__[name]
        check.state(ex is self)

        self._owner = owner
        self._name = name

        accessor_cls = self._build_accessor_cls(owner)
        self._accessor_cls = accessor_cls
        acc = accessor_cls(None, owner)
        acc.register = self.register
        setattr(owner, name, acc)

    def _build_accessor_cls(self, owner: type) -> type:
        name = check.non_empty_str(self._name)
        method_owner = check.not_none(owner)
        method_get_dispatch = self.get_dispatch

        def __init__(accessor, instance: ta.Any, owner: type) -> None:
            accessor._instance = instance
            accessor._owner = owner

        def __get__(accessor, instance, owner=None):
            self_instance = accessor._instance  # noqa
            self_owner = accessor._owner  # noqa
            if instance is self_instance and owner is self_owner:
                return accessor

            nxt = accessor_cls(instance, owner)  # noqa

            if instance is not None:
                instance.__dict__[name] = nxt  # noqa

                inst_cls = type(instance)
                try:
                    inst_cls.__dict__[name]

                except KeyError:
                    for mro_cls in inst_cls.__mro__[:-1]:
                        try:
                            mro_cls.__dict__[name]
                        except KeyError:
                            if issubclass(mro_cls, method_owner):
                                setattr(owner, name, accessor_cls(None, mro_cls))

                else:
                    if self_owner is not inst_cls:
                        raise TypeError('super() not supported')  # FIXME

            elif owner is not None:
                setattr(owner, name, nxt)

            else:
                raise TypeError

            return nxt

        def __call__(accessor, *args, **kwargs):
            impl = method_get_dispatch(accessor_owner := accessor._owner)(type(args[0])).__get__(accessor._instance, accessor_owner)  # noqa
            return impl(*args, **kwargs)

        accessor_cls = lang.new_type(
            type(self).__name__ + '$Accessor',
            (),
            {
                '__qualname__': type(self).__qualname__ + '$Accessor',
                '__init__': __init__,
                '__get__': __get__,
                '__call__': __call__,
            },
        )
        self.update_wrapper(accessor_cls)

        return accessor_cls

    def register(self, impl: T) -> T:
        # bpo-39679: in Python <= 3.9, classmethods and staticmethods don't inherit __annotations__ of the wrapped
        # function (fixed in 3.10+ as a side-effect of bpo-43682) but we need that for annotation-derived
        # singledispatches. So we add that just-in-time here.
        if isinstance(impl, (staticmethod, classmethod)):
            impl.__annotations__ = getattr(impl.__func__, '__annotations__', {})

        check.callable(impl)
        if impl not in self._impls:
            self._impls.add(impl)  # type: ignore
            self._dispatches_by_cls.clear()

        return impl

    def get_dispatch(self, cls: type) -> ta.Callable[[type], ta.Callable]:
        try:
            return self._dispatches_by_cls[cls]
        except KeyError:
            pass

        disp = Dispatcher()
        disp.register(self._func, [object])

        for mro_cls in cls.__mro__[1::-1]:
            for nam, att in mro_cls.__dict__.items():
                if att in self._impls:
                    disp.register(att, _get_impl_cls_set(att))

        ret = disp.dispatch
        self._dispatches_by_cls[cls] = ret
        return ret

    def update_wrapper(self, wrapper):
        for attr in functools.WRAPPER_ASSIGNMENTS:
            try:
                value = getattr(self._unwrapped_func, attr)
            except AttributeError:
                pass
            else:
                setattr(wrapper, attr, value)

        setattr(wrapper, '__isabstractmethod__', self._is_abstractmethod)  # noqa

        return wrapper

    def __get__(self, instance, owner=None):
        @self.update_wrapper
        def method(*args, **kwargs):  # noqa
            impl = self.get_dispatch(owner)(type(args[0])).__get__(instance, owner)  # noqa
            return impl(*args, **kwargs)  # noqa

        return method


def method(func):
    return Method(func)

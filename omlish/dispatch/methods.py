"""
TODO:
 - .super(instance[_cls], owner)
 - ALT: A.f(super(), ... ? :/
 - classmethod/staticmethod
"""
import contextlib
import functools
import typing as ta
import weakref

from .. import check
from .. import lang
from .dispatch import Dispatcher
from .dispatch import get_impl_func_cls_set


T = ta.TypeVar('T')


class Method:
    def __init__(self, func: ta.Callable) -> None:
        if not callable(func) and not hasattr(func, '__get__'):  # type: ignore
            raise TypeError(f'{func!r} is not callable or a descriptor')

        self._func = func

        self._impls: ta.MutableSet[ta.Callable] = weakref.WeakSet()

        # bpo-45678: special-casing for classmethod/staticmethod in Python <=3.9, as functools.update_wrapper doesn't
        # work properly in singledispatchmethod.__get__ if it is applied to an unbound classmethod/staticmethod
        unwrapped_func: ta.Any
        if isinstance(func, (staticmethod, classmethod)):
            unwrapped_func = func.__func__
        else:
            unwrapped_func = func
        self._unwrapped_func = unwrapped_func
        self._is_abstractmethod = getattr(func, '__isabstractmethod__', False)  # noqa
        self.update_wrapper(self)

        self._dispatch_func_cache: dict[ta.Any, ta.Callable] = {}

        def dispatch_func_cache_remove(k, self_ref=weakref.ref(self)):
            if (ref_self := self_ref()) is not None:
                cache = ref_self._dispatch_func_cache  # noqa
                with contextlib.suppress(KeyError):
                    del cache[k]

        self._dispatch_func_cache_remove = dispatch_func_cache_remove

    def __repr__(self) -> str:
        return f'<{type(self).__module__}.{type(self).__qualname__}:{self._func} at 0x{id(self):x}>'

    def update_wrapper(self, wrapper: T) -> T:
        for attr in functools.WRAPPER_ASSIGNMENTS:
            try:
                value = getattr(self._unwrapped_func, attr)
            except AttributeError:
                continue
            setattr(wrapper, attr, value)
        setattr(wrapper, '__isabstractmethod__', self._is_abstractmethod)  # noqa
        return wrapper

    def register(self, impl: T) -> T:
        # bpo-39679: in Python <= 3.9, classmethods and staticmethods don't inherit __annotations__ of the wrapped
        # function (fixed in 3.10+ as a side-effect of bpo-43682) but we need that for annotation-derived
        # singledispatches. So we add that just-in-time here.
        if isinstance(impl, (staticmethod, classmethod)):
            impl.__annotations__ = getattr(impl.__func__, '__annotations__', {})

        check.callable(impl)
        if impl not in self._impls:
            self._impls.add(impl)  # type: ignore
            self._dispatch_func_cache.clear()

        return impl

    def build_attr_dispatcher(self, instance_cls: type, owner_cls: type | None = None) -> Dispatcher[str]:
        disp: Dispatcher[str] = Dispatcher()

        mro_dct = lang.build_mro_dict(instance_cls, owner_cls)
        seen: ta.Mapping[ta.Any, str] = {}
        for nam, att in mro_dct.items():
            if att in self._impls:
                try:
                    ex_nam = seen[att]
                except KeyError:
                    pass
                else:
                    raise TypeError(f'Duplicate impl: {owner_cls} {instance_cls} {nam} {ex_nam}')
                disp.register(nam, get_impl_func_cls_set(att))

        return disp

    def build_dispatch_func(self, disp: Dispatcher[str]) -> ta.Callable:
        dispatch = disp.dispatch
        type_ = type
        getattr_ = getattr
        base_func = self._func
        func_name = getattr(base_func, '__name__', 'singledispatch method')

        def __call__(self, *args, **kwargs):  # noqa
            if not args:
                raise TypeError(f'{func_name} requires at least 1 positional argument')
            if (impl_att := dispatch(type_(args[0]))) is not None:
                fn = getattr_(self, impl_att)
                return fn(*args, **kwargs)
            return base_func.__get__(self)(*args, **kwargs)  # noqa

        self.update_wrapper(__call__)
        return __call__

    def get_dispatch_func(self, instance_cls: type) -> ta.Callable:
        cls_ref = weakref.ref(instance_cls)
        try:
            return self._dispatch_func_cache[cls_ref]
        except KeyError:
            pass
        del cls_ref

        att_disp = self.build_attr_dispatcher(instance_cls)
        func = self.build_dispatch_func(att_disp)
        self._dispatch_func_cache[weakref.ref(instance_cls, self._dispatch_func_cache_remove)] = func
        return func

    def __get__(self, instance, owner=None):
        if instance is None:
            # FIXME: classmethod/staticmethod
            return self

        instance_cls = type(instance)
        try:
            func = self._dispatch_func_cache[weakref.ref(instance_cls)]
        except KeyError:
            func = self.get_dispatch_func(instance_cls)
        return func.__get__(instance, owner)  # noqa

    def __call__(self, instance, *args, **kwargs):
        instance_cls = type(instance)
        try:
            func = self._dispatch_func_cache[weakref.ref(instance_cls)]
        except KeyError:
            func = self.get_dispatch_func(instance_cls)
        return func.__get__(instance)(*args, **kwargs)  # noqa


def method(func):  # noqa
    return Method(func)

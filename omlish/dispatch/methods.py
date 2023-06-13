"""
TODO:
 - ALT: A.f(super(), ... ? :/
 - *** __call__
 - classmethod/staticmethod
"""
import functools
import typing as ta
import weakref

from .. import check
from .dispatch import Dispatcher
from .dispatch import get_impl_func_cls_set


T = ta.TypeVar('T')


def build_mro_dct(instance_cls: type, owner_cls: ta.Optional[type] = None) -> ta.Mapping[str, ta.Any]:
    if owner_cls is None:
        instance_cls = owner_cls
    mro = instance_cls.__mro__[-2::-1]
    try:
        pos = mro.index(owner_cls)
    except ValueError:
        raise TypeError(f'Owner class {owner_cls} not in mro of instance class {instance_cls}')
    dct: ta.Dict[str, ta.Any] = {}
    for cur_cls in mro[:pos + 1]:
        dct.update(cur_cls.__dict__)
    return dct


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
            unwrapped_func = func.__func__  # type: ignore
        else:
            unwrapped_func = func
        self._unwrapped_func = unwrapped_func
        self._is_abstractmethod = getattr(func, '__isabstractmethod__', False)  # noqa

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
            # for acc_cls in self._accessor_map.values():
            #     acc_cls._invalidate()  # noqa

        return impl

    def build_attr_dispatcher(self, owner_cls: type, instance_cls: type) -> Dispatcher[str]:
        disp: Dispatcher[str] = Dispatcher()

        mro_dct = build_mro_dct(instance_cls, owner_cls)
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

        def __call__(self, *args, **kwargs):  # noqa
            if (impl_att := dispatch(type_(args[0]))) is not None:
                return getattr_(self, impl_att)(*args, **kwargs)
            return base_func.__get__(self)(*args, **kwargs)  # noqa

        self.update_wrapper(__call__)
        return __call__

    def __get__(self, instance, owner=None):
        if instance is None:
            # FIXME: classmethod/staticmethod
            return self

        if owner is None:
            owner = type(instance)

        att_disp = self.build_attr_dispatcher(owner, type(instance))
        return self.build_dispatch_func(att_disp).__get__(instance, owner)


def method(func):
    return Method(func)

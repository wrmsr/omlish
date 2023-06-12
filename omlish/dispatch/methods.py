"""
TODO:
 - ***** INSTALL, AND INTO PARENTS
 - ** non-weakkeymap hit in accessor_cls for when instance_cls is owner_cls
 - classmethod/staticmethod
"""
import functools
import typing as ta
import weakref

from .. import check
from .. import lang
from .dispatch import Dispatcher
from .dispatch import get_impl_func_cls_set


T = ta.TypeVar('T')


def build_mro_dct(owner_cls: type, instance_cls: type) -> ta.Mapping[str, ta.Any]:
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

        self._accessor_map: ta.MutableMapping[type, ta.Any] = weakref.WeakKeyDictionary()

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
            for acc_cls in self._accessor_map.values():
                acc_cls._invalidate()  # noqa

        return impl

    def build_attr_dispatcher(self, owner_cls: type, instance_cls: type) -> Dispatcher[str]:
        disp: Dispatcher[str] = Dispatcher()
        disp.register(self._func, [object])

        mro_dct = build_mro_dct(owner_cls, instance_cls)
        for nam, att in mro_dct.__dict__.items():
            if att in self._impls:
                disp.register(nam, get_impl_func_cls_set(att))

        return disp

    def _build_dispatch_func(self, disp: Dispatcher[str]) -> ta.Callable:
        dispatch = disp.dispatch
        type_ = type
        getattr_ = getattr

        def __call__(self, *args, **kwargs):  # noqa
            return getattr_(self, dispatch(type_(args[0])))(*args, **kwargs)

        self.update_wrapper(__call__)
        return __call__

    def _get_accessor(self, owner_cls: type) -> ta.Any:
        try:
            return self._accessor_map[owner_cls]
        except KeyError:
            pass

        main_func: ta.Optional[ta.Callable] = None
        funcs_by_instance_cls: ta.MutableMapping[type, ta.Callable] = weakref.WeakKeyDictionary()

        def invalidate(accessor):
            nonlocal main_func
            main_func = None
            funcs_by_instance_cls.clear()

        def __get__(accessor, instance, owner=None):
            raise NotImplementedError

        def __call__(accessor, *args, **kwargs):
            raise NotImplementedError

        cls_suffix = f'<{owner_cls.__qualname__}>'
        accessor_cls = lang.new_type(
            type(self).__name__ + cls_suffix,
            (),
            {
                '__qualname__': type(self).__qualname__ + cls_suffix,
                '__get__': __get__,
                '__call__': __call__,
                '_method': self,
                '_invalidate': invalidate,
            },
        )
        self.update_wrapper(accessor_cls)

        accessor = accessor_cls()
        self._accessor_map[owner_cls] = accessor
        return accessor

    def __get__(self, instance, owner=None):
        if owner is None:
            if instance is None:
                raise TypeError
            owner = type(instance)
        return self._get_accessor(owner).__get__(instance, owner)


def method(func):
    return Method(func)

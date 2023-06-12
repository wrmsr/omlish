"""
TODO:
 - ** non-weakkeymap hit in accessor_cls for when instance_cls is owner_cls
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

        self._accessor_cls_map: ta.MutableMapping[type, type] = weakref.WeakKeyDictionary()

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
            for acc_cls in self._accessor_cls_map.values():
                acc_cls._invalidate()  # noqa

        return impl

    def build_attr_dispatch(self, owner_cls: type, instance_cls: type) -> ta.Callable[[type], str]:
        disp: Dispatcher[str] = Dispatcher()
        disp.register(self._func, [object])

        mro_dct = build_mro_dct(owner_cls, instance_cls)
        for nam, att in mro_dct.__dict__.items():
            if att in self._impls:
                disp.register(nam, get_impl_func_cls_set(att))

        return disp.dispatch

    def _build_accessor_cls(self, owner_cls: type) -> type:
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

    def __get__(self, instance, owner=None):
        @self.update_wrapper
        def method(*args, **kwargs):  # noqa
            impl = self.get_dispatch(owner)(type(args[0])).__get__(instance, owner)  # noqa
            return impl(*args, **kwargs)  # noqa

        return method


def method(func):
    return Method(func)

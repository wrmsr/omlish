"""
TODO:
 - ***** INSTALL, AND INTO PARENTS
 - *** __call__
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

        mro_dct = build_mro_dct(owner_cls, instance_cls)
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

    def _build_dispatch_func(self, disp: Dispatcher[str]) -> ta.Callable:
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

    class _Accessor:
        pass

    def _get_accessor(self, owner_cls: type) -> ta.Any:
        try:
            return self._accessor_map[owner_cls]
        except KeyError:
            pass

        main_func: ta.Optional[ta.Callable] = None
        funcs_by_instance_cls: ta.MutableMapping[type, ta.Callable] = weakref.WeakKeyDictionary()

        def build_func(instance_cls: type) -> ta.Callable:
            att_disp = self.build_attr_dispatcher(owner_cls, instance_cls)
            return self._build_dispatch_func(att_disp)

        def invalidate(accessor):
            nonlocal main_func
            main_func = None
            funcs_by_instance_cls.clear()

        type_ = type

        def __get__(accessor, instance, owner=None):
            if instance is None:
                return self.__get__(instance, owner)

            instance_cls = type_(instance)
            if owner is None:
                if instance is None:
                    raise TypeError
                owner = instance_cls

            if owner is not owner_cls:
                return self.__get__(instance, owner)

            if instance_cls is owner_cls:
                nonlocal main_func
                if main_func is None:
                    main_func = build_func(owner_cls)
                return main_func.__get__(instance, owner)  # noqa

            try:
                func = funcs_by_instance_cls[instance_cls]
            except KeyError:
                func = funcs_by_instance_cls[instance_cls] = build_func(instance_cls)
            return func.__get__(instance, owner)  # noqa

        def __call__(accessor, *args, **kwargs):
            raise TypeError  # FIXME: ??

        cls_suffix = f'<{owner_cls.__qualname__}>'
        accessor_cls = lang.new_type(
            type(self).__name__ + cls_suffix,
            (Method._Accessor,),
            {
                '__qualname__': type(self).__qualname__ + cls_suffix,
                '__get__': __get__,
                '__call__': __call__,
                '_invalidate': invalidate,
                '_owner': owner_cls,
            },
        )
        self.update_wrapper(accessor_cls)

        accessor = accessor_cls()
        accessor._method = self
        self._accessor_map[owner_cls] = accessor  # FIXME: lol it hits Method.__get__ when in cls dct
        return accessor

    def __get__(self, instance, owner=None):
        if instance is None:
            # FIXME: classmethod/staticmethod
            return self

        if owner is None:
            owner = type(instance)

        mro_dct: ta.Dict[str, ta.Any] = {}
        for cur_cls in owner.__mro__[-2::-1]:
            # FIXME: dirty atts, dont rescan
            mro_dct.update(cur_cls.__dict__)
            cur_acc = None
            for nam, att in mro_dct.items():
                if not (
                    att is self or (
                        isinstance(att, Method._Accessor) and
                        att._method is self and  # noqa
                        att._owner is not cur_cls  # noqa
                    )
                ):
                    continue
                if cur_acc is None:
                    cur_acc = self._get_accessor(cur_cls)
                setattr(cur_cls, nam, cur_acc)

        owner_acc = self._get_accessor(owner)
        return owner_acc.__get__(instance, owner)


def method(func):
    return Method(func)

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
from .impls import get_impl_func_cls_set


T = ta.TypeVar('T')
R = ta.TypeVar('R')
P = ta.ParamSpec('P')


##


class Method(ta.Generic[P, R]):
    def __init__(
            self,
            func: ta.Callable,
            *,
            installable: bool = False,
            requires_override: bool = False,
    ) -> None:
        super().__init__()

        if not callable(func) and not hasattr(func, '__get__'):  # type: ignore
            raise TypeError(f'{func!r} is not callable or a descriptor')

        self._func = func
        self._installable = installable
        self._requires_override = requires_override

        self._impls: ta.MutableMapping[ta.Callable, frozenset[type] | None] = weakref.WeakKeyDictionary()

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

        self._owner: type | None = None
        self._name: str | None = None

    def __set_name__(self, owner, name):
        if self._owner is None:
            self._owner = owner
        if self._name is None:
            self._name = name

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

    def register(self, impl: T, cls_set: frozenset[type] | None = None) -> T:
        # bpo-39679: in Python <= 3.9, classmethods and staticmethods don't inherit __annotations__ of the wrapped
        # function (fixed in 3.10+ as a side-effect of bpo-43682) but we need that for annotation-derived
        # singledispatches. So we add that just-in-time here.
        if isinstance(impl, (staticmethod, classmethod)):
            impl.__annotations__ = getattr(impl.__func__, '__annotations__', {})

        check.callable(impl)
        if impl not in self._impls:
            self._impls[impl] = cls_set  # type: ignore
            self._dispatch_func_cache.clear()

        return impl

    def _is_impl(self, obj: ta.Any) -> bool:
        try:
            hash(obj)
        except TypeError:
            return False

        return obj in self._impls

    def build_attr_dispatcher(self, instance_cls: type, owner_cls: type | None = None) -> Dispatcher[str]:
        if owner_cls is None:
            owner_cls = instance_cls

        mro = instance_cls.__mro__[-2::-1]
        try:
            mro_pos = mro.index(owner_cls)
        except ValueError:
            raise TypeError(f'Owner class {owner_cls} not in mro of instance class {instance_cls}') from None

        mro_dct: dict[str, list[tuple[type, ta.Any]]] = {}
        for cur_cls in mro[:mro_pos + 1]:
            for att, obj in cur_cls.__dict__.items():
                if att not in mro_dct:
                    if not self._is_impl(obj):
                        continue

                try:
                    lst = mro_dct[att]
                except KeyError:
                    lst = mro_dct[att] = []
                lst.append((cur_cls, obj))

        #

        disp: Dispatcher[str] = Dispatcher()

        seen: dict[ta.Any, str] = {}
        for att, lst in mro_dct.items():
            if not lst:
                raise RuntimeError
            _, obj = lst[-1]

            if len(lst) > 1:
                if self._requires_override and not lang.is_override(obj):
                    raise lang.RequiresOverrideError(
                        att,
                        instance_cls,
                        lst[-1][0],
                        lst[0][0],
                    )

            if not self._is_impl(obj):
                continue

            cls_set = self._impls[obj]
            if cls_set is None:
                cls_set = get_impl_func_cls_set(obj, arg_offset=1)
                self._impls[obj] = cls_set

            try:
                ex_att = seen[obj]
            except KeyError:
                pass
            else:
                raise TypeError(f'Duplicate impl: {owner_cls} {instance_cls} {att} {ex_att}')
            seen[obj] = att

            disp.register(att, cls_set)

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

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        instance, *rest = args
        instance_cls = type(instance)

        # if instance_cls is super:
        #     owner = instance.__self_class__.__mro__[instance.__self_class__.__mro__.index(instance.__thisclass__) + 1]
        #     att_disp = self.build_attr_dispatcher(instance.__self_class__, owner)
        #     func = self.build_dispatch_func(att_disp)
        #     return func.__get__(instance, instance.__thisclass__)(*rest, **kwargs)

        try:
            func = self._dispatch_func_cache[weakref.ref(instance_cls)]
        except KeyError:
            func = self.get_dispatch_func(instance_cls)
        return func.__get__(instance)(*rest, **kwargs)  # noqa


##


@ta.overload
def method(
        func: ta.Callable[P, R],
        /,
        *,
        installable: bool = False,
        requires_override: bool = False,
) -> Method[P, R]:  # noqa
    ...


@ta.overload
def method(
        func: None = None,
        /,
        *,
        installable: bool = False,
        requires_override: bool = False,
) -> ta.Callable[[ta.Callable[P, R]], Method[P, R]]:  # noqa
    ...


def method(
        func=None,
        /,
        *,
        installable=False,
        requires_override=False,
):
    kw = dict(
        installable=installable,
        requires_override=requires_override,
    )

    if func is None:
        return functools.partial(Method, **kw)

    return Method(func, **kw)


#


def install_method(
        mth: ta.Any,
        *,
        name: str | None = None,
        on: type | None = None,
) -> ta.Callable[[T], T]:
    mth = check.isinstance(mth, Method)
    if not mth._installable:  # noqa
        raise TypeError(f'Method not installable: {mth}')

    def inner(fn):
        a = name
        if a is None:
            a = fn.__name__

        owner: type = check.not_none(mth._owner)  # noqa
        if on is None:
            cls = owner
        else:
            cls = check.issubclass(on, owner)

        check.arg(not hasattr(cls, a))
        setattr(cls, a, fn)

        mth.register(fn)

        return fn

    return inner

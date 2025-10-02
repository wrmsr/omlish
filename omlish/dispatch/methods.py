"""
TODO:
 - .super(instance[_cls], owner)
 - ALT: A.f(super(), ... ? :/
 - classmethod/staticmethod
"""
import functools
import typing as ta

from .. import check
from .. import collections as col
from .dispatch import Dispatcher
from .impls import get_impl_func_cls_set


T = ta.TypeVar('T')
R = ta.TypeVar('R')
P = ta.ParamSpec('P')


##


class Method(ta.Generic[P, R]):
    """
    MRO-honoring instancemethod singledispatch. There are many ways to do this, and this one is attr name based: a class
    is considered to have method implementations that have been registered to a given method based on whether or not
    they are accessible by a non-shadowed, MRO-resolved named attribute on that class.

    Care must be taken when overriding registered implementations from superclasses in subclasses - shadowing the name
    of the superclass method will not automatically register the new method with the same name to the dispatch method -
    it must be explicitly `@register`'ed itself. This is a feature, allowing for selective de-registration of
    implementations in subclasses via name shadowing.

    Methods can choose to allow external installation of implementations outside of direct subclasses. This is to be
    used *extremely* rarely - basically only in the rare case of externally extensible type hierarchies with visitors.
    """

    def __init__(
            self,
            func: ta.Callable,
            *,
            installable: bool = False,
            requires_override: bool = False,
            instance_cache: bool = False,
    ) -> None:
        super().__init__()

        if not callable(func) and not hasattr(func, '__get__'):  # type: ignore
            raise TypeError(f'{func!r} is not callable or a descriptor')

        self._func = func
        self._installable = installable
        self._instance_cache = instance_cache

        self._registry: col.AttrRegistry[ta.Callable, Method._Entry] = col.AttrRegistry(
            requires_override=requires_override,
        )

        self._cache: col.AttrRegistryCache[ta.Callable, Method._Entry, ta.Callable] = col.AttrRegistryCache(
            self._registry,
            self._prepare,
        )

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

        self._owner: type | None = None
        self._name: str | None = None

    class _Entry:
        cls_set: frozenset[type]

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
        check.callable(impl)

        entry = Method._Entry()
        if cls_set is not None:
            entry.cls_set = cls_set

        self._registry.register(ta.cast(ta.Callable, impl), entry)

        return impl

    def _build_dispatcher(self, collected: ta.Mapping[str, tuple[ta.Callable, _Entry]]) -> Dispatcher[str]:
        disp: Dispatcher[str] = Dispatcher()

        for a, (f, e) in collected.items():
            try:
                cls_set = e.cls_set
            except AttributeError:
                cls_set = e.cls_set = get_impl_func_cls_set(f, arg_offset=1)

            disp.register(a, cls_set)

        return disp

    def _build_dispatch_func(self, disp: Dispatcher[str]) -> ta.Callable:
        dispatch = disp.dispatch
        type_ = type
        getattr_ = getattr
        base_func = self._func
        func_name = getattr(base_func, '__name__', 'singledispatch method')

        def __call__(self, *args, **kwargs):  # noqa
            if not args:
                raise TypeError(f'{func_name} requires at least 1 positional argument')

            if (impl_att := dispatch(type_(args[0]))) is not None:
                return getattr_(self, impl_att)(*args, **kwargs)

            return base_func.__get__(self)(*args, **kwargs)  # noqa

        self.update_wrapper(__call__)
        return __call__

    def _prepare(self, instance_cls: type, collected: ta.Mapping[str, tuple[ta.Callable, _Entry]]) -> ta.Callable:
        disp = self._build_dispatcher(collected)
        func = self._build_dispatch_func(disp)
        return func

    def __get__(self, instance, owner=None):
        if instance is None:
            # FIXME: classmethod/staticmethod
            return self

        if self._instance_cache:
            try:
                return instance.__dict__[self._name]
            except KeyError:
                pass

        bound = self._cache.get(type(instance)).__get__(instance, owner)  # noqa

        if self._instance_cache:
            instance.__dict__[self._name] = bound

        return bound

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        instance, *rest = args

        # if instance_cls is super:
        #     owner = instance.__self_class__.__mro__[instance.__self_class__.__mro__.index(instance.__thisclass__) + 1]
        #     att_disp = self.build_attr_dispatcher(instance.__self_class__, owner)
        #     func = self.build_dispatch_func(att_disp)
        #     return func.__get__(instance, instance.__thisclass__)(*rest, **kwargs)

        return self.__get__(instance)(*rest, **kwargs)


##


def method(
        *,
        installable: bool = False,
        requires_override: bool = False,
        instance_cache: bool = False,
) -> ta.Callable[[ta.Callable[P, R]], Method[P, R]]:  # noqa
    return functools.partial(
        Method,  # type: ignore[arg-type]
        installable=installable,
        requires_override=requires_override,
        instance_cache=instance_cache,
    )


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
            cls = check.issubclass(on, owner)  # noqa

        check.arg(not hasattr(cls, a))
        setattr(cls, a, fn)

        mth.register(fn)

        return fn

    return inner

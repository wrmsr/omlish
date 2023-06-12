"""
TODO:
 - functools.partial get_dispatcher.dispatcher -> collections.defaultdict, almost all C instance inner
"""
import abc
import functools
import typing as ta
import weakref

from .. import c3
from .. import check


T = ta.TypeVar('T')


##


def _is_union_type(cls: ta.Any) -> bool:
    if hasattr(ta, 'UnionType'):
        return ta.get_origin(cls) in {ta.Union, getattr(ta, 'UnionType')}
    else:
        return ta.get_origin(cls) in {ta.Union}


def _get_impl_cls_set(func: ta.Callable) -> ta.Set[type]:
    ann = getattr(func, '__annotations__', {})
    if not ann:
        raise TypeError(f'Invalid impl: {func!r}')

    _, cls = next(iter(ta.get_type_hints(func).items()))
    if _is_union_type(cls):
        return {check.isinstance(arg, type) for arg in ta.get_args(cls)}
    else:
        return {check.isinstance(cls, type)}


def _find_impl(cls: type, registry: ta.Mapping[type, ta.Callable]) -> ta.Callable:
    mro = c3.compose_mro(cls, registry.keys())

    match: ta.Optional[type] = None
    for t in mro:
        if match is not None:
            # If *match* is an implicit ABC but there is another unrelated, equally matching implicit ABC, refuse the
            # temptation to guess.
            if (
                    t in registry
                    and t not in cls.__mro__
                    and match not in cls.__mro__
                    and not issubclass(match, t)
            ):
                raise RuntimeError(f'Ambiguous dispatch: {match} or {t}')
            break

        if t in registry:
            match = t

    impl: ta.Optional[ta.Callable] = None
    if match is not None:
        impl = registry.get(match)
    if impl is None:
        raise RuntimeError(f'No dispatch: {cls}')
    return impl


##


class Dispatcher:
    def __init__(self) -> None:
        super().__init__()

        self._impls_by_arg_cls: ta.Dict[type, ta.Callable] = {}
        self._dispatch_cache: ta.MutableMapping[type, ta.Callable] = weakref.WeakKeyDictionary()
        self._cache_token: ta.Any = None

    def dispatch(self, cls: type) -> ta.Callable:
        if self._cache_token is not None:
            current_token = abc.get_cache_token()
            if self._cache_token != current_token:
                self._dispatch_cache.clear()
                self._cache_token = current_token

        try:
            return self._dispatch_cache[cls]
        except KeyError:
            pass

        try:
            impl = self._impls_by_arg_cls[cls]
        except KeyError:
            impl = _find_impl(cls, self._impls_by_arg_cls)

        self._dispatch_cache[cls] = impl
        return impl

    def register(self, impl: ta.Callable, cls_col: ta.Iterable[type]) -> None:
        for cls in cls_col:
            self._impls_by_arg_cls[cls] = impl

            if self._cache_token is None and hasattr(cls, '__abstractmethods__'):
                self._cache_token = abc.get_cache_token()

        self._dispatch_cache.clear()


##


def function(func):
    disp = Dispatcher()
    disp.register(func, [object])

    func_name = getattr(func, '__name__', 'singledispatch function')

    @functools.wraps(func)
    def wrapper(*args, **kw):
        if not args:
            raise TypeError(f'{func_name} requires at least 1 positional argument')
        return disp.dispatch(type(args[0]))(*args, **kw)

    def register(impl, cls=None):
        if cls is None:
            cls_set = _get_impl_cls_set(impl)
        else:
            cls_set = {cls}
        disp.register(impl, cls_set)

    wrapper.register = register  # type: ignore
    wrapper.dispatch = disp.dispatch  # type: ignore
    return wrapper


##


class Method:
    def __init__(self, func: ta.Callable) -> None:
        if not callable(func) and not hasattr(func, '__get__'):  # type: ignore
            raise TypeError(f'{func!r} is not callable or a descriptor')

        self._func = func

        self._impls: ta.MutableSet[ta.Callable] = weakref.WeakSet()
        self._dispatch_by_cls: ta.MutableMapping[type, ta.Callable[[type], ta.Callable]] = weakref.WeakKeyDictionary()

        # bpo-45678: special-casing for classmethod/staticmethod in Python <=3.9, as functools.update_wrapper doesn't
        # work properly in singledispatchmethod.__get__ if it is applied to an unbound classmethod/staticmethod
        unwrapped_func: ta.Any
        if isinstance(func, (staticmethod, classmethod)):
            unwrapped_func = func.__func__  # type: ignore
        else:
            unwrapped_func = func
        self._unwrapped_func = unwrapped_func

        self.__isabstractmethod__ = getattr(func, '__isabstractmethod__', False)  # noqa

        self._owner: ta.Any = None
        self._name: ta.Optional[str] = None

    def __set_name__(self, owner, name):
        check.none(self._owner)
        check.none(self._name)
        check.isinstance(owner, type)
        check.non_empty_str(name)

        ex = owner.__dict__[name]
        check.state(ex is self)

        self._owner = owner
        self._name = name

        acc = _MethodAccessor(self, None, owner)
        acc.register = self.register  # type: ignore
        setattr(owner, name, acc)

    def register(self, impl: T) -> T:
        # bpo-39679: in Python <= 3.9, classmethods and staticmethods don't inherit __annotations__ of the wrapped
        # function (fixed in 3.10+ as a side-effect of bpo-43682) but we need that for annotation-derived
        # singledispatches. So we add that just-in-time here.
        if isinstance(impl, (staticmethod, classmethod)):
            impl.__annotations__ = getattr(impl.__func__, '__annotations__', {})

        check.callable(impl)
        if impl not in self._impls:
            self._impls.add(impl)  # type: ignore
            self._dispatch_by_cls.clear()

        return impl

    def get_dispatch(self, cls: type) -> ta.Callable[[type], ta.Callable]:
        try:
            return self._dispatch_by_cls[cls]
        except KeyError:
            pass

        disp = Dispatcher()
        disp.register(self._func, [object])

        for mro_cls in reversed(cls.__mro__):
            for nam, att in mro_cls.__dict__.items():
                if att in self._impls:
                    disp.register(att, _get_impl_cls_set(att))

        ret = disp.dispatch
        self._dispatch_by_cls[cls] = ret
        return ret

    def update_wrapper(self, wrapper):
        functools.update_wrapper(wrapper, self._unwrapped_func)
        setattr(wrapper, '__isabstractmethod__', self.__isabstractmethod__)  # noqa
        return wrapper

    def __get__(self, instance, owner=None):
        @self.update_wrapper
        def method(*args, **kwargs):  # noqa
            impl = self.get_dispatch(owner)(type(args[0])).__get__(instance, owner)  # noqa
            return impl(*args, **kwargs)  # noqa

        return method


class _MethodAccessor:
    def __init__(self, method: Method, instance: ta.Any, owner: type) -> None:
        super().__init__()

        self._method = method
        self._instance = instance
        self._owner = owner

        method.update_wrapper(self)

        self._get_dispatch = functools.partial(method.get_dispatch, self._owner)

    def __get__(self, instance, owner=None):
        self_instance = self._instance
        self_owner = self._owner
        if instance is self_instance and owner is self_owner:
            return self

        self_method = self._method
        name = self_method._name  # noqa

        nxt = _MethodAccessor(self_method, instance, owner)  # noqa
        if instance is not None:
            instance.__dict__[name] = nxt  # noqa

            inst_cls = type(instance)
            try:
                inst_cls.__dict__[name]  # type: ignore

            except KeyError:
                for mro_cls in inst_cls.__mro__:
                    try:
                        mro_cls.__dict__[name]  # type: ignore
                    except KeyError:
                        if issubclass(mro_cls, self_method._owner):  # noqa
                            setattr(owner, name, _MethodAccessor(self_method, None, mro_cls))  # type: ignore  # noqa

            else:
                if self_owner is not inst_cls:
                    raise TypeError('super() not supported')  # FIXME

        elif owner is not None:
            setattr(owner, name, nxt)  # type: ignore  # noqa

        else:
            raise TypeError

        return nxt

    def __call__(self, *args, **kwargs):
        impl = self._get_dispatch()(type(args[0])).__get__(self._instance, self._owner)
        return impl(*args, **kwargs)


def method(func):
    return Method(func)

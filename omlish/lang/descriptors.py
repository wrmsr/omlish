import functools
import operator
import types
import typing as ta


T = ta.TypeVar('T')
P = ta.ParamSpec('P')


##


def attr_property(n: str):
    return property(operator.attrgetter(n))


def item_property(n: str):
    return property(operator.itemgetter(n))


##


BUILTIN_METHOD_DESCRIPTORS = (classmethod, staticmethod)


class _MethodDescriptor:
    pass


def is_method_descriptor(obj: ta.Any) -> bool:
    return isinstance(obj, (*BUILTIN_METHOD_DESCRIPTORS, _MethodDescriptor))


def unwrap_method_descriptors(fn: ta.Callable) -> ta.Callable:
    while is_method_descriptor(fn):
        fn = fn.__func__  # type: ignore  # noqa
    return fn


##


def unwrap_func(fn: ta.Callable) -> ta.Callable:
    fn, _ = unwrap_func_with_partials(fn)
    return fn


def unwrap_func_with_partials(fn: ta.Callable) -> tuple[ta.Callable, list[functools.partial]]:
    ps = []
    while True:
        if is_method_descriptor(fn) or isinstance(fn, types.MethodType):
            fn = fn.__func__  # type: ignore
        elif hasattr(fn, '__wrapped__'):
            nxt = fn.__wrapped__
            if not callable(nxt):
                raise TypeError(nxt)
            if nxt is fn:
                raise TypeError(fn)
            fn = nxt
        # NOTE: __wrapped__ takes precedence - a partial might point to a bound Method when the important information is
        # still the unbound func. see _decorator_descriptor for an example of this.
        elif isinstance(fn, functools.partial):
            ps.append(fn)
            fn = fn.func
        else:
            break
    return fn, ps


##


WRAPPER_UPDATES_EXCEPT_DICT = tuple(a for a in functools.WRAPPER_UPDATES if a != '__dict__')


def update_wrapper_except_dict(
        wrapper,
        wrapped,
        assigned=functools.WRAPPER_ASSIGNMENTS,
        updated=WRAPPER_UPDATES_EXCEPT_DICT,
):
    return functools.update_wrapper(
        wrapper,
        wrapped,
        assigned=assigned,
        updated=updated,
    )


##


_DECORATOR_HANDLES_UNBOUND_METHODS = False


class _decorator_descriptor:  # noqa
    def __init__(self, wrapper, fn):
        self._wrapper = wrapper
        self._fn = fn
        update_wrapper_except_dict(self, fn)

    def __repr__(self):
        return f'{self.__class__.__name__}<{self._wrapper}, {self._fn}>'

    if _DECORATOR_HANDLES_UNBOUND_METHODS:
        def __get__(self, instance, owner):
            fn = self._fn.__get__(instance, owner)
            if instance is not None:
                return functools.update_wrapper(functools.partial(self._wrapper, fn), fn)
            else:
                @functools.wraps(fn)
                def outer(this, *args, **kwargs):
                    @functools.wraps(self._fn)
                    def inner(*args2, **kwargs2):
                        return fn(this, *args2, **kwargs2)
                    return self._wrapper(inner, *args, **kwargs)
                return outer

    else:
        def __get__(self, instance, owner):
            return functools.update_wrapper(functools.partial(self._wrapper, fn := self._fn.__get__(instance, owner)), fn)  # noqa

    def __call__(self, *args, **kwargs):
        return self._wrapper(self._fn, *args, **kwargs)


class _decorator:  # noqa
    def __init__(self, wrapper):
        self._wrapper = wrapper
        update_wrapper_except_dict(self, wrapper)

    def __repr__(self):
        return f'{self.__class__.__name__}<{self._wrapper}>'

    def __call__(self, fn):
        return _decorator_descriptor(self._wrapper, fn)  # noqa


# FIXME:
# def decorator(
#         wrapper: ta.Callable[ta.Concatenate[ta.Any, P], T],  # FIXME: https://youtrack.jetbrains.com/issue/PY-72164  # noqa
# ) -> ta.Callable[[ta.Callable[P, T]], ta.Callable[P, T]]:
#     return _decorator(wrapper)


decorator = _decorator


##


class AccessForbiddenError(Exception):

    def __init__(self, name: str | None = None, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*((name,) if name is not None else ()), *args, **kwargs)  # noqa
        self.name = name


class AccessForbiddenDescriptor:

    def __init__(self, name: str | None = None) -> None:
        super().__init__()

        self._name = name

    def __set_name__(self, owner: type, name: str) -> None:
        if self._name is None:
            self._name = name
        elif name != self._name:
            raise NameError(name)

    def __get__(self, instance, owner=None):
        raise AccessForbiddenError(self._name)


def access_forbidden():  # noqa
    return AccessForbiddenDescriptor()


##


class _ClassOnly:
    def __init__(self, mth):
        if not isinstance(mth, classmethod):
            raise TypeError(f'must be classmethod: {mth}')
        super().__init__()
        self._mth = (mth,)
        functools.update_wrapper(self, mth)  # type: ignore

    @property
    def _mth(self):
        return self.__mth

    @_mth.setter
    def _mth(self, x):
        self.__mth = x

    def __get__(self, instance, owner):
        if instance is not None:
            raise TypeError(f'method must not be used on instance: {self._mth}')
        return self._mth[0].__get__(instance, owner)


def classonly(obj: T) -> T:  # noqa
    return _ClassOnly(obj)  # type: ignore

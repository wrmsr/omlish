import functools
import typing as ta


T = ta.TypeVar('T')


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


class AccessForbiddenException(Exception):

    def __init__(self, name: str | None = None, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*((name,) if name is not None else ()), *args, **kwargs)  # noqa
        self.name = name


class AccessForbiddenDescriptor:

    def __init__(self, name: str | None = None) -> None:
        super().__init__()

        self._name = name

    def __set_name__(self, owner: ta.Type, name: str) -> None:
        if self._name is None:
            self._name = name
        elif name != self._name:
            raise NameError(name)

    def __get__(self, instance, owner=None):
        raise AccessForbiddenException(self._name)


def access_forbidden():
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

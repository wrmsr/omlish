import typing as ta


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

    def __init__(self, name: ta.Optional[str] = None, *args: ta.Any, **kwargs: ta.Any) -> None:
        super().__init__(*((name,) if name is not None else ()), *args, **kwargs)  # noqa
        self.name = name


class AccessForbiddenDescriptor:

    def __init__(self, name: ta.Optional[str] = None) -> None:
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

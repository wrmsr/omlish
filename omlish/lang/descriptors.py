import typing as ta


BUILTIN_METHOD_DESCRIPTORS = (classmethod, staticmethod)


class _MethodDescriptor:
    pass


def is_method_descriptor(obj: ta.Any) -> bool:
    return isinstance(obj, (*BUILTIN_METHOD_DESCRIPTORS, _MethodDescriptor))


def unwrap_method_descriptors(fn: ta.Callable) -> ta.Callable:
    while is_method_descriptor(fn):
        fn = fn.__func__  # type: ignore  # noqa
    return fn

import inspect
import types
import typing as ta


def fn_has_descriptor(fn: ta.Callable) -> bool:
    return type(fn).__get__ is not types.FunctionType.__get__  # noqa


def get_flat_fn_args(fn: ta.Callable) -> ta.List[str]:
    if isinstance(fn, classmethod):
        ofs = 1
    else:
        ofs = 0
    if isinstance(fn, (classmethod, staticmethod)):
        fn = fn.__func__
    argspec = inspect.getfullargspec(fn)
    if (
            argspec.varargs or
            argspec.varkw or
            argspec.defaults or
            argspec.kwonlyargs or
            argspec.kwonlydefaults
    ):
        raise TypeError(fn)
    return list(argspec.args)[ofs:]

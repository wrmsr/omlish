import importlib
import string
import typing as ta


class ResolvableClassNameError(NameError):
    pass


def get_cls_fqcn(cls: type, *, nocheck: bool = False) -> str:
    if not isinstance(cls, type):
        raise TypeError(cls)

    mn = cls.__module__
    if set(mn) - set(string.ascii_lowercase + string.digits + '_.'):
        raise ResolvableClassNameError(cls)

    qn = cls.__qualname__
    if not all(qp[0].isupper() for qp in qn.split('.')) or (set(qn) - set(string.ascii_letters + string.digits + '.')):
        raise ResolvableClassNameError(cls)

    fqcn = '.'.join([cls.__module__, cls.__qualname__])
    if not nocheck:
        if get_fqcn_cls(fqcn, nocheck=True) is not cls:
            raise ResolvableClassNameError(cls, fqcn)

    return fqcn


def get_fqcn_cls(fqcn: str, *, nocheck: bool = False) -> type:
    if not isinstance(fqcn, str) or not fqcn:
        raise TypeError(fqcn)

    parts = fqcn.split('.')
    pos = next(i for i, p in enumerate(parts) if p[0].isupper())
    mps, qps = parts[:pos], parts[pos:]
    mod = importlib.import_module('.'.join(mps))

    o: ta.Any = mod
    for qp in qps:
        o = getattr(o, qp)
        if not isinstance(o, type):
            raise TypeError(o)

    cls = o
    if not isinstance(cls, type):
        raise TypeError(cls)

    if not nocheck:
        if not get_cls_fqcn(cls, nocheck=True) == fqcn:
            raise ResolvableClassNameError(cls, fqcn)

    return o


class Resolvable:
    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)
        get_cls_fqcn(cls, nocheck=True)

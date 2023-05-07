"""
TODO:
 - https://github.com/JetBrains/intellij-community/blob/8a0b1c9e911750d74a3be4cfee746804c674f27f/python/python-psi-impl/src/com/jetbrains/python/psi/impl/PyClassImpl.java#L703  # noqa
"""
import typing as ta


T = ta.TypeVar('T')


class Property(ta.Generic[T]):

    @classmethod
    def _unwrap(cls, fn):
        if isinstance(fn, property):
            if fn.fset is not None or fn.fdel is not None:
                raise TypeError(fn)
            fn = fn.fget
        if callable(fn):
            return fn
        else:
            raise TypeError(fn)

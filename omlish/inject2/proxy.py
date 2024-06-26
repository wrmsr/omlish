import typing as ta

from .. import lang
from .. import check


@lang.cached_function
def _cyclic_dependency_proxy() -> tuple[type, ta.Callable[[ta.Any, ta.Any], None]]:
    import wrapt  # noqa

    class _CyclicDependencyPlaceholder(lang.Final):

        def __init__(self, cls: ta.Any) -> None:
            super().__init__()
            self.__cls = cls

        def __repr__(self) -> str:
            return f'{type(self).__name__}({self.__cls!r})'

    class _CyclicDependencyProxy(wrapt.ObjectProxy, lang.Final):  # noqa

        def __init__(self, cls):
            super().__init__(_CyclicDependencyPlaceholder(cls))
            if isinstance(cls, type):
                self._self__class__ = cls

        def __repr__(self) -> str:
            return f'_CyclicDependencyProxy({self.__wrapped__!r})'

        def __getattribute__(self, att):
            if att == '__class__':
                try:
                    return object.__getattribute__(self, '_self__class__')  # noqa
                except AttributeError:
                    pass
            return object.__getattribute__(self, att)  # noqa

    def set(prox, obj):
        check.state(type(prox) is _CyclicDependencyProxy)
        check.not_isinstance(obj, _CyclicDependencyPlaceholder)
        check.isinstance(prox.__wrapped__, _CyclicDependencyPlaceholder)
        if hasattr(prox, '_self__class__'):
            check.issubclass(type(obj), prox._self__class__)
        prox.__wrapped__ = obj
        if hasattr(prox, '_self__class__'):
            del prox._self__class__

    return (_CyclicDependencyProxy, set)  # noqa

import typing as ta


T = ta.TypeVar('T')


class _Proxy(ta.Generic[T]):
    __obj: ta.Optional[T] = None

    @property
    def _obj(self) -> T:
        if self.__obj is None:
            raise TypeError('recursive proxy not set')
        return self.__obj

    def _set_obj(self, obj: T) -> None:
        if self.__obj is not None:
            raise TypeError('recursive proxy already set')
        self.__obj = obj

    @classmethod
    def _new(cls):
        return (p := cls()), p._set_obj

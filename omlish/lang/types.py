import typing as ta


Ty = ta.TypeVar('Ty', bound=type)


BytesLike = ta.Union[bytes, bytearray]


def protocol_check(proto: type) -> ta.Callable[[Ty], Ty]:
    def inner(cls):
        if not issubclass(cls, proto):
            raise TypeError(cls)
        return cls
    return inner

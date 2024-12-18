# ruff: noqa: N802
import typing as ta


##


# class InputStream(ta.Protocol):
#
#   @property
#   def index(self) -> int: ...
#
#   @property
#   def size(self) -> int: ...
#
#   # Reset the stream so that it's in the same state it was when the object was created *except* the data array is not
#   # touched.
#   def reset(self) -> None: ...
#
#   def consume(self) -> None: ...
#
#   def LA(self, offset: int) -> int: ...
#
#   def LT(self, offset: int) -> int: ...
#
#   def mark(self) -> int: ...
#
#   def release(self, marker: int) -> None: ...
#
#   # consume() ahead until p==_index; can't just set p=_index as we must update line and column. If we seek backwards,
#   # just set p
#   def seek(self, _index: int) -> None: ...
#
#   def getText(self, start: int, stop: int) -> str: ...
#
#   def __str__(self) -> str: ...


InputStream: ta.TypeAlias = ta.Any


##


# @lang.protocol_check(InputStream)
class ProxyInputStream:
    def __init__(self, target: InputStream) -> None:
        super().__init__()

        self._target = target

    @property
    def index(self) -> int:
        return self._target.index

    @property
    def size(self) -> int:
        return self._target.size

    def reset(self) -> None:
        self._target.reset()

    def consume(self) -> None:
        self._target.consume()

    def LA(self, offset: int) -> int:
        return self._target.LA(offset)

    def LT(self, offset: int) -> int:
        return self._target.LT(offset)

    def mark(self) -> int:
        return self._target.mark()

    def release(self, marker: int) -> None:
        return self._target.release(marker)

    def seek(self, _index: int) -> None:
        return self._target.seek(_index)

    def getText(self, start: int, stop: int) -> str:
        return self._target.getText(start, stop)

    def __str__(self) -> str:
        return str(self._target)


##


class CaseInsensitiveInputStream(ProxyInputStream):
    def LA(self, offset: int) -> int:
        ret = super().LA(offset)
        if ret != -1:
            ret = ord(chr(ret).upper())
        return ret

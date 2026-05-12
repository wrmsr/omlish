# ruff: noqa: UP006 UP007 UP037 UP045
# The MIT License (MIT)
#
# Copyright (c) 2016 Alex Grönholm
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
import collections
import functools
import reprlib
import threading
import typing as ta


KT = ta.TypeVar('KT')
VT_co = ta.TypeVar('VT_co', covariant=True)


##


class CborError(Exception):
    """Base class for errors that occur during CBOR encoding or decoding."""


class CborEncodeError(CborError):
    """Raised for exceptions occurring during CBOR encoding."""


class CborEncodeTypeError(CborEncodeError, TypeError):
    """Raised when attempting to encode a type that cannot be serialized."""


class CborEncodeValueError(CborEncodeError, ValueError):
    """Raised when the CBOR encoder encounters an invalid value."""


class CborDecodeError(CborError):
    """Raised for exceptions occurring during CBOR decoding."""


class CborDecodeValueError(CborDecodeError, ValueError):
    """Raised when the CBOR stream being decoded contains an invalid value."""


class CborDecodeEOF(CborDecodeError, EOFError):
    """Raised when decoding unexpectedly reaches EOF."""


##


_CBOR_THREAD_LOCALS = threading.local()


@functools.total_ordering
class CborTag:
    """
    Represents a CBOR semantic tag.

    :param int tag: tag number
    :param value: encapsulated value (any object)
    """

    __slots__ = 'tag', 'value'

    def __init__(self, tag: str | int, value: ta.Any) -> None:
        if not isinstance(tag, int) or tag not in range(2**64):
            raise TypeError('CBORTag tags must be positive integers less than 2**64')
        self.tag = tag
        self.value = value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, CborTag):
            return (self.tag, self.value) == (other.tag, other.value)

        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, CborTag):
            return (self.tag, self.value) <= (other.tag, other.value)

        return NotImplemented

    @reprlib.recursive_repr()
    def __repr__(self) -> str:
        return f'CBORTag({self.tag}, {self.value!r})'

    def __hash__(self) -> int:
        self_id = id(self)
        try:
            running_hashes = _CBOR_THREAD_LOCALS.running_hashes
        except AttributeError:
            running_hashes = _CBOR_THREAD_LOCALS.running_hashes = set()

        if self_id in running_hashes:
            raise RuntimeError(
                'This CBORTag is not hashable because it contains a reference to itself',
            )

        running_hashes.add(self_id)
        try:
            return hash((self.tag, self.value))
        finally:
            running_hashes.remove(self_id)
            if not running_hashes:
                del _CBOR_THREAD_LOCALS.running_hashes


class CborSimpleValue(collections.namedtuple('CborSimpleValue', ['value'])):
    """
    Represents a CBOR "simple value".

    :param int value: the value (0-255)
    """

    __slots__ = ()

    value: int

    def __hash__(self) -> int:
        return hash(self.value)

    def __repr__(self) -> str:
        # Matches cbor2
        return f'CBORSimpleValue(value={self.value!r})'

    def __new__(cls, value: int) -> 'CborSimpleValue':
        if value < 0 or value > 255 or 23 < value < 32:
            raise TypeError('simple value out of range (0..23, 32..255)')

        return super().__new__(cls, value)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.value == other
        elif isinstance(other, CborSimpleValue):
            return self.value == other.value

        return NotImplemented

    def __ne__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.value != other
        elif isinstance(other, CborSimpleValue):
            return self.value != other.value

        return NotImplemented

    def __lt__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.value < other
        elif isinstance(other, CborSimpleValue):
            return self.value < other.value

        return NotImplemented

    def __le__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.value <= other
        elif isinstance(other, CborSimpleValue):
            return self.value <= other.value

        return NotImplemented

    def __ge__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.value >= other
        elif isinstance(other, CborSimpleValue):
            return self.value >= other.value

        return NotImplemented

    def __gt__(self, other: object) -> bool:
        if isinstance(other, int):
            return self.value > other
        elif isinstance(other, CborSimpleValue):
            return self.value > other.value

        return NotImplemented


class CborFrozenDict(ta.Mapping[KT, VT_co]):
    """
    A hashable, immutable mapping type.

    The arguments to ``FrozenDict`` are processed just like those to ``dict``.
    """

    def __init__(self, *args: ta.Mapping[KT, VT_co] | ta.Iterable[tuple[KT, VT_co]]) -> None:
        self._d: dict[KT, VT_co] = dict(*args)
        self._hash: int | None = None

    def __iter__(self) -> ta.Iterator[KT]:
        return iter(self._d)

    def __len__(self) -> int:
        return len(self._d)

    def __getitem__(self, key: KT) -> VT_co:
        return self._d[key]

    def __repr__(self) -> str:
        # Matches cbor2
        return f'FrozenDict({self._d})'

    def __hash__(self) -> int:
        if self._hash is None:
            self._hash = hash((frozenset(self), frozenset(self.values())))

        return self._hash


##


class CborUndefinedType:
    __slots__ = ()

    def __new__(cls: ta.Type['CborUndefinedType']) -> 'CborUndefinedType':
        try:
            return CBOR_UNDEFINED
        except NameError:
            return super().__new__(cls)

    def __repr__(self) -> str:
        return 'undefined'

    def __bool__(self) -> bool:
        return False


class CborBreakMarkerType:
    __slots__ = ()

    def __new__(cls: ta.Type['CborBreakMarkerType']) -> 'CborBreakMarkerType':
        try:
            return CBOR_BREAK_MARKER
        except NameError:
            return super().__new__(cls)

    def __repr__(self) -> str:
        return 'break_marker'

    def __bool__(self) -> bool:
        return True


CBOR_UNDEFINED = CborUndefinedType()
CBOR_BREAK_MARKER = CborBreakMarkerType()

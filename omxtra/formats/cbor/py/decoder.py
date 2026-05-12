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
import binascii
import codecs
import datetime
import decimal
import email.message
import fractions
import io
import ipaddress
import re
import struct
import sys
import typing as ta
import uuid

from .types import CBOR_BREAK_MARKER
from .types import CBOR_UNDEFINED
from .types import CborDecodeEOFError
from .types import CborDecodeError
from .types import CborDecodeValueError
from .types import CborFrozenDict
from .types import CborSimpleValue
from .types import CborTag


T = ta.TypeVar('T')


##


_CBOR_TIMESTAMP_PAT = re.compile(
    r'^(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)'
    r'(?:\.(\d{1,6})\d*)?(?:Z|([+-])(\d\d):(\d\d))$',
)

_CBOR_INCREMENTAL_UTF8_DECODER = codecs.getincrementaldecoder('utf-8')


class CborDecoder:
    """
    The CBORDecoder class implements a fully featured `CBOR`_ decoder with several extensions for handling shared
    references, big integers, rational numbers and so on. Typically the class is not used directly, but the :func:`load`
    and :func:`loads` functions are called to indirectly construct and use the class.

    When the class is constructed manually, the main entry points are :meth:`decode` and :meth:`decode_from_bytes`.

    .. _CBOR: https://cbor.io/
    """

    __slots__ = (
        '_tag_hook',
        '_object_hook',
        '_share_index',
        '_shareables',
        '_fp',
        '_fp_read',
        '_immutable',
        '_str_errors',
        '_stringref_namespace',
        '_max_depth',
        '_decode_depth',
    )

    _fp: ta.IO[bytes]
    _fp_read: ta.Callable[[int], bytes]
    _str_errors: str

    def __init__(
        self,
        fp: ta.IO[bytes],
        tag_hook: ta.Optional[ta.Callable[[CborDecoder, CborTag], ta.Any]] = None,
        object_hook: ta.Optional[ta.Callable[[CborDecoder, ta.Dict[ta.Any, ta.Any]], ta.Any]] = None,
        str_errors: str = 'strict',
        *,
        max_depth: int = 400,
    ):
        """
        :param fp:
            the file to read from (any file-like object opened for reading in binary mode)
        :param tag_hook:
            callable that takes 2 arguments: the decoder instance, and the :class:`.CBORTag` to be decoded. This
            callback is invoked for any tags for which there is no built-in decoder. The return value is substituted for
            the :class:`.CBORTag` object in the deserialized output
        :param object_hook:
            callable that takes 2 arguments: the decoder instance, and a dictionary. This callback is invoked for each
            deserialized :class:`dict` object. The return value is substituted for the dict in the deserialized output.
        :param str_errors:
            determines how to handle unicode decoding errors (see the `Error Handlers`_ section in the standard library
            documentation for details)
        :param max_depth:
            the maximum allowed container nesting depth

        .. _Error Handlers: https://docs.python.org/3/library/codecs.html#error-handlers
        """

        self.fp = fp
        self.tag_hook = tag_hook
        self.object_hook = object_hook
        self.str_errors = str_errors
        self._share_index: ta.Optional[int] = None
        self._shareables: list[object] = []
        self._stringref_namespace: ta.Optional[list[str | bytes]] = None
        self._immutable = False
        self._max_depth = max_depth
        self._decode_depth = 0

    @property
    def immutable(self) -> bool:
        """
        Used by decoders to check if the calling context requires an immutable type.  Object_hook or tag_hook should
        raise an exception if this flag is set unless the result can be safely used as a dict key.
        """

        return self._immutable

    @property
    def fp(self) -> ta.IO[bytes]:
        return self._fp

    @fp.setter
    def fp(self, value: ta.IO[bytes]) -> None:
        try:
            if not callable(value.read):
                raise ValueError('fp.read is not callable')  # noqa
        except AttributeError:
            raise ValueError('fp object has no read method') from None
        else:
            self._fp = value
            self._fp_read = value.read

    @property
    def tag_hook(self) -> ta.Optional[ta.Callable[[CborDecoder, CborTag], ta.Any]]:
        return self._tag_hook

    @tag_hook.setter
    def tag_hook(self, value: ta.Optional[ta.Callable[[CborDecoder, CborTag], ta.Any]]) -> None:
        if value is None or callable(value):
            self._tag_hook = value
        else:
            raise ValueError('tag_hook must be None or a callable')

    @property
    def object_hook(self) -> ta.Optional[ta.Callable[[CborDecoder, ta.Dict[ta.Any, ta.Any]], ta.Any]]:
        return self._object_hook

    @object_hook.setter
    def object_hook(self, value: ta.Optional[ta.Callable[[CborDecoder, ta.Dict[ta.Any, ta.Any]], ta.Any]]) -> None:
        if value is None or callable(value):
            self._object_hook = value
        else:
            raise ValueError('object_hook must be None or a callable')

    @property
    def str_errors(self) -> str:
        return self._str_errors

    @str_errors.setter
    def str_errors(self, value: str) -> None:
        if value == 'error':
            self._str_errors = 'strict'
        elif value in ('strict', 'error', 'replace', 'backslashreplace', 'surrogateescape'):
            self._str_errors = value
        else:
            raise ValueError(
                f"invalid str_errors value {value!r} (must be 'strict', 'error', 'replace', "
                f"'backslashreplace' or 'surrogateescape')",
            )

    def set_shareable(self, value: T) -> T:
        """
        Set the shareable value for the last encountered shared value marker, if any. If the current shared index is
        ``None``, nothing is done.

        :param value: the shared value
        :returns: the shared value to permit chaining
        """

        if self._share_index is not None:
            self._shareables[self._share_index] = value

        return value

    def _stringref_namespace_add(self, string: str | bytes, length: int) -> None:
        if self._stringref_namespace is not None:
            next_index = len(self._stringref_namespace)
            if next_index < 24:
                is_referenced = length >= 3
            elif next_index < 256:
                is_referenced = length >= 4
            elif next_index < 65536:
                is_referenced = length >= 5
            elif next_index < 4294967296:
                is_referenced = length >= 7
            else:
                is_referenced = length >= 11

            if is_referenced:
                self._stringref_namespace.append(string)

    def read(self, amount: int) -> bytes:
        """
        Read bytes from the data stream.

        :param int amount: the number of bytes to read
        """

        data = self._fp_read(amount)
        if len(data) < amount:
            raise CborDecodeEOFError(
                f'premature end of stream (expected to read {amount} bytes, got {len(data)} '
                'instead)',
            )

        return data

    def decode(self, immutable: bool = False, unshared: bool = False) -> ta.Any:
        """
        Decode the next value from the stream.

        :raises CBORDecodeError: if there is any problem decoding the stream
        """

        if self._decode_depth > self._max_depth:
            raise CborDecodeError(f'maximum container nesting depth ({self._max_depth}) exceeded')

        if immutable:
            old_immutable = self._immutable
            self._immutable = True
        if unshared:
            old_index = self._share_index
            self._share_index = None

        self._decode_depth += 1
        try:
            initial_byte = self.read(1)[0]
            major_type = initial_byte >> 5
            subtype = initial_byte & 31
            decoder = CBOR_MAJOR_DECODERS[major_type]
            return decoder(self, subtype)
        finally:
            if immutable:
                self._immutable = old_immutable
            if unshared:
                self._share_index = old_index

            self._decode_depth -= 1
            if self._decode_depth < 0:
                raise ValueError('decode depth cannot be negative')
            if self._decode_depth == 0:
                self._shareables.clear()
                self._share_index = None

    def decode_from_bytes(self, buf: bytes) -> object:
        """
        Wrap the given bytestring as a file and call :meth:`decode` with it as the argument.

        This method was intended to be used from the ``tag_hook`` hook when an object needs to be decoded separately
        from the rest but while still taking advantage of the shared value registry.
        """

        with io.BytesIO(buf) as fp:
            old_fp = self.fp
            self.fp = fp
            retval = self.decode()
            self.fp = old_fp
            return retval

    @ta.overload
    def _decode_length(self, subtype: int) -> int: ...

    @ta.overload
    def _decode_length(self, subtype: int, allow_indefinite: ta.Literal[True]) -> ta.Optional[int]: ...

    def _decode_length(self, subtype: int, allow_indefinite: bool = False) -> ta.Optional[int]:
        if subtype < 24:
            return subtype
        elif subtype == 24:
            return self.read(1)[0]
        elif subtype == 25:
            return ta.cast(int, struct.unpack('>H', self.read(2))[0])
        elif subtype == 26:
            return ta.cast(int, struct.unpack('>L', self.read(4))[0])
        elif subtype == 27:
            return ta.cast(int, struct.unpack('>Q', self.read(8))[0])
        elif subtype == 31 and allow_indefinite:
            return None
        else:
            raise CborDecodeValueError(f'unknown unsigned integer subtype 0x{subtype:x}')

    def decode_uint(self, subtype: int) -> int:
        # Major tag 0
        return self.set_shareable(self._decode_length(subtype))

    def decode_negint(self, subtype: int) -> int:
        # Major tag 1
        return self.set_shareable(-self._decode_length(subtype) - 1)

    def decode_bytestring(self, subtype: int) -> bytes:
        # Major tag 2
        length = self._decode_length(subtype, allow_indefinite=True)
        if length is None:
            # Indefinite length
            buf: list[bytes] = []
            while True:
                initial_byte = self.read(1)[0]
                if initial_byte == 0xFF:
                    result = b''.join(buf)
                    break
                elif initial_byte >> 5 == 2:
                    length = self._decode_length(initial_byte & 0x1F)
                    if length is None or length > sys.maxsize:
                        raise CborDecodeValueError(
                            f'invalid length for indefinite bytestring chunk 0x{length:x}',
                        )
                    value = self.read(length)
                    buf.append(value)
                else:
                    raise CborDecodeValueError(
                        'non-bytestring found in indefinite length bytestring',
                    )
        else:
            if length > sys.maxsize:
                raise CborDecodeValueError(f'invalid length for bytestring 0x{length:x}')
            elif length <= 65536:
                result = self.read(length)
            else:
                # Read large bytestrings 65536 (2 ** 16) bytes at a time
                left = length
                buffer = bytearray()
                while left:
                    chunk_size = min(left, 65536)
                    buffer.extend(self.read(chunk_size))
                    left -= chunk_size

                result = bytes(buffer)

            self._stringref_namespace_add(result, length)

        return self.set_shareable(result)

    def decode_string(self, subtype: int) -> str:
        # Major tag 3
        length = self._decode_length(subtype, allow_indefinite=True)
        if length is None:
            # Indefinite length
            # NOTE: It may seem redundant to repeat this code to handle UTF-8 strings but there is a reason to do this
            # separately to byte-strings. Specifically, the CBOR spec states (in sec. 2.2):
            #
            #     Text strings with indefinite lengths act the same as byte strings with indefinite lengths, except that
            #     all their chunks MUST be definite-length text strings.  Note that this implies that the bytes of a
            #     single UTF-8 character cannot be spread between chunks: a new chunk can only be started at a character
            #     boundary.
            #
            # This precludes using the indefinite bytestring decoder above as that would happily ignore UTF-8 characters
            # split across chunks.
            buf: list[str] = []
            while True:
                initial_byte = self.read(1)[0]
                if initial_byte == 0xFF:
                    result = ''.join(buf)
                    break
                elif initial_byte >> 5 == 3:
                    length = self._decode_length(initial_byte & 0x1F)
                    if length is None or length > sys.maxsize:
                        raise CborDecodeValueError(f'invalid length for indefinite string chunk 0x{length:x}')

                    try:
                        value = self.read(length).decode('utf-8', self._str_errors)
                    except UnicodeDecodeError as exc:
                        raise CborDecodeValueError('error decoding unicode string') from exc

                    buf.append(value)
                else:
                    raise CborDecodeValueError('non-string found in indefinite length string')
        else:
            if length > sys.maxsize:
                raise CborDecodeValueError(f'invalid length for string 0x{length:x}')

            if length <= 65536:
                try:
                    result = self.read(length).decode('utf-8', self._str_errors)
                except UnicodeDecodeError as exc:
                    raise CborDecodeValueError('error decoding unicode string') from exc
            else:
                # Read and decode large text strings 65536 (2 ** 16) bytes at a time
                codec = _CBOR_INCREMENTAL_UTF8_DECODER(self._str_errors)
                left = length
                result = ''
                while left:
                    chunk_size = min(left, 65536)
                    final = left <= chunk_size
                    try:
                        result += codec.decode(self.read(chunk_size), final)
                    except UnicodeDecodeError as exc:
                        raise CborDecodeValueError('error decoding unicode string') from exc

                    left -= chunk_size

            self._stringref_namespace_add(result, length)

        return self.set_shareable(result)

    def decode_array(self, subtype: int) -> ta.Sequence[ta.Any]:
        # Major tag 4
        length = self._decode_length(subtype, allow_indefinite=True)
        if length is None:
            # Indefinite length
            items: list[ta.Any] = []
            if not self._immutable:
                self.set_shareable(items)
            while True:
                value = self.decode(unshared=True)
                if value is CBOR_BREAK_MARKER:
                    break
                else:
                    items.append(value)
        else:
            if length > sys.maxsize:
                raise CborDecodeValueError(f'invalid length for array 0x{length:x}')

            items = []
            if not self._immutable:
                self.set_shareable(items)

            for _index in range(length):
                items.append(self.decode(unshared=True))

        if self._immutable:
            items_tuple = tuple(items)
            self.set_shareable(items_tuple)
            return items_tuple

        return items

    def decode_map(self, subtype: int) -> ta.Mapping[ta.Any, ta.Any]:
        # Major tag 5
        length = self._decode_length(subtype, allow_indefinite=True)
        if length is None:
            # Indefinite length
            dictionary: ta.Dict[ta.Any, ta.Any] = {}
            self.set_shareable(dictionary)
            while True:
                key = self.decode(immutable=True, unshared=True)
                if key is CBOR_BREAK_MARKER:
                    break
                else:
                    dictionary[key] = self.decode(unshared=True)
        else:
            dictionary = {}
            self.set_shareable(dictionary)
            for _ in range(length):
                key = self.decode(immutable=True, unshared=True)
                dictionary[key] = self.decode(unshared=True)

        if self._object_hook:
            dictionary = self._object_hook(self, dictionary)
            self.set_shareable(dictionary)
        elif self._immutable:
            frozen_dict = CborFrozenDict(dictionary)
            self.set_shareable(dictionary)
            return frozen_dict

        return dictionary

    def decode_semantic(self, subtype: int) -> ta.Any:
        # Major tag 6
        tagnum = self._decode_length(subtype)
        if semantic_decoder := CBOR_SEMANTIC_DECODERS.get(tagnum):
            return semantic_decoder(self)

        tag = CborTag(tagnum, None)
        self.set_shareable(tag)
        tag.value = self.decode(unshared=True)
        if self._tag_hook:
            tag = self._tag_hook(self, tag)

        return self.set_shareable(tag)

    def decode_special(self, subtype: int) -> ta.Any:
        # Simple value
        if subtype < 20:
            # XXX Set shareable?
            return CborSimpleValue(subtype)

        # Major tag 7
        try:
            return CBOR_SPECIAL_DECODERS[subtype](self)
        except KeyError as e:
            raise CborDecodeValueError(
                f'Undefined Reserved major type 7 subtype 0x{subtype:x}',
            ) from e

    # Semantic decoders (major tag 6)

    def decode_epoch_date(self) -> datetime.date:
        # Semantic tag 100
        value = self.decode()
        return self.set_shareable(datetime.date.fromordinal(value + 719163))

    def decode_date_string(self) -> datetime.date:
        # Semantic tag 1004
        value = self.decode()
        return self.set_shareable(datetime.date.fromisoformat(value))

    def decode_datetime_string(self) -> datetime.datetime:
        # Semantic tag 0
        value = self.decode()
        match = _CBOR_TIMESTAMP_PAT.match(value)
        if match:
            (
                year,
                month,
                day,
                hour,
                minute,
                second,
                secfrac,
                offset_sign,
                offset_h,
                offset_m,
            ) = match.groups()
            if secfrac is None:
                microsecond = 0
            else:
                microsecond = int(f'{secfrac:<06}')

            if offset_h:
                if offset_sign == '-':
                    sign = -1
                else:
                    sign = 1
                hours = int(offset_h) * sign
                minutes = int(offset_m) * sign
                tz = datetime.timezone(datetime.timedelta(hours=hours, minutes=minutes))
            else:
                tz = datetime.timezone.utc  # noqa

            return self.set_shareable(
                datetime.datetime(
                    int(year),
                    int(month),
                    int(day),
                    int(hour),
                    int(minute),
                    int(second),
                    microsecond,
                    tz,
                ),
            )
        else:
            raise CborDecodeValueError(f'invalid datetime string: {value!r}')

    def decode_epoch_datetime(self) -> datetime.datetime:
        # Semantic tag 1
        value = self.decode()

        try:
            tmp = datetime.datetime.fromtimestamp(value, datetime.timezone.utc)  # noqa
        except (OverflowError, OSError, ValueError) as exc:
            raise CborDecodeValueError('error decoding datetime from epoch') from exc

        return self.set_shareable(tmp)

    def decode_positive_bignum(self) -> int:
        # Semantic tag 2
        value = self.decode()
        if not isinstance(value, bytes):
            raise CborDecodeValueError('invalid bignum value ' + str(value))

        return self.set_shareable(int(binascii.hexlify(value), 16))

    def decode_negative_bignum(self) -> int:
        # Semantic tag 3
        return self.set_shareable(-self.decode_positive_bignum() - 1)

    def decode_fraction(self) -> decimal.Decimal:
        # Semantic tag 4
        try:
            exp, sig = self.decode()
        except (TypeError, ValueError) as e:
            raise CborDecodeValueError('Incorrect tag 4 payload') from e
        tmp = decimal.Decimal(sig).as_tuple()
        return self.set_shareable(decimal.Decimal((tmp.sign, tmp.digits, exp)))

    def decode_bigfloat(self) -> decimal.Decimal:
        # Semantic tag 5
        try:
            exp, sig = self.decode()
        except (TypeError, ValueError) as e:
            raise CborDecodeValueError('Incorrect tag 5 payload') from e

        return self.set_shareable(decimal.Decimal(sig) * (2 ** decimal.Decimal(exp)))

    def decode_stringref(self) -> str | bytes:
        # Semantic tag 25
        if self._stringref_namespace is None:
            raise CborDecodeValueError('string reference outside of namespace')

        index: int = self.decode()
        try:
            value = self._stringref_namespace[index]
        except IndexError:
            raise CborDecodeValueError(f'string reference {index} not found') from None

        return value

    def decode_shareable(self) -> object:
        # Semantic tag 28
        old_index = self._share_index
        self._share_index = len(self._shareables)
        self._shareables.append(None)
        try:
            return self.decode()
        finally:
            self._share_index = old_index

    def decode_sharedref(self) -> ta.Any:
        # Semantic tag 29
        value = self.decode(unshared=True)
        try:
            shared = self._shareables[value]
        except IndexError:
            raise CborDecodeValueError(f'shared reference {value} not found') from None

        if shared is None:
            raise CborDecodeValueError(f'shared value {value} has not been initialized')
        else:
            return shared

    def decode_complex(self) -> complex:
        # Semantic tag 43000
        inputval = self.decode(immutable=True, unshared=True)
        try:
            value = complex(*inputval)
        except TypeError as exc:
            if not isinstance(inputval, tuple):
                raise CborDecodeValueError(
                    'error decoding complex: input value was not a tuple',
                ) from None

            raise CborDecodeValueError('error decoding complex') from exc

        return self.set_shareable(value)

    def decode_rational(self) -> fractions.Fraction:
        # Semantic tag 30
        inputval = self.decode(immutable=True, unshared=True)
        try:
            value = fractions.Fraction(*inputval)
        except (TypeError, ZeroDivisionError) as exc:
            if not isinstance(inputval, tuple):
                raise CborDecodeValueError('error decoding rational: input value was not a tuple') from None

            raise CborDecodeValueError('error decoding rational') from exc

        return self.set_shareable(value)

    def decode_regexp(self) -> re.Pattern[str]:
        # Semantic tag 35
        try:
            value = re.compile(self.decode())
        except re.error as exc:
            raise CborDecodeValueError('error decoding regular expression') from exc

        return self.set_shareable(value)

    def decode_mime(self) -> email.message.Message:
        # Semantic tag 36
        import email.parser  # noqa
        try:
            value = email.parser.Parser().parsestr(self.decode())
        except TypeError as exc:
            raise CborDecodeValueError('error decoding MIME message') from exc

        return self.set_shareable(value)

    def decode_uuid(self) -> uuid.UUID:
        # Semantic tag 37
        try:
            value = uuid.UUID(bytes=self.decode())
        except (TypeError, ValueError) as exc:
            raise CborDecodeValueError('error decoding UUID value') from exc

        return self.set_shareable(value)

    def decode_stringref_namespace(self) -> ta.Any:
        # Semantic tag 256
        old_namespace = self._stringref_namespace
        self._stringref_namespace = []
        value = self.decode()
        self._stringref_namespace = old_namespace
        return value

    def decode_set(self) -> ta.Union[ta.Set[ta.Any], ta.FrozenSet[ta.Any]]:
        # Semantic tag 258
        if self._immutable:
            return self.set_shareable(frozenset(self.decode(immutable=True)))
        else:
            return self.set_shareable(set(self.decode(immutable=True)))

    def decode_ipaddress(self) -> ipaddress.IPv4Address | ipaddress.IPv6Address | CborTag:
        # Semantic tag 260
        buf = self.decode()
        if not isinstance(buf, bytes) or len(buf) not in (4, 6, 16):
            raise CborDecodeValueError(f'invalid ipaddress value {buf!r}')
        elif len(buf) in (4, 16):
            return self.set_shareable(ipaddress.ip_address(buf))
        elif len(buf) == 6:
            # MAC address
            return self.set_shareable(CborTag(260, buf))

        raise CborDecodeValueError(f'invalid ipaddress value {buf!r}')

    def decode_ipnetwork(self) -> ipaddress.IPv4Network | ipaddress.IPv6Network:
        # Semantic tag 261
        net_map = self.decode()
        if isinstance(net_map, ta.Mapping) and len(net_map) == 1:
            for net in net_map.items():
                try:
                    return self.set_shareable(ipaddress.ip_network(net, strict=False))
                except (TypeError, ValueError):
                    break

        raise CborDecodeValueError(f'invalid ipnetwork value {net_map!r}')

    def decode_self_describe_cbor(self) -> ta.Any:
        # Semantic tag 55799
        return self.decode()

    # Special decoders (major tag 7)

    def decode_simple_value(self) -> CborSimpleValue:
        # XXX Set shareable?
        return CborSimpleValue(self.read(1)[0])

    def decode_float16(self) -> float:
        return self.set_shareable(ta.cast(float, struct.unpack('>e', self.read(2))[0]))

    def decode_float32(self) -> float:
        return self.set_shareable(ta.cast(float, struct.unpack('>f', self.read(4))[0]))

    def decode_float64(self) -> float:
        return self.set_shareable(ta.cast(float, struct.unpack('>d', self.read(8))[0]))


CBOR_MAJOR_DECODERS: ta.Dict[int, ta.Callable[[CborDecoder, int], ta.Any]] = {
    0: CborDecoder.decode_uint,
    1: CborDecoder.decode_negint,
    2: CborDecoder.decode_bytestring,
    3: CborDecoder.decode_string,
    4: CborDecoder.decode_array,
    5: CborDecoder.decode_map,
    6: CborDecoder.decode_semantic,
    7: CborDecoder.decode_special,
}

CBOR_SPECIAL_DECODERS: ta.Dict[int, ta.Callable[[CborDecoder], ta.Any]] = {
    20: lambda self: False,
    21: lambda self: True,
    22: lambda self: None,
    23: lambda self: CBOR_UNDEFINED,
    24: CborDecoder.decode_simple_value,
    25: CborDecoder.decode_float16,
    26: CborDecoder.decode_float32,
    27: CborDecoder.decode_float64,
    31: lambda self: CBOR_BREAK_MARKER,
}

CBOR_SEMANTIC_DECODERS: ta.Dict[int, ta.Callable[[CborDecoder], ta.Any]] = {
    0: CborDecoder.decode_datetime_string,
    1: CborDecoder.decode_epoch_datetime,
    2: CborDecoder.decode_positive_bignum,
    3: CborDecoder.decode_negative_bignum,
    4: CborDecoder.decode_fraction,
    5: CborDecoder.decode_bigfloat,
    25: CborDecoder.decode_stringref,
    28: CborDecoder.decode_shareable,
    29: CborDecoder.decode_sharedref,
    30: CborDecoder.decode_rational,
    35: CborDecoder.decode_regexp,
    36: CborDecoder.decode_mime,
    37: CborDecoder.decode_uuid,
    100: CborDecoder.decode_epoch_date,
    256: CborDecoder.decode_stringref_namespace,
    258: CborDecoder.decode_set,
    260: CborDecoder.decode_ipaddress,
    261: CborDecoder.decode_ipnetwork,
    1004: CborDecoder.decode_date_string,
    43000: CborDecoder.decode_complex,
    55799: CborDecoder.decode_self_describe_cbor,
}


##


def cbor_loads(
    s: bytes | bytearray | memoryview,
    tag_hook: ta.Optional[ta.Callable[[CborDecoder, CborTag], ta.Any]] = None,
    object_hook: ta.Optional[ta.Callable[[CborDecoder, ta.Dict[ta.Any, ta.Any]], ta.Any]] = None,
    str_errors: ta.Literal['strict', 'error', 'replace'] = 'strict',
    *,
    max_depth: int = 400,
) -> ta.Any:
    """
    Deserialize an object from a bytestring.

    :param bytes s:
        the bytestring to deserialize
    :param tag_hook:
        callable that takes 2 arguments: the decoder instance, and the :class:`.CBORTag` to be decoded. This callback is
        invoked for any tags for which there is no built-in decoder. The return value is substituted for the
        :class:`.CBORTag` object in the deserialized output
    :param object_hook:
        callable that takes 2 arguments: the decoder instance, and a dictionary. This callback is invoked for each
        deserialized :class:`dict` object. The return value is substituted for the dict in the deserialized output.
    :param str_errors:
        determines how to handle unicode decoding errors (see the `Error Handlers`_ section in the standard library
        documentation for details)
    :param max_depth:
        the maximum allowed container nesting depth
    :return:
        the deserialized object

    .. _Error Handlers: https://docs.python.org/3/library/codecs.html#error-handlers
    """

    with io.BytesIO(s) as fp:
        return CborDecoder(
            fp,
            tag_hook=tag_hook,
            object_hook=object_hook,
            str_errors=str_errors,
            max_depth=max_depth,
        ).decode()


def cbor_load(
    fp: ta.IO[bytes],
    tag_hook: ta.Optional[ta.Callable[[CborDecoder, CborTag], ta.Any]] = None,
    object_hook: ta.Optional[ta.Callable[[CborDecoder, ta.Dict[ta.Any, ta.Any]], ta.Any]] = None,
    str_errors: ta.Literal['strict', 'error', 'replace'] = 'strict',
    *,
    max_depth: int = 400,
) -> ta.Any:
    """
    Deserialize an object from an open file.

    :param fp:
        the file to read from (any file-like object opened for reading in binary mode)
    :param tag_hook:
        callable that takes 2 arguments: the decoder instance, and the :class:`.CBORTag` to be decoded. This callback is
        invoked for any tags for which there is no built-in decoder. The return value is substituted for the
        :class:`.CBORTag` object in the deserialized output
    :param object_hook:
        callable that takes 2 arguments: the decoder instance, and a dictionary. This callback is invoked for each
        deserialized :class:`dict` object. The return value is substituted for the dict in the deserialized output.
    :param str_errors:
        determines how to handle unicode decoding errors (see the `Error Handlers`_ section in the standard library
        documentation for details)
    :param max_depth:
        the maximum allowed container nesting depth
    :return:
        the deserialized object

    .. _Error Handlers: https://docs.python.org/3/library/codecs.html#error-handlers
    """

    return CborDecoder(
        fp,
        tag_hook=tag_hook,
        object_hook=object_hook,
        str_errors=str_errors,
        max_depth=max_depth,
    ).decode()

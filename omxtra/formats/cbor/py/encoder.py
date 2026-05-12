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
import calendar
import collections
import contextlib
import datetime
import decimal
import email.message
import fractions
import functools
import io
import ipaddress
import math
import re
import struct
import sys
import typing as ta
import uuid

from .types import CBOR_UNDEFINED
from .types import CborEncodeTypeError
from .types import CborEncodeValueError
from .types import CborFrozenDict
from .types import CborSimpleValue
from .types import CborTag
from .types import CborUndefinedType


##


def cbor_shareable_encoder(
    func: ta.Callable[[CborEncoder, ta.Any], None],
) -> ta.Callable[[CborEncoder, ta.Any], None]:
    """
    Wrap the given encoder function to gracefully handle cyclic data structures.

    If value sharing is enabled, this marks the given value shared in the datastream on the first call. If the value has
    already been passed to this method, a reference marker is instead written to the data stream and the wrapped
    function is not called.

    If value sharing is disabled, only infinite recursion protection is done.
    :rtype: Callable[[cbor2.CBOREncoder, Any], None]
    """

    @functools.wraps(func)
    def wrapper(encoder: CborEncoder, value: ta.Any) -> None:
        encoder.encode_shared(func, value)

    return wrapper


def cbor_container_encoder(
    func: ta.Callable[[CborEncoder, ta.Any], ta.Any],
) -> ta.Callable[[CborEncoder, ta.Any], ta.Any]:
    """
    The given encoder is a container with child values. Handle cyclic or duplicate references to the value and strings
    within the value efficiently.

    Containers may contain cyclic data structures or may contain values or themselves by referenced multiple times
    throughout the greater encoded value and could thus be more efficiently encoded with shared value references and
    string references where duplication occurs.

    If value sharing is enabled, this marks the given value shared in the datastream on the first call. If the value has
    already been passed to this method, a reference marker is instead written to the data stream and the wrapped
    function is not called.

    If value sharing is disabled, only infinite recursion protection is done.

    If string referencing is enabled and this is the first use of this method in encoding a value, all repeated
    references to long strings and bytearrays will be replaced with references to the first occurrence of those arrays.

    If string referencing is disabled, all strings and bytearrays will be encoded directly.
    """

    @functools.wraps(func)
    def wrapper(encoder: CborEncoder, value: ta.Any) -> None:
        encoder.encode_container(func, value)

    return wrapper


##


class CborEncoder:
    """
    The CBOREncoder class implements a fully featured `CBOR`_ encoder with several extensions for handling shared
    references, big integers, rational numbers and so on. Typically the class is not used directly, but the
    :func:`dump` and :func:`dumps` functions are called to indirectly construct and use the class.

    When the class is constructed manually, the main entry points are
    :meth:`encode` and :meth:`encode_to_bytes`.

    .. _CBOR: https://cbor.io/
    """

    __slots__ = (
        'datetime_as_timestamp',
        'date_as_datetime',
        '_timezone',
        '_default',
        'value_sharing',
        '_fp',
        '_fp_write',
        '_shared_containers',
        '_encoders',
        '_canonical',
        'string_referencing',
        'string_namespacing',
        '_string_references',
        'indefinite_containers',
        '_encode_depth',
    )

    _fp: ta.IO[bytes]
    _fp_write: ta.Callable[[ta.Any], int]

    def __init__(
        self,
        fp: ta.IO[bytes],
        datetime_as_timestamp: bool = False,
        timezone: datetime.tzinfo | None = None,
        value_sharing: bool = False,
        default: ta.Callable[[CborEncoder, ta.Any], ta.Any] | None = None,
        canonical: bool = False,
        date_as_datetime: bool = False,
        string_referencing: bool = False,
        indefinite_containers: bool = False,
    ):
        """
        :param fp:
            the file to write to (any file-like object opened for writing in binary mode)
        :param datetime_as_timestamp:
            set to ``True`` to serialize datetimes as UNIX timestamps (this makes datetimes more concise on the wire,
            but loses the timezone information)
        :param timezone:
            the default timezone to use for serializing naive datetimes; if this is not specified naive datetimes will
            throw a :exc:`ValueError` when encoding is attempted
        :param value_sharing:
            set to ``True`` to allow more efficient serializing of repeated values and, more importantly, cyclic data
            structures, at the cost of extra line overhead
        :param default:
            a callable that is called by the encoder with two arguments (the encoder instance and the value being
            encoded) when no suitable encoder has been found, and should use the methods on the encoder to encode any
            objects it wants to add to the data stream
        :param canonical:
            when ``True``, use "canonical" CBOR representation; this typically involves sorting maps, sets, etc. into a
            pre-determined order ensuring that serializations are comparable without decoding
        :param date_as_datetime:
            set to ``True`` to serialize date objects as datetimes (CBOR tag 0), which was the default behavior in
            previous releases (cbor2 <= 4.1.2).
        :param string_referencing:
            set to ``True`` to allow more efficient serializing of repeated string values
        :param indefinite_containers:
            encode containers as indefinite (use stop code instead of specifying length)
        """

        self.fp = fp
        self.datetime_as_timestamp = datetime_as_timestamp
        self.date_as_datetime = date_as_datetime
        self.timezone = timezone
        self.value_sharing = value_sharing
        self.string_referencing = string_referencing
        self.string_namespacing = string_referencing
        self.indefinite_containers = indefinite_containers
        self.default = default
        self._canonical = canonical
        self._shared_containers: ta.Dict[
            int, ta.Tuple[object, int | None],
        ] = {}  # indexes used for value sharing
        self._string_references: ta.Dict[str | bytes, int] = {}  # indexes used for string references
        self._encode_depth = 0
        self._encoders = CBOR_DEFAULT_ENCODERS.copy()
        if canonical:
            self._encoders.update(CBOR_CANONICAL_ENCODERS)

    def _find_encoder(self, obj_type: type) -> ta.Callable[[CborEncoder, ta.Any], None] | None:
        for type_or_tuple, enc in list(self._encoders.items()):
            if type(type_or_tuple) is tuple:
                try:
                    modname, typename = type_or_tuple
                except (TypeError, ValueError):
                    raise CborEncodeValueError(
                        f"invalid deferred encoder type {type_or_tuple!r} (must be a "
                        "2-tuple of module name and type name, e.g. "
                        "('collections', 'defaultdict'))",
                    )

                imported_type = getattr(sys.modules.get(modname), typename, None)
                if imported_type is not None:
                    del self._encoders[type_or_tuple]
                    self._encoders[imported_type] = enc
                    type_ = imported_type
                else:  # pragma: nocover
                    continue
            else:
                type_ = type_or_tuple

            if issubclass(obj_type, type_):
                self._encoders[obj_type] = enc
                return enc

        return None

    @property
    def fp(self) -> ta.IO[bytes]:
        return self._fp

    @fp.setter
    def fp(self, value: ta.IO[bytes]) -> None:
        try:
            if not callable(value.write):
                raise ValueError('fp.write is not callable')
        except AttributeError:
            raise ValueError('fp object has no write method')
        else:
            self._fp = value
            self._fp_write = value.write

    @property
    def timezone(self) -> datetime.tzinfo | None:
        return self._timezone

    @timezone.setter
    def timezone(self, value: datetime.tzinfo | None) -> None:
        if value is None or isinstance(value, datetime.tzinfo):
            self._timezone = value
        else:
            raise ValueError('timezone must be None or a tzinfo instance')

    @property
    def default(self) -> ta.Callable[[CborEncoder, ta.Any], ta.Any] | None:
        return self._default

    @default.setter
    def default(self, value: ta.Callable[[CborEncoder, ta.Any], ta.Any] | None) -> None:
        if value is None or callable(value):
            self._default = value
        else:
            raise ValueError('default must be None or a callable')

    @property
    def canonical(self) -> bool:
        return self._canonical

    @contextlib.contextmanager
    def disable_value_sharing(self) -> ta.Generator[None]:
        """Disable value sharing in the encoder for the duration of the context block."""

        old_value_sharing = self.value_sharing
        self.value_sharing = False
        yield
        self.value_sharing = old_value_sharing

    @contextlib.contextmanager
    def disable_string_referencing(self) -> ta.Generator[None]:
        """Disable tracking of string references for the duration of the context block."""

        old_string_referencing = self.string_referencing
        self.string_referencing = False
        yield
        self.string_referencing = old_string_referencing

    @contextlib.contextmanager
    def disable_string_namespacing(self) -> ta.Generator[None]:
        """Disable generation of new string namespaces for the duration of the context block."""

        old_string_namespacing = self.string_namespacing
        self.string_namespacing = False
        yield
        self.string_namespacing = old_string_namespacing

    def write(self, data: bytes) -> None:
        """
        Write bytes to the data stream.

        :param bytes data:
            the bytes to write
        """

        self._fp_write(data)

    @contextlib.contextmanager
    def _encoding_context(self) -> ta.Generator[None]:
        """
        Context manager for tracking encode depth and clearing shared state.

        Shared state is cleared at the end of each top-level encode to prevent shared references from leaking between
        independent encode operations. Nested calls (from hooks) must preserve the state.
        """

        self._encode_depth += 1
        try:
            yield
        finally:
            self._encode_depth -= 1
            if self._encode_depth == 0:
                self._shared_containers.clear()
                self._string_references.clear()

    def encode(self, obj: ta.Any) -> None:
        """
        Encode the given object using CBOR.

        :param obj:
            the object to encode
        """

        with self._encoding_context():
            self._encode_value(obj)

    def _encode_value(self, obj: ta.Any) -> None:
        """
        Internal fast path for encoding - used by built-in encoders.

        External code should use encode() instead, which properly manages shared state between independent encode
        operations.
        """

        obj_type = obj.__class__
        encoder = self._encoders.get(obj_type) or self._find_encoder(obj_type) or self._default
        if not encoder:
            raise CborEncodeTypeError(f'cannot serialize type {obj_type.__name__}')

        encoder(self, obj)

    def encode_to_bytes(self, obj: ta.Any) -> bytes:
        """
        Encode the given object to a byte buffer and return its value as bytes.

        This method was intended to be used from the ``default`` hook when an object needs to be encoded separately from
        the rest but while still taking advantage of the shared value registry.
        """

        with io.BytesIO() as fp:
            old_fp = self.fp
            self.fp = fp
            self.encode(obj)
            self.fp = old_fp
            return fp.getvalue()

    def encode_container(self, encoder: ta.Callable[[CborEncoder, ta.Any], ta.Any], value: ta.Any) -> None:
        if self.string_namespacing:
            # Create a new string reference domain
            self.encode_length(6, 256)

        with self.disable_string_namespacing():
            self.encode_shared(encoder, value)

    def encode_shared(self, encoder: ta.Callable[[CborEncoder, ta.Any], ta.Any], value: ta.Any) -> None:
        value_id = id(value)
        try:
            index = self._shared_containers[id(value)][1]
        except KeyError:
            if self.value_sharing:
                # Mark the container as shareable
                self._shared_containers[value_id] = (
                    value,
                    len(self._shared_containers),
                )
                self.encode_length(6, 0x1C)
                encoder(self, value)
            else:
                self._shared_containers[value_id] = (value, None)
                try:
                    encoder(self, value)
                finally:
                    del self._shared_containers[value_id]
        else:
            if self.value_sharing:
                # Generate a reference to the previous index instead of encoding this again
                self.encode_length(6, 0x1D)
                self.encode_int(ta.cast(int, index))
            else:
                raise CborEncodeValueError(
                    'cyclic data structure detected but value sharing is disabled',
                )

    def _stringref(self, value: str | bytes) -> bool:
        """
        Try to encode the string or bytestring as a reference.

        Returns True if a reference was generated, False if the string must still be emitted.
        """

        try:
            index = self._string_references[value]
            self.encode_semantic(CborTag(25, index))
            return True
        except KeyError:
            length = len(value)
            next_index = len(self._string_references)
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
                self._string_references[value] = next_index

            return False

    def encode_length(self, major_tag: int, length: int | None) -> None:
        major_tag <<= 5
        if length is None:  # Indefinite
            self._fp_write(struct.pack('>B', major_tag | 31))
        elif length < 24:
            self._fp_write(struct.pack('>B', major_tag | length))
        elif length < 256:
            self._fp_write(struct.pack('>BB', major_tag | 24, length))
        elif length < 65536:
            self._fp_write(struct.pack('>BH', major_tag | 25, length))
        elif length < 4294967296:
            self._fp_write(struct.pack('>BL', major_tag | 26, length))
        else:
            self._fp_write(struct.pack('>BQ', major_tag | 27, length))

    def encode_break(self) -> None:
        # Break stop code for indefinite containers
        self._fp_write(struct.pack('>B', (7 << 5) | 31))

    def encode_int(self, value: int) -> None:
        # Big integers (2 ** 64 and over)
        if value >= 18446744073709551616 or value < -18446744073709551616:
            if value >= 0:
                major_type = 0x02
            else:
                major_type = 0x03
                value = -value - 1

            payload = value.to_bytes((value.bit_length() + 7) // 8, 'big')
            self.encode_semantic(CborTag(major_type, payload))
        elif value >= 0:
            self.encode_length(0, value)
        else:
            self.encode_length(1, -(value + 1))

    def encode_bytestring(self, value: bytes) -> None:
        if self.string_referencing:
            if self._stringref(value):
                return

        self.encode_length(2, len(value))
        self._fp_write(value)

    def encode_bytearray(self, value: bytearray) -> None:
        self.encode_bytestring(bytes(value))

    def encode_string(self, value: str) -> None:
        if self.string_referencing:
            if self._stringref(value):
                return

        encoded = value.encode('utf-8')
        self.encode_length(3, len(encoded))
        self._fp_write(encoded)

    @cbor_container_encoder
    def encode_array(self, value: ta.Sequence[ta.Any]) -> None:
        self.encode_length(4, len(value) if not self.indefinite_containers else None)
        for item in value:
            self._encode_value(item)

        if self.indefinite_containers:
            self.encode_break()

    @cbor_container_encoder
    def encode_map(self, value: ta.Mapping[ta.Any, ta.Any]) -> None:
        self.encode_length(5, len(value) if not self.indefinite_containers else None)
        for key, val in value.items():
            self._encode_value(key)
            self._encode_value(val)

        if self.indefinite_containers:
            self.encode_break()

    def encode_sortable_key(self, value: ta.Any) -> ta.Tuple[int, bytes]:
        """
        Takes a key and calculates the length of its optimal byte representation, along with the representation itself.
        This is used as the sorting key in CBOR's canonical representations.
        """

        with self.disable_string_referencing():
            encoded = self.encode_to_bytes(value)
            return len(encoded), encoded

    @cbor_container_encoder
    def encode_canonical_map(self, value: ta.Mapping[ta.Any, ta.Any]) -> None:
        """Reorder keys according to Canonical CBOR specification"""

        keyed_keys = ((self.encode_sortable_key(key), key, value) for key, value in value.items())
        self.encode_length(5, len(value) if not self.indefinite_containers else None)
        for sortkey, realkey, value in sorted(keyed_keys):
            if self.string_referencing:
                # String referencing requires that the order encoded is the same as the order emitted so string
                # references are generated after an order is determined
                self._encode_value(realkey)
            else:
                self._fp_write(sortkey[1])
            self._encode_value(value)

        if self.indefinite_containers:
            self.encode_break()

    def encode_semantic(self, value: CborTag) -> None:
        # Nested string reference domains are distinct
        old_string_referencing = self.string_referencing
        old_string_references = self._string_references
        if value.tag == 256:
            self.string_referencing = True
            self._string_references = {}

        self.encode_length(6, value.tag)
        self._encode_value(value.value)

        self.string_referencing = old_string_referencing
        self._string_references = old_string_references

    # Semantic decoders (major tag 6)

    def encode_datetime(self, value: datetime.datetime) -> None:
        # Semantic tag 0
        if not value.tzinfo:
            if self._timezone:
                value = value.replace(tzinfo=self._timezone)
            else:
                raise CborEncodeValueError(f'naive datetime {value!r} encountered and no default timezone has been set')

        if self.datetime_as_timestamp:
            if not value.microsecond:
                timestamp: float = calendar.timegm(value.utctimetuple())
            else:
                timestamp = calendar.timegm(value.utctimetuple()) + value.microsecond / 1000000

            self.encode_semantic(CborTag(1, timestamp))
        else:
            datestring = value.isoformat().replace('+00:00', 'Z')
            self.encode_semantic(CborTag(0, datestring))

    def encode_date(self, value: datetime.date) -> None:
        # Semantic tag 100
        if self.date_as_datetime:
            value = datetime.datetime.combine(value, datetime.time()).replace(tzinfo=self._timezone)
            self.encode_datetime(value)
        elif self.datetime_as_timestamp:
            days_since_epoch = value.toordinal() - 719163
            self.encode_semantic(CborTag(100, days_since_epoch))
        else:
            datestring = value.isoformat()
            self.encode_semantic(CborTag(1004, datestring))

    def encode_decimal(self, value: decimal.Decimal) -> None:
        # Semantic tag 4
        if value.is_nan():
            self._fp_write(b'\xf9\x7e\x00')
        elif value.is_infinite():
            self._fp_write(b'\xf9\x7c\x00' if value > 0 else b'\xf9\xfc\x00')
        else:
            dt = value.as_tuple()
            sig = 0
            for digit in dt.digits:
                sig = (sig * 10) + digit
            if dt.sign:
                sig = -sig
            with self.disable_value_sharing():
                self.encode_semantic(CborTag(4, [dt.exponent, sig]))

    def encode_stringref(self, value: str | bytes) -> None:
        # Semantic tag 25
        if not self._stringref(value):
            self._encode_value(value)

    def encode_rational(self, value: fractions.Fraction) -> None:
        # Semantic tag 30
        with self.disable_value_sharing():
            self.encode_semantic(CborTag(30, [value.numerator, value.denominator]))

    def encode_regexp(self, value: re.Pattern[str]) -> None:
        # Semantic tag 35
        self.encode_semantic(CborTag(35, str(value.pattern)))

    def encode_mime(self, value: email.message.Message) -> None:
        # Semantic tag 36
        self.encode_semantic(CborTag(36, value.as_string()))

    def encode_uuid(self, value: uuid.UUID) -> None:
        # Semantic tag 37
        self.encode_semantic(CborTag(37, value.bytes))

    def encode_stringref_namespace(self, value: ta.Any) -> None:
        # Semantic tag 256
        with self.disable_string_namespacing():
            self.encode_semantic(CborTag(256, value))

    def encode_set(self, value: ta.Set[ta.Any]) -> None:
        # Semantic tag 258
        self.encode_semantic(CborTag(258, tuple(value)))

    def encode_canonical_set(self, value: ta.Set[ta.Any]) -> None:
        # Semantic tag 258
        values = sorted((self.encode_sortable_key(key), key) for key in value)
        self.encode_semantic(CborTag(258, [key[1] for key in values]))

    def encode_ipaddress(self, value: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
        # Semantic tag 260
        self.encode_semantic(CborTag(260, value.packed))

    def encode_ipnetwork(self, value: ipaddress.IPv4Network | ipaddress.IPv6Network) -> None:
        # Semantic tag 261
        self.encode_semantic(CborTag(261, {value.network_address.packed: value.prefixlen}))

    # Special encoders (major tag 7)

    def encode_simple_value(self, value: CborSimpleValue) -> None:
        if value.value < 24:
            self._fp_write(struct.pack('>B', 0xE0 | value.value))
        else:
            self._fp_write(struct.pack('>BB', 0xF8, value.value))

    def encode_float(self, value: float) -> None:
        # Handle special values efficiently
        if math.isnan(value):
            self._fp_write(b'\xf9\x7e\x00')
        elif math.isinf(value):
            self._fp_write(b'\xf9\x7c\x00' if value > 0 else b'\xf9\xfc\x00')
        else:
            self._fp_write(struct.pack('>Bd', 0xFB, value))

    def encode_complex(self, value: complex) -> None:
        # Semantic tag 43000
        with self.disable_value_sharing():
            self.encode_semantic(CborTag(43000, [value.real, value.imag]))

    def encode_minimal_float(self, value: float) -> None:
        # Handle special values efficiently
        if math.isnan(value):
            self._fp_write(b'\xf9\x7e\x00')
        elif math.isinf(value):
            self._fp_write(b'\xf9\x7c\x00' if value > 0 else b'\xf9\xfc\x00')
        else:
            # Try each encoding in turn from longest to shortest
            encoded = struct.pack('>Bd', 0xFB, value)
            for format, tag in [('>Bf', 0xFA), ('>Be', 0xF9)]:
                try:
                    new_encoded = struct.pack(format, tag, value)
                    # Check if encoding as low-byte float loses precision
                    if struct.unpack(format, new_encoded)[1] == value:
                        encoded = new_encoded
                    else:
                        break
                except OverflowError:
                    break

            self._fp_write(encoded)

    def encode_boolean(self, value: bool) -> None:
        self._fp_write(b'\xf5' if value else b'\xf4')

    def encode_none(self, value: None) -> None:
        self._fp_write(b'\xf6')

    def encode_undefined(self, value: CborUndefinedType) -> None:
        self._fp_write(b'\xf7')


CBOR_DEFAULT_ENCODERS: ta.Dict[type | ta.Tuple[str, str], ta.Callable[[CborEncoder, ta.Any], None]] = {
    bytes: CborEncoder.encode_bytestring,
    bytearray: CborEncoder.encode_bytearray,
    str: CborEncoder.encode_string,
    int: CborEncoder.encode_int,
    float: CborEncoder.encode_float,
    complex: CborEncoder.encode_complex,
    ('decimal', 'Decimal'): CborEncoder.encode_decimal,
    bool: CborEncoder.encode_boolean,
    type(None): CborEncoder.encode_none,
    tuple: CborEncoder.encode_array,
    list: CborEncoder.encode_array,
    dict: CborEncoder.encode_map,
    collections.defaultdict: CborEncoder.encode_map,
    collections.OrderedDict: CborEncoder.encode_map,
    CborFrozenDict: CborEncoder.encode_map,
    type(CBOR_UNDEFINED): CborEncoder.encode_undefined,
    datetime.datetime: CborEncoder.encode_datetime,
    datetime.date: CborEncoder.encode_date,
    re.Pattern: CborEncoder.encode_regexp,
    ('fractions', 'Fraction'): CborEncoder.encode_rational,
    ('email.message', 'Message'): CborEncoder.encode_mime,
    ('uuid', 'UUID'): CborEncoder.encode_uuid,
    ('ipaddress', 'IPv4Address'): CborEncoder.encode_ipaddress,
    ('ipaddress', 'IPv6Address'): CborEncoder.encode_ipaddress,
    ('ipaddress', 'IPv4Network'): CborEncoder.encode_ipnetwork,
    ('ipaddress', 'IPv6Network'): CborEncoder.encode_ipnetwork,
    CborSimpleValue: CborEncoder.encode_simple_value,
    CborTag: CborEncoder.encode_semantic,
    set: CborEncoder.encode_set,
    frozenset: CborEncoder.encode_set,
}


CBOR_CANONICAL_ENCODERS: ta.Dict[type | ta.Tuple[str, str], ta.Callable[[CborEncoder, ta.Any], None]] = {
    float: CborEncoder.encode_minimal_float,
    dict: CborEncoder.encode_canonical_map,
    collections.defaultdict: CborEncoder.encode_canonical_map,
    collections.OrderedDict: CborEncoder.encode_canonical_map,
    CborFrozenDict: CborEncoder.encode_canonical_map,
    set: CborEncoder.encode_canonical_set,
    frozenset: CborEncoder.encode_canonical_set,
}


##


def cbor_dumps(
    obj: object,
    datetime_as_timestamp: bool = False,
    timezone: datetime.tzinfo | None = None,
    value_sharing: bool = False,
    default: ta.Callable[[CborEncoder, ta.Any], None] | None = None,
    canonical: bool = False,
    date_as_datetime: bool = False,
    string_referencing: bool = False,
    indefinite_containers: bool = False,
) -> bytes:
    """
    Serialize an object to a bytestring.

    :param obj:
        the object to serialize
    :param datetime_as_timestamp:
        set to ``True`` to serialize datetimes as UNIX timestamps (this makes datetimes more concise on the wire, but
        loses the timezone information)
    :param timezone:
        the default timezone to use for serializing naive datetimes; if this is not specified naive datetimes will throw
        a :exc:`ValueError` when encoding is attempted
    :param value_sharing:
        set to ``True`` to allow more efficient serializing of repeated values and, more importantly, cyclic data
        structures, at the cost of extra line overhead
    :param default:
        a callable that is called by the encoder with two arguments (the encoder instance and the value being encoded)
        when no suitable encoder has been found, and should use the methods on the encoder to encode any objects it
        wants to add to the data stream
    :param canonical:
        when ``True``, use "canonical" CBOR representation; this typically involves sorting maps, sets, etc. into a
        pre-determined order ensuring that serializations are comparable without decoding
    :param date_as_datetime:
        set to ``True`` to serialize date objects as datetimes (CBOR tag 0), which was the default behavior in previous
        releases (cbor2 <= 4.1.2).
    :param string_referencing:
        set to ``True`` to allow more efficient serializing of repeated string values
    :param indefinite_containers:
        encode containers as indefinite (use stop code instead of specifying length)
    :return: the serialized output
    """

    with io.BytesIO() as fp:
        CborEncoder(
            fp,
            datetime_as_timestamp=datetime_as_timestamp,
            timezone=timezone,
            value_sharing=value_sharing,
            default=default,
            canonical=canonical,
            date_as_datetime=date_as_datetime,
            string_referencing=string_referencing,
            indefinite_containers=indefinite_containers,
        ).encode(obj)
        return fp.getvalue()


def cbor_dump(
    obj: object,
    fp: ta.IO[bytes],
    datetime_as_timestamp: bool = False,
    timezone: datetime.tzinfo | None = None,
    value_sharing: bool = False,
    default: ta.Callable[[CborEncoder, ta.Any], None] | None = None,
    canonical: bool = False,
    date_as_datetime: bool = False,
    string_referencing: bool = False,
    indefinite_containers: bool = False,
) -> None:
    """
    Serialize an object to a file.

    :param obj:
        the object to serialize
    :param fp:
        the file to write to (any file-like object opened for writing in binary mode)
    :param datetime_as_timestamp:
        set to ``True`` to serialize datetimes as UNIX timestamps (this makes datetimes more concise on the wire, but
        loses the timezone information)
    :param timezone:
        the default timezone to use for serializing naive datetimes; if this is not specified naive datetimes will throw
        a :exc:`ValueError` when encoding is attempted
    :param value_sharing:
        set to ``True`` to allow more efficient serializing of repeated values and, more importantly, cyclic data
        structures, at the cost of extra line overhead
    :param default:
        a callable that is called by the encoder with two arguments (the encoder instance and the value being encoded)
        when no suitable encoder has been found, and should use the methods on the encoder to encode any objects it
        wants to add to the data stream
    :param canonical:
        when ``True``, use "canonical" CBOR representation; this typically involves sorting maps, sets, etc. into a
        pre-determined order ensuring that serializations are comparable without decoding
    :param date_as_datetime:
        set to ``True`` to serialize date objects as datetimes (CBOR tag 0), which was the default behavior in previous
        releases (cbor2 <= 4.1.2).
    :param indefinite_containers:
        encode containers as indefinite (use stop code instead of specifying length)
    :param string_referencing:
        set to ``True`` to allow more efficient serializing of repeated string values
    """

    CborEncoder(
        fp,
        datetime_as_timestamp=datetime_as_timestamp,
        timezone=timezone,
        value_sharing=value_sharing,
        default=default,
        canonical=canonical,
        date_as_datetime=date_as_datetime,
        string_referencing=string_referencing,
        indefinite_containers=indefinite_containers,
    ).encode(obj)

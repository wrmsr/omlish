from libc.stdint cimport uint64_t
from libc.stdint cimport uint8_t
import uuid


cdef extern from "Python.h":
    int PyUnicode_READY(object o)
    int PyUnicode_KIND(object o)
    Py_ssize_t PyUnicode_GET_LENGTH(object o)
    void* PyUnicode_DATA(object o)
    ctypedef enum PyUnicode_Kind:
        PyUnicode_WCHAR_KIND,
        PyUnicode_1BYTE_KIND,
        PyUnicode_2BYTE_KIND,
        PyUnicode_4BYTE_KIND,


bytes_ = bytes
object_new = object.__new__
object_setattr = object.__setattr__
UUID = uuid.UUID


def make(
        hex=None,
        bytes=None,
        bytes_le=None,
        fields=None,
        _int=None,
        version=None,
        *,
        is_safe=uuid.SafeUUID.unknown,
):
    self = object_new(UUID)

    cdef int ct = 0
    if hex is not None: ct += 1
    if bytes is not None: ct += 1
    if bytes_le is not None: ct += 1
    if fields is not None: ct += 1
    if _int is not None: ct += 1
    if ct != 1:
        raise TypeError('one of the hex, bytes, bytes_le, fields, or int arguments must be given')

    cdef Py_ssize_t sz;
    cdef char* p;
    cdef uint64_t low_part = 0L
    cdef uint64_t high_part = 0L
    cdef int i
    cdef uint8_t b

    if hex is not None:
        hex_ = <str> hex

        if PyUnicode_READY(hex_) == 0 and PyUnicode_KIND(hex_) == PyUnicode_1BYTE_KIND:
            sz = PyUnicode_GET_LENGTH(hex_)
            p = <char*> PyUnicode_DATA(hex_)
            if sz >= 4 and (
                    p[0] == ord('u') and
                    p[1] == ord('r') and
                    p[2] == ord('n') and
                    p[3] == ord(':')
            ):
                p += 4
                sz -= 4
            if sz >= 5 and (
                    p[0] == ord('u') and
                    p[1] == ord('u') and
                    p[2] == ord('i') and
                    p[3] == ord('d') and
                    p[4] == ord(':')
            ):
                p += 5
                sz -= 5
            if sz > 0 and p[0] == ord('{'):
                p += 1
                sz -= 1

            i = 0

            while i < 16 and sz > 0:
                b = <uint8_t> p[0]
                p += 1
                sz -= 1
                if ord('0') <= b <= ord('9'):
                    b = b - ord('0')
                elif ord('a') <= b <= ord('f'):
                    b = b - ord('a') + 10
                elif ord('A') <= b <= ord('F'):
                    b = b - ord('A') + 10
                elif b == ord('-'):
                    continue
                else:
                    raise ValueError('badly formed hexadecimal UUID string')
                i += 1
                high_part = (high_part << 4) | (b & 0xF)

            while i < 32 and sz > 0:
                b = <uint8_t> p[0]
                p += 1
                sz -= 1
                if ord('0') <= b <= ord('9'):
                    b = b - ord('0')
                elif ord('a') <= b <= ord('f'):
                    b = b - ord('a') + 10
                elif ord('A') <= b <= ord('F'):
                    b = b - ord('A') + 10
                elif b == ord('-'):
                    continue
                else:
                    raise ValueError('badly formed hexadecimal UUID string')
                i += 1
                low_part = (low_part << 4) | (b & 0xF)

            if sz > 0 and p[0] == ord('}'):
                p += 1
                sz -= 1
            if i != 32 or sz != 0:
                raise ValueError('badly formed hexadecimal UUID string')

            if version is not None:
                if not 1 <= version <= 5:
                    raise ValueError('illegal version number')

                # Set the variant to RFC 4122.
                low_part &= ~(0xc000 << 48)
                low_part |= 0x8000 << 48

                # Set the version number.
                high_part &= ~0xf000
                high_part |= version << 12

            _int = high_part
            _int <<= 64
            _int |= low_part

            object_setattr(self, 'int', _int)
            object_setattr(self, 'is_safe', is_safe)

            return self

        hex_ = hex_.replace('urn:', '').replace('uuid:', '')
        hex_ = hex_.strip('{}').replace('-', '')

        if len(hex_) != 32:
            raise ValueError('badly formed hexadecimal UUID string')

        _int = int(hex_, 16)

    if bytes_le is not None:
        if len(bytes_le) != 16:
            raise ValueError('bytes_le is not a 16-char string')

        bytes = (
                bytes_le[4 - 1::-1] +
                bytes_le[6 - 1:4 - 1:-1] +
                bytes_le[8 - 1:6 - 1:-1] +
                bytes_le[8:]
        )

    if bytes is not None:
        if len(bytes) != 16:
            raise ValueError('bytes is not a 16-char string')

        assert isinstance(bytes, bytes_), repr(bytes)

        _int = int.from_bytes(bytes, byteorder='big')

    if fields is not None:
        if len(fields) != 6:
            raise ValueError('fields is not a 6-tuple')

        (
            time_low,
            time_mid,
            time_hi_version,
            clock_seq_hi_variant,
            clock_seq_low,
            node
        ) = fields

        if not 0 <= time_low < 1 << 32:
            raise ValueError('field 1 out of range (need a 32-bit value)')

        if not 0 <= time_mid < 1 << 16:
            raise ValueError('field 2 out of range (need a 16-bit value)')

        if not 0 <= time_hi_version < 1 << 16:
            raise ValueError('field 3 out of range (need a 16-bit value)')

        if not 0 <= clock_seq_hi_variant < 1 << 8:
            raise ValueError('field 4 out of range (need an 8-bit value)')

        if not 0 <= clock_seq_low < 1 << 8:
            raise ValueError('field 5 out of range (need an 8-bit value)')

        if not 0 <= node < 1 << 48:
            raise ValueError('field 6 out of range (need a 48-bit value)')

        clock_seq = (clock_seq_hi_variant << 8) | clock_seq_low

        _int = (
                (time_low << 96) |
                (time_mid << 80) |
                (time_hi_version << 64) |
                (clock_seq << 48) |
                node
        )

    if _int is not None:
        if not 0 <= _int < 1 << 128:
            raise ValueError('int is out of range (need a 128-bit value)')

    if version is not None:
        if not 1 <= version <= 5:
            raise ValueError('illegal version number')

        # Set the variant to RFC 4122.
        _int &= ~(0xc000 << 48)
        _int |= 0x8000 << 48

        # Set the version number.
        _int &= ~(0xf000 << 64)
        _int |= version << 76

    object.__setattr__(self, 'int', int)
    object.__setattr__(self, 'is_safe', is_safe)

    return self

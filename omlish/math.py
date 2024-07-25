import functools
import struct
import typing as ta


##


def isclose(a: float, b: float, *, rel_tol: float = 1e-09, abs_tol: float = 0.0) -> float:
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def get_bit(bit: int, value: int) -> int:
    return (value >> bit) & 1


def get_bits(bits_from: int, num_bits: int, value: int) -> int:
    return (value & ((1 << (bits_from + num_bits)) - 1)) >> bits_from


def set_bit(bit: int, bit_value: int, value: int) -> int:
    if bit_value:
        return value | (1 << bit)
    else:
        return value & ~(1 << bit)


def set_bits(bits_from: int, num_bits: int, bits_value: int, value: int) -> int:
    return value & ~(((1 << num_bits) - 1) << bits_from) | (bits_value << bits_from)


def float_to_bytes(f: float) -> bytes:
    return struct.pack('>f', f)


def bytes_to_float(b: bytes) -> float:
    return struct.unpack('>f', b)[0]


##


def _gen_scalar_proxy_method(name):
    def inner(self, *args, **kwargs):
        return self.__class__(orig(self, *args, **kwargs))

    orig = getattr(int, name)
    return functools.wraps(orig)(inner)


def _gen_tuple_proxy_method(name):
    def inner(self, *args, **kwargs):
        return tuple(map(self.__class__, orig(self, *args, **kwargs)))

    orig = getattr(int, name)
    return functools.wraps(orig)(inner)


class FixedWidthInt(int):

    BITS: ta.ClassVar[int]
    SIGNED: ta.ClassVar[bool]

    MIN: ta.ClassVar[int]
    MAX: ta.ClassVar[int]

    MASK: ta.ClassVar[int]

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if not isinstance(cls.BITS, int):
            raise TypeError(cls.BITS)

        if cls.SIGNED:
            cls.MIN = -(1 << (cls.BITS - 1))
            cls.MAX = (1 << (cls.BITS - 1)) - 1
        else:
            cls.MIN = 0
            cls.MAX = (1 << cls.BITS) - 1

        cls.MASK = (1 << cls.BITS) - 1

    @classmethod
    def clamp(cls, value: int) -> int:
        return ((value - cls.MIN) & cls.MASK) + cls.MIN

    def __new__(cls, value: int) -> 'FixedWidthInt':
        return super().__new__(cls, cls.clamp(value))  # noqa

    SCALAR_PROXY_METHODS = frozenset([
        '__abs__',
        '__add__',
        '__and__',
        '__floordiv__',
        '__invert__',
        '__lshift__',
        '__mod__',
        '__mul__',
        '__neg__',
        '__or__',
        '__pos__',
        '__pow__',
        '__radd__',
        '__rand__',
        '__rfloordiv__',
        '__rlshift__',
        '__rmod__',
        '__rmul__',
        '__ror__',
        '__rpow__',
        '__rrshift__',
        '__rshift__',
        '__rsub__',
        '__rtruediv__',
        '__rxor__',
        '__sub__',
        '__truediv__',
        '__xor__',
    ])

    TUPLE_PROXY_METHODS = frozenset([
        '__divmod__',
        '__rdivmod__',
    ])

    for _proxy_name in SCALAR_PROXY_METHODS:
        locals()[_proxy_name] = _gen_scalar_proxy_method(_proxy_name)
    for _proxy_name in TUPLE_PROXY_METHODS:
        locals()[_proxy_name] = _gen_tuple_proxy_method(_proxy_name)
    del _proxy_name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({int(self)})'


class Int8(FixedWidthInt):
    BITS = 8
    SIGNED = True


class Int16(FixedWidthInt):
    BITS = 16
    SIGNED = True


class Int32(FixedWidthInt):
    BITS = 32
    SIGNED = True


class Int64(FixedWidthInt):
    BITS = 64
    SIGNED = True


class Int128(FixedWidthInt):
    BITS = 128
    SIGNED = True


class Uint8(FixedWidthInt):
    BITS = 8
    SIGNED = False


class Uint16(FixedWidthInt):
    BITS = 16
    SIGNED = False


class Uint32(FixedWidthInt):
    BITS = 32
    SIGNED = False


class Uint64(FixedWidthInt):
    BITS = 64
    SIGNED = False


class Uint128(FixedWidthInt):
    BITS = 128
    SIGNED = False

import enum
import functools
import typing as ta

from .. import check
from .. import lang


##


class CheckedFixedWidthIntError(ValueError):
    pass


class OverflowFixedWidthIntError(CheckedFixedWidthIntError):
    pass


class UnderflowFixedWidthIntError(CheckedFixedWidthIntError):
    pass


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


class FixedWidthInt(int, lang.Abstract):
    BITS: ta.ClassVar[int]

    #

    class Mode(enum.StrEnum):
        CHECKED = enum.auto()
        CLAMPED = enum.auto()

    MODE: ta.ClassVar[Mode]

    SIGNED: ta.ClassVar[bool]

    #

    MIN: ta.ClassVar[int]
    MAX: ta.ClassVar[int]

    MASK: ta.ClassVar[int]

    #

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()

        if lang.is_abstract_class(cls):
            return

        bits = check.single({
            check.isinstance(bbits, int)
            for bcls in cls.__mro__
            if (bbits := bcls.__dict__.get('BITS')) is not None
        })

        #

        if issubclass(cls, SignedInt):
            check.not_issubclass(cls, UnsignedInt)
            cls.SIGNED = True
            cls.MIN = -(1 << (bits - 1))
            cls.MAX = (1 << (bits - 1)) - 1

        elif issubclass(cls, UnsignedInt):
            check.not_issubclass(cls, SignedInt)
            cls.SIGNED = False
            cls.MIN = 0
            cls.MAX = (1 << bits) - 1

        else:
            raise TypeError(cls)

        #

        if issubclass(cls, CheckedInt):
            check.not_issubclass(cls, ClampedInt)
            cls.MODE = cls.Mode.CHECKED

        elif issubclass(cls, ClampedInt):
            check.not_issubclass(cls, CheckedInt)
            cls.MODE = cls.Mode.CLAMPED

        else:
            raise TypeError(cls)

        #

        cls.MASK = (1 << cls.BITS) - 1

    @classmethod
    def clamp(cls, value: int) -> int:
        return ((value - cls.MIN) & cls.MASK) + cls.MIN

    def __new__(cls, value: int) -> 'FixedWidthInt':
        return super().__new__(cls, cls.clamp(value))  # noqa

    _SCALAR_PROXY_METHODS = frozenset([
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

    _TUPLE_PROXY_METHODS = frozenset([
        '__divmod__',
        '__rdivmod__',
    ])

    for _proxy_name in _SCALAR_PROXY_METHODS:
        locals()[_proxy_name] = _gen_scalar_proxy_method(_proxy_name)
    for _proxy_name in _TUPLE_PROXY_METHODS:
        locals()[_proxy_name] = _gen_tuple_proxy_method(_proxy_name)
    del _proxy_name

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({int(self)})'


##


class SignedInt(FixedWidthInt, lang.Abstract):
    pass


class UnsignedInt(FixedWidthInt, lang.Abstract):
    pass


#


class CheckedInt(FixedWidthInt, lang.Abstract):
    pass


class ClampedInt(FixedWidthInt, lang.Abstract):
    pass


#


class AnyInt8(FixedWidthInt, lang.Abstract):
    BITS = 8


class AnyInt16(FixedWidthInt, lang.Abstract):
    BITS = 16


class AnyInt32(FixedWidthInt, lang.Abstract):
    BITS = 32


class AnyInt64(FixedWidthInt, lang.Abstract):
    BITS = 64


class AnyInt128(FixedWidthInt, lang.Abstract):
    BITS = 128


##


class CheckedInt8(CheckedInt, SignedInt, AnyInt8):
    pass


class CheckedInt16(CheckedInt, SignedInt, AnyInt16):
    pass


class CheckedInt32(CheckedInt, SignedInt, AnyInt32):
    pass


class CheckedInt64(CheckedInt, SignedInt, AnyInt64):
    pass


class CheckedInt128(CheckedInt, SignedInt, AnyInt128):
    pass


#


class CheckedUInt8(CheckedInt, UnsignedInt, AnyInt8):
    pass


class CheckedUInt16(CheckedInt, UnsignedInt, AnyInt16):
    pass


class CheckedUInt32(CheckedInt, UnsignedInt, AnyInt32):
    pass


class CheckedUInt64(CheckedInt, UnsignedInt, AnyInt64):
    pass


class CheckedUInt128(CheckedInt, UnsignedInt, AnyInt128):
    pass


#


class ClampedInt8(ClampedInt, SignedInt, AnyInt8):
    pass


class ClampedInt16(ClampedInt, SignedInt, AnyInt16):
    pass


class ClampedInt32(ClampedInt, SignedInt, AnyInt32):
    pass


class ClampedInt64(ClampedInt, SignedInt, AnyInt64):
    pass


class ClampedInt128(ClampedInt, SignedInt, AnyInt128):
    pass


#


class ClampedUInt8(ClampedInt, UnsignedInt, AnyInt8):
    pass


class ClampedUInt16(ClampedInt, UnsignedInt, AnyInt16):
    pass


class ClampedUInt32(ClampedInt, UnsignedInt, AnyInt32):
    pass


class ClampedUInt64(ClampedInt, UnsignedInt, AnyInt64):
    pass


class ClampedUInt128(ClampedInt, UnsignedInt, AnyInt128):
    pass

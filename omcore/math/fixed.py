import enum
import functools
import typing as ta

from .. import check
from .. import lang


FixedWidthIntT = ta.TypeVar('FixedWidthIntT', bound='FixedWidthInt')


##


class CheckedFixedWidthIntError(ValueError):
    pass


class OverflowFixedWidthIntError(CheckedFixedWidthIntError):
    pass


class UnderflowFixedWidthIntError(CheckedFixedWidthIntError):
    pass


##


def _get_exclusive_base_cls(cls: type, base_classes: ta.Iterable[type]) -> type:
    return check.single(bcls for bcls in base_classes if issubclass(cls, bcls))


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
        CHECK = enum.auto()
        CLAMP = enum.auto()
        WRAP = enum.auto()

    MODE: ta.ClassVar[Mode]

    SIGNED: ta.ClassVar[bool]

    #

    MIN: ta.ClassVar[int]
    MAX: ta.ClassVar[int]

    MASK: ta.ClassVar[int]

    #

    def __init_subclass__(cls, **kwargs: ta.Any) -> None:
        super().__init_subclass__(**kwargs)

        if lang.is_abstract_class(cls):
            return

        #

        bits = check.single({
            check.isinstance(bbits, int)
            for bcls in cls.__mro__
            if (bbits := bcls.__dict__.get('BITS')) is not None
        })

        #

        mode_base = _get_exclusive_base_cls(cls, _MODE_BASE_CLASSES)

        if mode_base is CheckedInt:
            cls.MODE = cls.Mode.CHECK

        elif mode_base is ClampedInt:
            cls.MODE = cls.Mode.CLAMP

        elif mode_base is WrappedInt:
            cls.MODE = cls.Mode.WRAP

        else:
            raise TypeError(cls)

        #

        sign_base = _get_exclusive_base_cls(cls, _SIGN_BASE_CLASSES)

        if sign_base is SignedInt:
            cls.SIGNED = True
            cls.MIN = -(1 << (bits - 1))
            cls.MAX = (1 << (bits - 1)) - 1

        elif sign_base is UnsignedInt:
            cls.SIGNED = False
            cls.MIN = 0
            cls.MAX = (1 << bits) - 1

        else:
            raise TypeError(cls)

        #

        cls.MASK = (1 << bits) - 1

    #

    @classmethod
    def clamp(cls, value: int) -> int:
        return max(min(value, cls.MAX), cls.MIN)

    @classmethod
    def check(cls, value: int) -> int:
        if value > cls.MAX:
            raise OverflowFixedWidthIntError(value)
        elif value < cls.MIN:
            raise UnderflowFixedWidthIntError(value)
        return value

    @classmethod
    def wrap(cls, value: int) -> int:
        return ((value - cls.MIN) & cls.MASK) + cls.MIN

    #

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

    #

    def __invert__(self) -> ta.Self:
        if not self.SIGNED:
            return self.__class__(~int(self) & self.MASK)
        else:
            return self.__class__(super().__invert__())

    #

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({int(self)})'


##


class SignedInt(FixedWidthInt, lang.Abstract):
    pass


class UnsignedInt(FixedWidthInt, lang.Abstract):
    pass


_SIGN_BASE_CLASSES: tuple[type[FixedWidthInt], ...] = (
    SignedInt,
    UnsignedInt,
)


#


class CheckedInt(FixedWidthInt, lang.Abstract):
    def __new__(cls: type[FixedWidthIntT], value: int) -> FixedWidthIntT:
        return super().__new__(cls, cls.check(value))  # type: ignore[misc]


class ClampedInt(FixedWidthInt, lang.Abstract):
    def __new__(cls: type[FixedWidthIntT], value: int) -> FixedWidthIntT:
        return super().__new__(cls, cls.clamp(value))  # type: ignore[misc]


class WrappedInt(FixedWidthInt, lang.Abstract):
    def __new__(cls: type[FixedWidthIntT], value: int) -> FixedWidthIntT:
        return super().__new__(cls, cls.wrap(value))  # type: ignore[misc]


_MODE_BASE_CLASSES: tuple[type[FixedWidthInt], ...] = (
    CheckedInt,
    ClampedInt,
    WrappedInt,
)


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


class CheckedUint8(CheckedInt, UnsignedInt, AnyInt8):
    pass


class CheckedUint16(CheckedInt, UnsignedInt, AnyInt16):
    pass


class CheckedUint32(CheckedInt, UnsignedInt, AnyInt32):
    pass


class CheckedUint64(CheckedInt, UnsignedInt, AnyInt64):
    pass


class CheckedUint128(CheckedInt, UnsignedInt, AnyInt128):
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


class ClampedUint8(ClampedInt, UnsignedInt, AnyInt8):
    pass


class ClampedUint16(ClampedInt, UnsignedInt, AnyInt16):
    pass


class ClampedUint32(ClampedInt, UnsignedInt, AnyInt32):
    pass


class ClampedUint64(ClampedInt, UnsignedInt, AnyInt64):
    pass


class ClampedUint128(ClampedInt, UnsignedInt, AnyInt128):
    pass


#


class WrappedInt8(WrappedInt, SignedInt, AnyInt8):
    pass


class WrappedInt16(WrappedInt, SignedInt, AnyInt16):
    pass


class WrappedInt32(WrappedInt, SignedInt, AnyInt32):
    pass


class WrappedInt64(WrappedInt, SignedInt, AnyInt64):
    pass


class WrappedInt128(WrappedInt, SignedInt, AnyInt128):
    pass


#


class WrappedUint8(WrappedInt, UnsignedInt, AnyInt8):
    pass


class WrappedUint16(WrappedInt, UnsignedInt, AnyInt16):
    pass


class WrappedUint32(WrappedInt, UnsignedInt, AnyInt32):
    pass


class WrappedUint64(WrappedInt, UnsignedInt, AnyInt64):
    pass


class WrappedUint128(WrappedInt, UnsignedInt, AnyInt128):
    pass

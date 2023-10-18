from __future__ import annotations

import typing as ta

import numpy as np


class DType(ta.NamedTuple):
    priority: int  # this determines when things get upcasted
    itemsize: int
    name: str
    np: ta.Optional[
        type
    ]  # TODO: someday this will be removed with the "remove numpy" project
    sz: int = 1

    def __repr__(self):
        return f"dtypes.{INVERSE_DTYPES_DICT[self]}"


# dependent typing?
class ImageDType(DType):
    def __new__(cls, priority, itemsize, name, np, shape):
        return super().__new__(cls, priority, itemsize, name, np)

    def __init__(self, priority, itemsize, name, np, shape) -> None:
        self.shape: tuple[int, ...] = shape  # arbitrary arg for the dtype, used in image for the shape
        super().__init__()

    def __repr__(self):
        return f"dtypes.{self.name}({self.shape})"

    # TODO: fix this to not need these
    def __hash__(self):
        return hash((super().__hash__(), self.shape))

    def __eq__(self, x):
        return super().__eq__(x) and self.shape == x.shape

    def __ne__(self, x):
        return super().__ne__(x) or self.shape != x.shape


class PtrDType(DType):
    def __new__(cls, dt: DType):
        return super().__new__(cls, dt.priority, dt.itemsize, dt.name, dt.np, dt.sz)

    def __repr__(self):
        return f"ptr.{super().__repr__()}"


class dtypes:
    @staticmethod  # static methds on top, or bool in the type info will refer to dtypes.bool
    def is_int(x: DType) -> bool:
        return x in (
            dtypes.int8,
            dtypes.int16,
            dtypes.int32,
            dtypes.int64,
            dtypes.uint8,
            dtypes.uint16,
            dtypes.uint32,
            dtypes.uint64,
        )

    @staticmethod
    def is_float(x: DType) -> bool:
        return x in (
            dtypes.float16,
            dtypes.float32,
            dtypes.float64,
            dtypes._half4,
            dtypes._float2,
            dtypes._float4,
        )

    @staticmethod
    def is_unsigned(x: DType) -> bool:
        return x in (dtypes.uint8, dtypes.uint16, dtypes.uint32, dtypes.uint64)

    @staticmethod
    def from_np(x) -> DType:
        return DTYPES_DICT[np.dtype(x).name]

    @staticmethod
    def fields() -> dict[str, DType]:
        return DTYPES_DICT

    bool: ta.Final[DType] = DType(0, 1, "bool", np.bool_)
    float16: ta.Final[DType] = DType(0, 2, "half", np.float16)
    half = float16
    float32: ta.Final[DType] = DType(4, 4, "float", np.float32)
    float = float32
    float64: ta.Final[DType] = DType(0, 8, "double", np.float64)
    double = float64
    int8: ta.Final[DType] = DType(0, 1, "char", np.int8)
    int16: ta.Final[DType] = DType(1, 2, "short", np.int16)
    int32: ta.Final[DType] = DType(2, 4, "int", np.int32)
    int64: ta.Final[DType] = DType(3, 8, "long", np.int64)
    uint8: ta.Final[DType] = DType(0, 1, "unsigned char", np.uint8)
    uint16: ta.Final[DType] = DType(1, 2, "unsigned short", np.uint16)
    uint32: ta.Final[DType] = DType(2, 4, "unsigned int", np.uint32)
    uint64: ta.Final[DType] = DType(3, 8, "unsigned long", np.uint64)

    # NOTE: bfloat16 isn't supported in numpy
    bfloat16: ta.Final[DType] = DType(0, 2, "__bf16", None)

    # NOTE: these are internal dtypes, should probably check for that
    _int2: ta.Final[DType] = DType(2, 4 * 2, "int2", None, 2)
    _half4: ta.Final[DType] = DType(0, 2 * 4, "half4", None, 4)
    _float2: ta.Final[DType] = DType(4, 4 * 2, "float2", None, 2)
    _float4: ta.Final[DType] = DType(4, 4 * 4, "float4", None, 4)
    _arg_int32: ta.Final[DType] = DType(2, 4, "_arg_int32", None)

    # NOTE: these are image dtypes
    @staticmethod
    def imageh(shp):
        return ImageDType(100, 2, "imageh", np.float16, shp)

    @staticmethod
    def imagef(shp):
        return ImageDType(100, 4, "imagef", np.float32, shp)


# HACK: staticmethods are not callable in 3.8 so we have to compare the class
DTYPES_DICT = {
    k: v
    for k, v in dtypes.__dict__.items()
    if not k.startswith("__") and not callable(v) and not v.__class__ == staticmethod
}

INVERSE_DTYPES_DICT = {v: k for k,v in DTYPES_DICT.items()}

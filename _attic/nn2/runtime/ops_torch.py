import typing as ta

import numpy as np
import torch

from .. import ops
from ..dtypes import DType
from ..dtypes import dtypes
from ..execution import Interpreted
from ..helpers import getenv
from ..helpers import prod
from ..runtime.lib import RawBuffer
from ..runtime.ops_cpu import einsum_mulacc
from ..runtime.ops_cpu import shape_to_axis


device = torch.device(
    "cuda:0" if torch.cuda.is_available() else ("mps" if getenv("MPS", 0) else "cpu")
)

type_map = {
    torch.float64: dtypes.float64,
    torch.float16: dtypes.float16,
    torch.float32: dtypes.float32,
    torch.int8: dtypes.int8,
    torch.int16: dtypes.int16,
    torch.int32: dtypes.int32,
    torch.int64: dtypes.int64,
    torch.uint8: dtypes.uint8,
    torch.bool: dtypes.bool,
}

inverse_type_map = {v: k for k, v in type_map.items()}


class RawTorchBuffer(RawBuffer):
    def __init__(self, size: int, dtype: DType, buf: ta.Optional[torch.Tensor] = None) -> None:
        super().__init__(size, dtype, buf)

    @classmethod
    def fromCpu(cls, x):
        buf = torch.from_numpy(x if all(s >= 0 for s in x.strides) else x.copy()).requires_grad_(False).to(device)
        return cls(prod(x.shape), type_map[buf.dtype], buf)

    def _get_buf(self):
        if self._buf is not None:
            return self._buf
        else:
            return torch.empty([self.size], device=device, dtype=inverse_type_map[self.dtype])

    def toCpu(self):
        return self._get_buf().cpu().numpy()


def output_type(x, y):
    return x.dtype if type_map[x.dtype].priority > type_map[y.dtype].priority else y.dtype


def match_types(x, y, disallow_bool=False):
    up = output_type(x, y)
    if disallow_bool and up == torch.bool:
        up = torch.float
    return x.type(up), y.type(up)


def as_strided(x, arg):
    if any(i < 0 for i in arg[1]):
        return torch.as_strided(
            x.contiguous(),
            arg[0],
            tuple(abs(i) for i in arg[1]),
            arg[2] + sum((s - 1) * a if a < 0 else 0 for (s, a) in zip(arg[0], arg[1])),
        ).flip([i for i, a in enumerate(arg[1]) if a < 0])
    return torch.as_strided(x.contiguous(), arg[0], arg[1], arg[2])


torch_fxn_for_op: dict[type[ops.LazyOp], ta.Callable] = {
    # TODO: torch.tensor should work here. it doesn't due to "overflow" in uint8
    # BufferOps.CONST: lambda val, dtype: torch.tensor(val, dtype=inverse_type_map[dtype]),
    ops.Const: lambda val, dtype: torch.from_numpy(np.array(val, dtype=dtype.np)).requires_grad_(False).to(device),
    ops.Mem: lambda x: x._get_buf(),
    ops.FromUnderlying: lambda x: RawTorchBuffer(prod(x.shape), type_map[x.dtype], x),
    ops.Nop: lambda x: x.contiguous(),
    ops.Sqrt: lambda x: x.sqrt(),
    ops.Exp2: lambda x: x.exp2(),
    ops.Log2: lambda x: x.log2(),
    ops.Sin: torch.sin,
    ops.Cast: lambda x, y: (x.view if y[1] else x.type)(next(k for k, v in type_map.items() if v == y[0])),
    ops.Neg: lambda x: torch.logical_not(x) if x.dtype is torch.bool else torch.neg(x),
    ops.Max2: torch.maximum,
    ops.CmpLt: lambda x, y: (x < y).type(torch.promote_types(x.dtype, y.dtype)),
    ops.Add: lambda x, y: torch.add(*match_types(x, y)).type(output_type(x, y)),
    ops.Sub: lambda x, y: torch.sub(*match_types(x, y, disallow_bool=True)).type(output_type(x, y)),
    ops.Mul: lambda x, y: torch.mul(*match_types(x, y)).type(output_type(x, y)),
    ops.Div: lambda x, y: torch.div(*match_types(x, y)).type(torch.promote_types(x.dtype, y.dtype)),
    ops.Sum: lambda x, new_shape: x.sum(shape_to_axis(x.shape, new_shape), dtype=x.dtype, keepdims=True) if x.shape != new_shape else x,
    ops.Max: lambda x, new_shape: x.amax(shape_to_axis(x.shape, new_shape), keepdims=True) if x.shape != new_shape else x,
    ops.AsStrided: as_strided,
    ops.Expand: lambda x, arg: x.expand(arg),
    ops.Pad: lambda x, padding: torch.nn.functional.pad(x, [item for sublist in padding[::-1] for item in sublist]),  # noqa
    ops.MulAcc: einsum_mulacc(
        lambda s, a, b: torch.einsum(s, a.float(), b.float()).type(output_type(a, b)),
        lambda x: x.stride(),
        lambda x, s: x.expand(s),
    ),
    ops.Where: lambda x, y, z: torch.where(x != 0, y, z),
}


TorchBuffer = Interpreted(
    RawTorchBuffer,
    torch_fxn_for_op,
)

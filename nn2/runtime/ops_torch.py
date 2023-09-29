import typing as ta

import torch

from .. import ops
from ..dtypes import DType
from ..dtypes import dtypes
from ..execution import Interpreted
from ..helpers import getenv
from ..helpers import prod
from ..runtime.lib import RawBuffer
from ..runtime.ops_cpu import base_fxn_for_op
from ..runtime.ops_cpu import einsum_mulacc


device = torch.device(
    "cuda:0" if torch.cuda.is_available() else ("mps" if getenv("MPS", 0) else "cpu")
)
type_map = {
    torch.float64: dtypes.float64,
    torch.float16: dtypes.float16,
    torch.float32: dtypes.float32,
    torch.int8: dtypes.int8,
    torch.int32: dtypes.int32,
    torch.int64: dtypes.int64,
    torch.uint8: dtypes.uint8,
    torch.bool: dtypes.bool,
}
inverse_type_map = {v: k for k, v in type_map.items()}


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
    **base_fxn_for_op,
    **{
        ops.Nop: lambda x: x.contiguous(),
        ops.Sqrt: lambda x: x.sqrt(),
        ops.Exp2: lambda x: x.exp2(),
        ops.Log2: lambda x: x.log2(),
        ops.Sin: torch.sin,
        ops.Cast: lambda x, y: (x.view if y[1] else x.type)(next(k for k, v in type_map.items() if v == y[0])),
        ops.Max2: torch.maximum,
        ops.CmpLt: lambda x, y: (x < y).type(torch.promote_types(x.dtype, y.dtype)),
        ops.Pad: lambda x, padding: torch.nn.functional.pad(x, [item for sublist in padding[::-1] for item in sublist]),  # noqa
        ops.MulAcc: einsum_mulacc(
            lambda s, a, b: torch.einsum(s, a.float(), b.float()).type(torch.promote_types(a.dtype, b.dtype)),
            lambda x: x.stride(),
            lambda x, s: x.expand(s),
        ),
        ops.Where: lambda x, y, z: torch.where(x != 0, y, z),
        ops.Restride: lambda x, arg: x[tuple(slice(None, None, abs(i)) for i in arg)].flip([i for i, a in enumerate(arg) if a < 0]),  # noqa
        ops.Expand: lambda x, arg: x.expand(arg),
        ops.Permute: lambda x, arg: x.permute(arg),
        ops.AsStrided: as_strided,
    },
}


class RawTorchBuffer(RawBuffer):
    def __init__(self, size: int, dtype: DType, buf: ta.Optional[torch.Tensor] = None) -> None:
        super().__init__(
            size,
            dtype,
            buf
            if buf is not None else torch.empty([size], dtype=inverse_type_map[dtype]),
        )

    @classmethod
    def fromCpu(cls, x):
        buf = torch.from_numpy(x).requires_grad_(False).to(device)
        return cls(prod(x.shape), type_map[buf.dtype], buf)

    def toCpu(self):
        return self._buf.cpu().numpy()


TorchBuffer = Interpreted(
    RawTorchBuffer,
    torch_fxn_for_op,
    from_underlying=lambda x: RawTorchBuffer(prod(x.shape), type_map[x.dtype], x),
)

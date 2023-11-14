from __future__ import annotations

import functools
import itertools
import typing as ta
import weakref

from .devices import Device
from .dtypes import DType
from .execution import AstRunner
from .execution import BatchExecutor
from .execution import JitItem
from .helpers import DEBUG
from .helpers import getenv
from .helpers import merge_dicts
from .runtime.lib import RawBuffer
from .shape.shapetracker import ShapeTracker
from .shape.symbolic import Variable
from .tensor import Tensor


JIT_SUPPORTED_DEVICE = ["OPENCL", "CLANG", "METAL", "CUDA", "HIP", "WEBGPU", "LLVM"]


class TinyJit:
    def __init__(self, fxn: ta.Callable) -> None:
        super().__init__()

        self.fxn: ta.Callable = fxn
        self.jit_fxn: ta.Optional[BatchExecutor] = None
        self.cnt: int = 0
        self.ret: ta.Any = None
        self.expected_vals: ta.Optional[tuple[Variable, ...]] = None
        self.expected_sts_dtype: ta.Optional[tuple[tuple[ShapeTracker, DType], ...]] = None

    @property
    def jit_cache(self) -> list[JitItem]:
        return self.jit_fxn.jit_cache if self.jit_fxn else []

    @property
    def input_replace(self) -> dict[tuple[int, int], ta.Union[int, str]]:
        return self.jit_fxn.input_replace if self.jit_fxn else {}

    # add support for instance methods
    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs) -> ta.Any:
        if Device.DEFAULT.split(":")[0] not in JIT_SUPPORTED_DEVICE:
            return self.fxn(*args, **kwargs)  # only jit on supported device

        # all inputs are realized
        input_tensors: dict[ta.Union[int, str], Tensor] = {
            ta.cast(ta.Union[int, str], k): v.realize()
            for k, v in itertools.chain(enumerate(args), kwargs.items())
            if v.__class__ is Tensor
        }
        expected_sts_dtype = tuple([(v.lazydata.st.unbind(), v.dtype) for v in input_tensors.values()])

        # get rawbuffers
        input_rawbuffers: dict[ta.Union[int, str], RawBuffer] = {
            k: ta.cast(RawBuffer, v.lazydata.realized)
            for k, v in input_tensors.items()
        }
        assert len(input_rawbuffers) != 0, "no inputs to JIT"
        assert len(set(input_rawbuffers.values())) == len(input_rawbuffers), "duplicate inputs to JIT"

        # get variables: they can either be in Tensors or passed in as arguments, and all must be bound. these are all global
        var_vals: dict[Variable, int] = merge_dicts(
            [arg.lazydata.st.var_vals for arg in input_tensors.values()] +
            [dict(x.unbind() for x in itertools.chain(args, kwargs.values()) if isinstance(x, Variable))]
        )
        expected_vals = tuple(var_vals.keys())

        if self.cnt >= 2:
            assert self.expected_vals == expected_vals, "mismatch of var_vals"
            assert self.expected_sts_dtype == expected_sts_dtype, "mismatch of sts"
            assert self.jit_fxn, "didn't get jitted?"
            self.jit_fxn(input_rawbuffers, var_vals, DEBUG >= 2)

        elif self.cnt == 1:
            self.expected_vals, self.expected_sts_dtype = expected_vals, expected_sts_dtype

            CacheCollector.start(var_vals)
            self.ret = self.fxn(*args, **kwargs)
            jit_cache = CacheCollector.finish()
            assert len(jit_cache) != 0, "didn't JIT anything!"
            if DEBUG >= 1:
                print(f"JIT captured {len(jit_cache)} kernels with {len(input_rawbuffers)} inputs")

            alt_batch_exec = Device[Device.DEFAULT].batch_executor
            self.jit_fxn = (BatchExecutor if alt_batch_exec is None or getenv("JIT") == 2 else alt_batch_exec)(jit_cache, input_rawbuffers, var_vals)

        elif self.cnt == 0:
            self.ret = self.fxn(*args, **kwargs)

        self.cnt += 1
        return self.ret


class PlaceHolder:
    def __init__(self, buf: RawBuffer) -> None:
        super().__init__()
        self.size = buf.size
        self.dtype = buf.dtype
        self._device = getattr(buf, '_device', None)
        self.ref = weakref.ref(buf)
        self.buftype = type(buf)
        self.bufid = id(buf._buf)

    def to_tuple(self):
        return (self.size, self.dtype, self._device, self.buftype, self.bufid)

    def __hash__(self):
        return hash(self.to_tuple())

    def __eq__(self, x):
        return isinstance(x, PlaceHolder) and self.to_tuple() == x.to_tuple()

    def alloc_if_needed(self, buffer_cache: dict[PlaceHolder, RawBuffer]) -> RawBuffer:
        ret = self.ref()
        if ret:
            return ret
        if self not in buffer_cache:
            buffer_cache[self] = self.buftype(
                self.size,
                self.dtype,
                **({'device': self._device} if self._device is not None else dict()),
            )
        return buffer_cache[self]


class _CacheCollector:
    def __init__(self) -> None:
        super().__init__()
        self.cache: ta.Optional[list[tuple[AstRunner, list[ta.Union[RawBuffer, PlaceHolder]]]]] = None

    def start(self, var_vals: ta.Optional[dict[Variable, int]] = None):
        self.cache = []
        self.placeholders: weakref.WeakKeyDictionary[RawBuffer, PlaceHolder] = weakref.WeakKeyDictionary()
        self.var_vals = var_vals if var_vals is not None else {}

    def add(self, prg, rawbufs, var_vals):
        if self.cache is None:
            return
        for k, v in var_vals.items():
            assert k in self.var_vals and self.var_vals[k] == v, f"var_vals {k} mismatch {v} != {self.var_vals.get(k)}"
        self.placeholders[rawbufs[0]] = PlaceHolder(rawbufs[0])
        self.cache.append((prg, [self.placeholders.get(x, x) if isinstance(x, RawBuffer) else x for x in rawbufs]))

    def finish(self) -> list[JitItem]:
        if self.cache is None: return []
        buffer_cache: dict[PlaceHolder, RawBuffer] = {}
        saved_cache = self.cache
        self.cache = None
        return [
            JitItem(prg, [x.alloc_if_needed(buffer_cache) if isinstance(x, PlaceHolder) else x for x in pl])
            for prg, pl in saved_cache
        ]


CacheCollector = _CacheCollector()

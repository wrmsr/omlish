from __future__ import annotations

import functools
import itertools
import operator
import typing as ta
import weakref

from omlish import dataclasses as dc

from .device import Device
from .dtypes import DType
from .execution import CompiledAstRunner
from .execution import JitRunner
from .helpers import DEBUG
from .helpers import all_int
from .helpers import getenv
from .helpers import merge_dicts
from .runtime.lib import RawBuffer
from .shape.shapetracker import ShapeTracker
from .shape.symbolic import Node
from .shape.symbolic import NumNode
from .shape.symbolic import Variable
from .tensor import Tensor


@dc.dataclass(frozen=True)
class JitItem:
    prg: JitRunner
    rawbufs: list[ta.Optional[RawBuffer]]


def get_jit_stats(jit_cache: list[JitItem]) -> tuple[Node, Node]:
    return (
        functools.reduce(operator.__add__, [ji.prg.op_estimate for ji in jit_cache], NumNode(0)),
        functools.reduce(operator.__add__, [ji.prg.mem_estimate for ji in jit_cache], NumNode(0)),
    )


def get_input_replace(
        jit_cache: list[JitItem],
        input_rawbuffers: list[RawBuffer],
) -> dict[tuple[int, int], int]:
    input_replace: dict[tuple[int, int], int] = {}
    for j, ji in enumerate(jit_cache):
        for i, a in enumerate(ji.rawbufs):
            if a in input_rawbuffers:
                input_replace[(j, i)] = input_rawbuffers.index(a)
    assert len(set(input_replace.values())) == len(input_rawbuffers), "some input tensors not found"
    return input_replace


def get_jc_idxs_with_updatable_launch_dims(jit_cache: list[JitItem]) -> list[int]:
    return [
        j
        for j, ji in enumerate(jit_cache)
        if isinstance(ji.prg, CompiledAstRunner)
        and (
            (ji.prg.global_size and not all_int(tuple(ji.prg.global_size)))
            or (ji.prg.local_size and not all_int(tuple(ji.prg.local_size)))
        )
    ]


def get_jc_idxs_with_updatable_var_vals(jit_cache: list[JitItem]) -> list[int]:
    return [
        j
        for j, ji in enumerate(jit_cache)
        if isinstance(ji.prg, CompiledAstRunner)
        and ji.prg.vars
    ]

class GraphException(Exception):
    pass


ReturnType = ta.TypeVar('ReturnType')


class TinyJit:
    def __init__(self, fxn: ta.Callable[..., ReturnType]) -> None:
        super().__init__()
        self.fxn: ta.Callable = fxn
        self.reset()

    def reset(self) -> None:
        self.jit_cache: list[JitItem] = []
        self.input_replace: dict[tuple[int, int], int] = {}
        self.cnt: int = 0
        self.ret: ta.Optional[ReturnType] = None
        self.expected_vals: ta.Optional[tuple[Variable, ...]] = None
        self.expected_sts_dtype: ta.Optional[tuple[tuple[ShapeTracker, DType], ...]] = None
        self.expected_name_sts_dtype: ta.Optional[tuple[tuple[ta.Union[int, str], ShapeTracker, DType], ...]] = None

    # add support for instance methods
    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs) -> ReturnType:
        # all inputs are realized
        input_tensors: dict[ta.Union[int, str], Tensor] = {
            ta.cast(ta.Union[int, str], k): v.realize()
            for k, v in itertools.chain(enumerate(args), kwargs.items())
            if v.__class__ is Tensor
        }
        expected_name_sts_dtype = tuple([(k, v.lazydata.st.unbind(), v.dtype) for k, v in input_tensors.items()])

        # get rawbuffers
        input_rawbuffers: list[RawBuffer] = [ta.cast(RawBuffer, v.lazydata.realized) for v in input_tensors.values()]
        assert len(set(input_rawbuffers)) == len(input_rawbuffers), "duplicate inputs to JIT"

        # get variables: they can either be in Tensors or passed in as arguments, and all must be bound. these are all global
        var_vals: dict[Variable, int] = merge_dicts(
            [arg.lazydata.st.var_vals for arg in input_tensors.values()] +
            [dict(x.unbind() for x in itertools.chain(args, kwargs.values()) if isinstance(x, Variable))]
        )
        expected_vals = tuple(var_vals.keys())

        if self.cnt >= 2:
            # jit exec
            assert self.expected_vals == expected_vals, "mismatch of var_vals"
            assert (
                    self.expected_name_sts_dtype == expected_name_sts_dtype
            ), f"mismatch of sts, expected {self.expected_name_sts_dtype} got {expected_name_sts_dtype}"
            for (j, i), input_idx in self.input_replace.items():
                self.jit_cache[j].rawbufs[i] = input_rawbuffers[input_idx]
            for ji in self.jit_cache:
                ji.prg(ta.cast(list[RawBuffer], ji.rawbufs), var_vals, wait=DEBUG >= 2, jit=True)

        elif self.cnt == 1:
            # jit capture
            self.expected_vals = expected_vals
            self.expected_name_sts_dtype = expected_name_sts_dtype

            CacheCollector.start(var_vals)
            self.ret = self.fxn(*args, **kwargs)
            self.jit_cache = CacheCollector.finish()
            assert len(self.jit_cache) != 0, "didn't JIT anything!"
            if DEBUG >= 1:
                print(f"JIT captured {len(self.jit_cache)} kernels with {len(input_rawbuffers)} inputs")

            # if your Device supports it, condense the items into a graph executor
            if (make_graph := Device[Device.DEFAULT].graph) and getenv("JIT") != 2:
                try:
                    self.jit_cache = [
                        JitItem(
                            make_graph(
                                self.jit_cache,
                                input_rawbuffers,
                                var_vals,
                            ),
                            ta.cast(list[ta.Optional[RawBuffer]], input_rawbuffers),
                        )
                    ]
                except GraphException as e:
                    if DEBUG >= 1:
                        print(f"graph create failed {e}")

            self.input_replace = get_input_replace(self.jit_cache, input_rawbuffers)

        elif self.cnt == 0:
            # jit ignore
            self.ret = self.fxn(*args, **kwargs)

        # clear jit inputs
        for (j, i) in self.input_replace.keys():
            self.jit_cache[j].rawbufs[i] = None

        self.cnt += 1
        return ta.cast(ReturnType, self.ret)


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
        self.cache: ta.Optional[list[tuple[JitRunner, list[ta.Union[RawBuffer, PlaceHolder]]]]] = None

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
        self.cache.append((
            prg,
            [
                self.placeholders.get(x, x) if isinstance(x, RawBuffer) else x
                for x in rawbufs
            ],
        ))

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

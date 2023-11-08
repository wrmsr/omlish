import collections
import functools
import itertools
import typing as ta

from .devices import Device
from .dtypes import DType
from .helpers import DEBUG
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
        self.cnt: int = 0
        self.jit_cache: list[tuple[ta.Any, list[ta.Optional[RawBuffer]], dict[Variable, int]]] = []
        self.ret: ta.Any = None

        # (kernel_number, buffer_number) -> (input_name, expected_shapetracker, expected_type)
        self.input_replace: dict[tuple[int, int], tuple[ta.Union[int, str], ShapeTracker, DType]] = {}

        # (kernel_number) -> list(argument id). These are buffers from input + variables.
        self.updatable_entries: dict[int, list[int]] = collections.defaultdict(list)

    # add support for instance methods
    def __get__(self, obj, objtype):
        return functools.partial(self.__call__, obj)

    def __call__(self, *args, **kwargs) -> ta.Any:
        if Device.DEFAULT.split(":")[0] not in JIT_SUPPORTED_DEVICE:
            return self.fxn(*args, **kwargs)  # only jit on supported device

        # NOTE: this cast is needed since although we know realize will create a ".realized" RawBuffer, the type checke
        # doesn't
        input_rawbuffers: dict[ta.Union[int, str], tuple[RawBuffer, ShapeTracker]] = {
            ta.cast(ta.Union[int, str], k): (
                ta.cast(RawBuffer, v.realize().lazydata.realized),
                v.lazydata.st,
            )
            for k, v in itertools.chain(enumerate(args), kwargs.items())
            if v.__class__ is Tensor
        }

        assert len(input_rawbuffers) != 0, "no inputs to JIT"
        assert len(set(input_rawbuffers.values())) == len(
            input_rawbuffers
        ), "duplicate inputs to JIT"

        if self.cnt >= 2:
            try:
                var_vals: dict[Variable, int] = kwargs["jit_ctx"]
            except KeyError:
                var_vals = merge_dicts(
                    [arg.lazydata.st.var_vals for arg in args if arg.__class__ is Tensor]
                )

            if len(var_vals) > 1:
                var_vals = dict(sorted(var_vals.items(), key=lambda kv: kv[0].key))

            for (j, i), (
                input_name,
                expected_st,
                expected_type,
            ) in self.input_replace.items():
                assert (
                    input_rawbuffers[input_name][0].dtype == expected_type
                ), f"type mismatch in JIT, {input_rawbuffers[input_name][0].dtype} != {expected_type}"
                # NOTE: if we pass jit_ctx instead of using reshape to update the var_vals, we cannot compare the
                # shapetracker directly
                if "jit_ctx" not in kwargs:
                    assert input_rawbuffers[input_name][1].unbind() == expected_st, f"ShapeTracker mismatch in JIT, {input_rawbuffers[input_name][1].unbind()} != {expected_st}"
                self.jit_cache[j][1][i] = input_rawbuffers[input_name][0]

            for j in self.updatable_entries.keys():
                for k in self.jit_cache[j][2].keys():
                    try:
                        self.jit_cache[j][2][k] = var_vals[k]
                    except KeyError:
                        pass

            for prg, pargs, variables in self.jit_cache:
                prg(pargs, variables, jit=True)

            for j, i in self.input_replace.keys():
                self.jit_cache[j][1][i] = None

        elif self.cnt == 1:
            CacheCollector.start()

            self.ret = self.fxn(*args, **kwargs)
            self.jit_cache = CacheCollector.finish()

            assert len(self.jit_cache) != 0, "didn't JIT anything!"
            if DEBUG >= 1:
                print(
                    f"JIT captured {len(self.jit_cache)} kernels with {len(input_rawbuffers)} inputs"
                )

            # get the inputs for replacement
            for j_, cache in enumerate(
                self.jit_cache
            ):  # type: tuple[int, tuple[ta.Callable, list[ta.Optional[RawBuffer]], dict[Variable, int]]]
                for i, a in enumerate(cache[1]):
                    if a in [v[0] for v in input_rawbuffers.values()]:
                        self.input_replace[(j_,i)] = [(k, v[1].unbind(), v[0].dtype) for k,v in input_rawbuffers.items() if v[0] == a][0]
                        self.updatable_entries[j_].append(i)

                for i in range(len(cache[2])):
                    self.updatable_entries[j_].append(len(cache[1]) + i)

            assert set([x[0] for x in self.input_replace.values()]) == set(
                input_rawbuffers.keys()
            ), "some input tensors not found"

            for j, i in self.input_replace.keys():
                self.jit_cache[j][1][i] = None

        elif self.cnt == 0:
            self.ret = self.fxn(*args, **kwargs)

        self.cnt += 1
        return self.ret


class _CacheCollector:
    def __init__(self):
        self.cache: ta.Optional[list[tuple[ta.Callable, list[ta.Any], dict[ta.Any, ta.Any]]]] = None

    def start(self):
        self.cache = []

    def add(self, prg, rawbufs, var_vals):
        if self.cache is None:
            return
        self.cache.append((prg, rawbufs, var_vals))

    def finish(self):
        if self.cache is None:
            return []
        ret = self.cache
        self.cache = None
        return ret


CacheCollector = _CacheCollector()

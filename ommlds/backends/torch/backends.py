import abc
import typing as ta

import torch

from omlish import collections as col
from omlish import dataclasses as dc
from omlish import lang


##


def _mem_b_repr(b: int | None) -> str | None:
    return f'{b:_}' if b is not None else None


@dc.dataclass(frozen=True, kw_only=True)
class MemoryStats:
    total_b: int | None = dc.xfield(default=None, repr_fn=_mem_b_repr)
    used_b: int | None = dc.xfield(default=None, repr_fn=_mem_b_repr)

    self_allocated_b: int | None = dc.xfield(default=None, repr_fn=_mem_b_repr)
    self_reserved_b: int | None = dc.xfield(default=None, repr_fn=_mem_b_repr)

    def __add__(self, other: 'MemoryStats') -> ta.Self:
        return dc.replace(self, **{
            f.name: ((l or 0) + (r or 0)) if l is not None or r is not None else None
            for f in dc.fields(MemoryStats)  # noqa
            for l, r in [[getattr(o, f.name) for o in [self, other]]]
        })


@dc.dataclass(frozen=True, kw_only=True)
class AggregateMemoryStats(MemoryStats):
    by_device: ta.Mapping[ta.Any, MemoryStats] | None = dc.xfield(repr_fn=dc.opt_repr)


##


class UnsupportedOpError(Exception):
    pass


class BackendOps(lang.Abstract):
    @property
    @abc.abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def is_available(self) -> bool:
        raise NotImplementedError

    #

    def get_device_count(self) -> int:
        raise UnsupportedOpError

    def get_memory_stats(self) -> AggregateMemoryStats:
        raise UnsupportedOpError

    #

    def empty_cache(self) -> None:
        raise UnsupportedOpError


##


class CpuOps(BackendOps):
    name = 'cpu'

    def is_available(self) -> bool:
        return torch.cpu.is_available()

    #

    @ta.override
    def get_device_count(self) -> int:
        return torch.cpu.device_count()


##


class CudaOps(BackendOps):
    name = 'cuda'

    def is_available(self) -> bool:
        return torch.cuda.is_available()

    #

    @ta.override
    def get_device_count(self) -> int:
        return torch.cuda.device_count()

    @ta.override
    def get_memory_stats(self) -> AggregateMemoryStats:
        dct: dict[ta.Any, MemoryStats] = {}
        ams = AggregateMemoryStats(by_device=dct)

        for i in range(torch.cuda.device_count()):
            free_b, total_b = torch.cuda.mem_get_info(i)

            dms = MemoryStats(
                total_b=total_b,
                used_b=total_b - free_b,

                self_allocated_b=torch.cuda.memory_allocated(i),
                self_reserved_b=torch.cuda.memory_reserved(i),
            )

            dct[i] = dms
            ams += dms

        return ams

    #

    @ta.override
    def empty_cache(self) -> None:
        torch.cuda.empty_cache()


##


class MpsOps(BackendOps):
    name = 'mps'

    def is_available(self) -> bool:
        return torch.mps.is_available()

    #

    @ta.override
    def get_device_count(self) -> int:
        return torch.mps.device_count()

    @ta.override
    def get_memory_stats(self) -> AggregateMemoryStats:
        return AggregateMemoryStats(
            self_allocated_b=torch.mps.driver_allocated_memory(),
        )

    #

    @ta.override
    def empty_cache(self) -> None:
        torch.mps.empty_cache()


##


BACKEND_OPS: ta.Sequence[BackendOps] = [
    CPU := CpuOps(),
    CUDA := CudaOps(),
    MPS := MpsOps(),
]


BACKEND_OPS_BY_NAME: ta.Mapping[str, BackendOps] = col.make_map_by(
    lambda bo: bo.name,
    BACKEND_OPS,
    strict=True,
)

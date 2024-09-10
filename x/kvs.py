"""
TODO:
 - Optional vs KeyError

NOTES:
 - Sized, Iterable, Container

https://github.com/wrmsr/tokamak/tree/3ebf3395c5bb78b80e0445199958cb81f4cf9be8/tokamak-util/src/main/java/com/wrmsr/tokamak/util/kv
"""  # noqa
import abc
import dataclasses as dc
import typing as ta


K = ta.TypeVar('K')
V = ta.TypeVar('V')


class Op(abc.ABC, ta.Generic[K, V]):
    pass


@dc.dataclass(frozen=True)
class Get(Op[K, V]):
    key: K


@dc.dataclass(frozen=True)
class Put(Op[K, V]):
    key: K
    value: V | None


class Kv(abc.ABC, ta.Generic[K, V]):
    @abc.abstractmethod
    def do(self, op: Op[K, V]) -> V | None:
        raise NotImplementedError


@dc.dataclass(frozen=True)
class MappingKv(Kv[K, V]):
    m: ta.MutableMapping[K, V]

    def do(self, op: Op[K, V]) -> V | None:
        if isinstance(op, Get):
            return self.m.get(op.key)

        elif isinstance(op, Put):
            if op.value is not None:
                self.m[op.key] = op.value
            else:
                del self.m[op.key]
            return None

        else:
            raise TypeError(op)


@dc.dataclass(frozen=True)
class MappingKvAdapter(ta.Mapping[K, V]):
    kv: Kv[K, V]

    def __getitem__(self, k: K) -> V:
        if (v := self.kv.do(Get(k))) is None:
            raise KeyError(k)
        return v

    def __len__(self) -> int:
        raise TypeError

    def __iter__(self) -> ta.Iterator[K]:
        raise TypeError

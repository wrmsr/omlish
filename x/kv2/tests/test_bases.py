import typing as ta

import pytest

from ..bases import KvToKvFunc
from ..bases import SizedQueryableKv
from ..interfaces import Kv
from ..interfaces import KvSubclassMustUseBaseTypeError
from ..interfaces import QueryableKv
from ..interfaces import SizedKv


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


def test_bases_raise():
    with pytest.raises(KvSubclassMustUseBaseTypeError) as exc_info:
        class BadSizedQueryableKv(SizedKv[int, int], QueryableKv[int, int]):
            def __getitem__(self, k: int, /) -> int:
                raise NotImplementedError

            def __len__(self) -> int:
                raise NotImplementedError

    assert 'SizedQueryableKv' in exc_info.value.args[0]


##


class DummySizedQueryableKv(SizedQueryableKv[int, int]):
    def __getitem__(self, k: int, /) -> int:
        if k == 0:
            return 1
        raise KeyError(k)

    def __len__(self) -> int:
        return 1


def _frob_kv(kv: Kv[K, V]) -> Kv[K, V]:
    return kv


frob_kv = ta.cast(KvToKvFunc, _frob_kv)


def test_bases():
    kv0 = DummySizedQueryableKv()
    assert kv0[0] == 1
    assert len(kv0) == 1

    kv1 = frob_kv(kv0)
    assert kv1[0] == 1
    assert len(kv1) == 1

    # if ta.TYPE_CHECKING:
    #     reveal_type(kv0)
    #     reveal_type(kv1)

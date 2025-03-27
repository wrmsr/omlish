from ..base import Kv
from ..mappings import MappingKv
from ..transformed import KeyTransformedKv
from ..wrappers import underlying


def test_kv():
    d = {i: i for i in range(20)}
    kv0 = MappingKv(d)
    assert kv0[1] == 1
    kv1: Kv[int, int] = KeyTransformedKv(kv0, t_to_f=lambda i: i * 2)
    assert kv1[1] == 2
    print(list(underlying(kv1)))

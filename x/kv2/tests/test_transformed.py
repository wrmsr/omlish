from ..mappings import MutableMappingKv
from ..transformed import transform_keys
from ..wrappers import underlying


def test_transformed():
    d = {i: i for i in range(20)}
    kv0 = MutableMappingKv(d)
    assert kv0[1] == 1

    kv1 = transform_keys(a_to_b=lambda i: i * 2)(kv0)
    assert kv1[1] == 2
    print(list(underlying(kv1)))

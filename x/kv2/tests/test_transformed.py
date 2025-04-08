from ..mappings import MappingFullKv
from ..shrinkwraps import shrinkwrap_factory
from ..transformed import KeyTransformedKv
from ..wrappers import underlying


def test_transformed():
    d = {i: i for i in range(20)}
    kv0 = MappingFullKv(d)
    assert kv0[1] == 1

    kv1 = shrinkwrap_factory(KeyTransformedKv)(kv0, a_to_b=lambda i: i * 2)
    assert kv1[1] == 2
    reveal_type(kv1)
    print(list(underlying(kv1)))

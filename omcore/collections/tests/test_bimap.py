from ..bimap import make_bi_map
from ..bimap import make_mutable_bi_map


def test_bimap() -> None:
    bm = make_bi_map(zip('abcd', range(4)))
    assert bm['b'] == 1
    assert bm.inverse[1] == 'b'
    assert bm.inverse.inverse is bm


def test_mutable_bimap() -> None:
    bm = make_mutable_bi_map(zip('abcd', range(4)))
    assert bm['b'] == 1
    assert bm.inverse[1] == 'b'
    assert bm.inverse.inverse is bm
    bm['z'] = 5
    assert bm['z'] == 5
    assert bm.inverse[5] == 'z'

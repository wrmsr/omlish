from ..bimap import make_bi_map


##


def test_bimap() -> None:
    bm = make_bi_map(zip('abcd', range(4)))
    assert bm['b'] == 1
    assert bm.inverse()[1] == 'b'

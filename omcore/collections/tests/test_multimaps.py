from ..multimaps import AbstractSetBiMultiMap
from ..multimaps import SequenceBiMultiMap
from ..multimaps import abs_set_bi_multi_map
from ..multimaps import seq_bi_multi_map


##


def test_tuple_bi_multi_map() -> None:
    m: SequenceBiMultiMap[str, int] = seq_bi_multi_map({
        'a': [1, 2],
        'b': [3, 4],
        'c': [5],
    })

    assert m['b'] == (3, 4)
    assert m.inverse()[2] == 'a'
    assert m.inverse().inverse()['b'] == (3, 4)


def test_frozenset_bi_multi_map() -> None:
    m: AbstractSetBiMultiMap[str, int] = abs_set_bi_multi_map({
        'a': [1, 2],
        'b': [3, 4],
        'c': [5],
    })

    assert m['b'] == frozenset([3, 4])
    assert m.inverse()[2] == 'a'
    assert m.inverse().inverse()['b'] == frozenset([3, 4])

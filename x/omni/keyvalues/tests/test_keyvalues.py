from .. import base as base_
from .. import codecs as codecs_
from .. import impls as impls_
from .. import stubs as stubs_
from ... import codecs as cod


def test_mapping_key_values():
    kv: base_.KeyValue[int, str]
    with impls_.MappingKeyValue() as kv:
        kv[4] = 'four'
        kv[5] = 'five'
        assert kv[4] == 'four'
        with kv.iter_keys() as it:
            assert set(it) == {4, 5}


def _test_sikv(sikv: base_.SortedIterableKeyValue[int, str]):
    sikv[4] = 'four'
    sikv[5] = 'five'
    sikv[6] = 'six'
    assert sikv[4] == 'four'
    with sikv.sorted_iter_keys() as it:
        assert list(it) == [4, 5, 6]
    with sikv.reverse_sorted_iter_keys() as it:
        assert list(it) == [6, 5, 4]
    with sikv.sorted_iter_keys(5) as it:
        assert list(it) == [5, 6]
    with sikv.reverse_sorted_iter_keys(5) as it:
        assert list(it) == [5, 4]
    del sikv[5]
    with sikv.sorted_iter_keys(5) as it:
        assert list(it) == [6]
    with sikv.reverse_sorted_iter_keys(5) as it:
        assert list(it) == [4]


def test_skip_dict_key_values():
    with impls_.SortedMappingKeyValue() as sikv:
        _test_sikv(sikv)


def test_codecs():
    kv = codecs_.KeyCodecKeyValue(cod.FunctionPairCodec(str, int), impls_.MappingKeyValue())
    kv[5] = 'five'
    assert kv[5] == 'five'
    assert kv._wrapped._mapping == {'5': 'five'}

    kv = codecs_.ValueCodecKeyValue(cod.FunctionPairCodec(str, int), impls_.MappingKeyValue())
    kv[5] = 6
    assert kv[5] == 6
    assert kv._wrapped._mapping == {5: '6'}

    kv = codecs_.KeyCodecBatchedIterableKeyValue(
        cod.FunctionPairCodec(str, int),
        stubs_.StubBatchedIterableKeyValue(
            impls_.MappingKeyValue()))
    kv[5] = 6
    assert kv[5] == 6
    assert list(kv.get_item_batch([5])) == [6]

    kv = codecs_.ValueCodecBatchedIterableKeyValue(
        cod.FunctionPairCodec(str, int),
        stubs_.StubBatchedIterableKeyValue(
            impls_.MappingKeyValue()))
    kv[5] = 6
    assert kv[5] == 6
    assert list(kv.get_item_batch([5])) == [6]

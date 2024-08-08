from .. import slotsdict


def test_slotsdict():
    dct = slotsdict.AdaptiveSlotsDict()()
    dct['test'] = 1
    dct['test2'] = 2
    assert dct == {'test': 1, 'test2': 2}

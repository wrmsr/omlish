from .... import codecs


def test_bz2_codec():
    assert codecs.lookup('bz2').name == 'bz2'

import bz2

from .... import codecs


def test_bz2_codec():
    co = codecs.lookup('bz2')
    assert co.name == 'bz2'
    assert bz2.decompress(co.new().encode(b'abcd')) == b'abcd'

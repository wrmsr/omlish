from .. import compress as compress_


def test_gzip():
    c = compress_.gzip()
    assert c.decode(c.encode(b'123')) == b'123'


def test_bz2():
    c = compress_.bz2()
    assert c.decode(c.encode(b'123')) == b'123'


def test_lzma():
    c = compress_.lzma()
    assert c.decode(c.encode(b'123')) == b'123'


def test_zstd():
    c = compress_.zstd()
    assert c.decode(c.encode(b'123')) == b'123'

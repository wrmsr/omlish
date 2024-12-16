import pytest

from .... import codecs
from ....testing import pytest as ptu


def _test_compression(name: str) -> None:
    co = codecs.lookup(name).new()
    o = b'abcd1234'
    c = co.encode(o)
    u = co.decode(c)
    assert o == u


@pytest.mark.parametrize('name', [
    'bz2',
    'gzip',
    'lzma',
])
def test_compression_codec(name: str) -> None:
    _test_compression(name)


@ptu.skip.if_cant_import('lz4')
def test_compression_lz4() -> None:
    _test_compression('lz4')


@ptu.skip.if_cant_import('snappy')
def test_compression_snappy() -> None:
    _test_compression('snappy')


@ptu.skip.if_cant_import('zstandard')
def test_compression_zstd() -> None:
    _test_compression('zstd')

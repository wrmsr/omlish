import io

from ....testing import pytest as ptu
from ...generators import read_into_bytes_stepped_generator
from ..lz4 import Lz4Compression


_DEC_DATA = b'foobar' * 128


@ptu.skip.if_cant_import('lz4.frame')
def test_lz4():
    c = Lz4Compression().compress(_DEC_DATA)
    d = Lz4Compression().decompress(c)
    assert d == _DEC_DATA

    ow = io.BytesIO()
    for b in read_into_bytes_stepped_generator(
            Lz4Compression().compress_incremental(),
            io.BytesIO(_DEC_DATA),
            read_size=13,
    ):
        ow.write(b)
    d = Lz4Compression().decompress(ow.getvalue())
    assert d == _DEC_DATA

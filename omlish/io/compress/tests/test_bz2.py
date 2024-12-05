import bz2
import io

from ...generators.stepped import read_into_bytes_stepped_generator
from ..bz2 import Bz2Compression


_DEC_DATA = b'foobar' * 128
_ENC_DATA = bz2.compress(_DEC_DATA)


def test_bz2_inc_compressor():
    ow = io.BytesIO()
    for b in read_into_bytes_stepped_generator(
            Bz2Compression().compress_incremental(),
            io.BytesIO(_DEC_DATA),
            read_size=13,
    ):
        ow.write(b)

    assert ow.getvalue() == _ENC_DATA


def test_bz2_inc_decompressor():
    ir = io.BytesIO(_ENC_DATA)
    ow = io.BytesIO()
    g = Bz2Compression().decompress_incremental()
    o = next(g)
    sz = 13
    while True:
        if isinstance(o, int):
            o = g.send(ir.read(o))
        elif o is None:
            o = g.send(ir.read(sz))
        elif isinstance(o, bytes):
            if not o:
                break
            ow.write(o)
            o = g.send(None)
        else:
            raise TypeError(o)
    assert ow.getvalue() == _DEC_DATA

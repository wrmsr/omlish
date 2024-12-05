import io
import lzma

from ...generators.stepped import read_into_bytes_stepped_generator
from ..lzma import LzmaCompression


_DEC_DATA = b'foobar' * 128
_ENC_DATA = lzma.compress(_DEC_DATA)


def test_lzma_inc_compressor():
    ow = io.BytesIO()
    for b in read_into_bytes_stepped_generator(
            LzmaCompression().compress_incremental(),
            io.BytesIO(_DEC_DATA),
            read_size=13,
    ):
        ow.write(b)

    assert ow.getvalue() == _ENC_DATA


def test_lzma_inc_decompressor():
    ir = io.BytesIO(_ENC_DATA)
    ow = io.BytesIO()
    g = LzmaCompression().decompress_incremental()
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

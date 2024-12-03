import bz2
import io

from ..bz2 import IncrementalBz2Compressor
from ..bz2 import IncrementalBz2Decompressor
from .helpers import feed_inc_compressor


_DEC_DATA = b'foobar' * 128
_ENC_DATA = bz2.compress(_DEC_DATA)


def test_bz2_inc_compressor():
    ow = io.BytesIO()
    for b in feed_inc_compressor(
            IncrementalBz2Compressor()(),
            io.BytesIO(_DEC_DATA),
            read_size=13,
    ):
        ow.write(b)

    assert ow.getvalue() == _ENC_DATA


def test_bz2_inc_decompressor():
    ir = io.BytesIO(_ENC_DATA)
    ow = io.BytesIO()
    igr = IncrementalBz2Decompressor()
    g = igr()
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

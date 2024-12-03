import gzip
import io

from ..gzip import IncrementalGzipCompressor
from ..gzip import IncrementalGzipDecompressor
from .helpers import feed_inc_compressor


_MTIME = 1733266027
_DEC_DATA = b'foobar' * 128
_ENC_DATA = gzip.compress(_DEC_DATA, mtime=_MTIME)


def test_compressor():
    ow = io.BytesIO()
    for b in feed_inc_compressor(IncrementalGzipCompressor(mtime=_MTIME)(), io.BytesIO(_DEC_DATA), read_size=13):
        ow.write(b)

    assert ow.getvalue() == _ENC_DATA


def test_decompressor():
    ir = io.BytesIO(_ENC_DATA)
    ow = io.BytesIO()
    igr = IncrementalGzipDecompressor()
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

import io
import gzip

from ..gzip_inc import IncrementalGzipReader
from ..gzip_inc import IncrementalGzipWriter


_DEC_DATA = b'foobar' * 128
_ENC_DATA = gzip.compress(_DEC_DATA)


def test_gzip_inc_reader():
    ir = io.BytesIO(_ENC_DATA)
    ow = io.BytesIO()
    igr = IncrementalGzipReader()
    g = igr.gen()
    o = next(g)
    while True:
        if isinstance(o, int):
            o = g.send(ir.read(o))
        elif o is None:
            o = g.send(ir.read(13))
        elif isinstance(o, bytes):
            if not o:
                break
            ow.write(o)
            o = g.send(None)
        else:
            raise TypeError(o)
    assert ow.getvalue() == _DEC_DATA


def test_gzip_inc_writer():
    igw = IncrementalGzipWriter()
    g2 = igw.gen()
    o = io
    for b in _DEC_DATA:
        pass

import io
import gzip

from ..gzip import GzipReader
from ..gzip_inc import IncrementalGzipReader


def test_gzip_inc():
    dec_data = b'foobar' * 128
    enc_data = gzip.compress(dec_data)
    print(enc_data)

    gr = GzipReader(io.BytesIO(enc_data))
    print(gr.read())

    ir = io.BytesIO(enc_data)
    igr = IncrementalGzipReader()
    g = igr.gen()
    o = next(g)
    while True:
        if isinstance(o, int):
            o = g.send(ir.read(o))
        elif o is None:
            o = g.send(ir.read(4096))
        elif isinstance(o, bytes):
            print(o)
            if not o:
                break
            o = g.send(None)
        else:
            raise TypeError(o)

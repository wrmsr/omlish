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


def test_gzip_inc_writer():
    igw = IncrementalGzipWriter()
    ir = io.BytesIO(_DEC_DATA)
    ow = io.BytesIO()
    g = igw.gen()
    i = None
    sz = 13

    while True:
        o = g.send(i)
        i = None
        if o is None:
            i = ir.read(sz)
            if len(i) != sz:
                break
        elif not o:
            raise TypeError(o)
        else:
            ow.write(o)

    o = g.send(i)
    while True:
        if o is None:
            break
        elif not o:
            raise TypeError(o)
        else:
            ow.write(o)
        try:
            o = g.send(None)
        except StopIteration:
            if i:
                raise RuntimeError

    if i:
        try:
            o = g.send(b'')
        except StopIteration:
            pass
        else:
            while True:
                if o is None:
                    break
                elif not o:
                    raise TypeError(o)
                else:
                    ow.write(o)
                try:
                    o = g.send(None)
                except StopIteration:
                    break

    assert ow.getvalue() == _ENC_DATA

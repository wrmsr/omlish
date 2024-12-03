import bz2
import io

from ..bz2 import IncrementalBz2Compressor
from ..bz2 import IncrementalBz2Decompressor


_DEC_DATA = b'foobar' * 128
_ENC_DATA = bz2.compress(_DEC_DATA)


def test_bz2_inc_compressor():
    igw = IncrementalBz2Compressor()
    ir = io.BytesIO(_DEC_DATA)
    ow = io.BytesIO()
    g = igw()
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
                raise RuntimeError  # noqa

    if i:
        try:
            o = g.send(b'')
        except StopIteration:
            pass
        else:
            while True:
                if o is None:
                    raise TypeError(o)
                elif not o:
                    break
                else:
                    ow.write(o)
                try:
                    o = g.send(None)
                except StopIteration:
                    break

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

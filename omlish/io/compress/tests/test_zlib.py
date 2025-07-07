import io
import zlib

from .... import lang
from ...coro.stepped import buffer_bytes_stepped_reader_coro
from ...coro.stepped import iterable_bytes_stepped_coro
from ...coro.stepped import read_into_bytes_stepped_coro
from ..zlib import ZlibCompression


_DEC_DATA = b'foobar' * 128
_ENC_DATA = zlib.compress(_DEC_DATA)


def test_zlib_inc_compressor():
    ow = io.BytesIO()
    for b in read_into_bytes_stepped_coro(
            ZlibCompression().compress_incremental(),
            io.BytesIO(_DEC_DATA),
            read_size=13,
    ):
        ow.write(b)

    assert zlib.decompress(ow.getvalue()) == _DEC_DATA


def test_zlib_inc_decompressor():
    ir = io.BytesIO(_ENC_DATA)
    ow = io.BytesIO()
    g = ZlibCompression().decompress_incremental()
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


def test_zlib_inc_decompressed_buffered():
    g = ZlibCompression().decompress_incremental()
    bg = buffer_bytes_stepped_reader_coro(g)
    sz = 13
    l = []
    for i in range((len(_ENC_DATA) // sz) + 1):
        o = bg.send(_ENC_DATA[i * sz:(i + 1) * sz])
        while o is not None:
            assert isinstance(o, bytes)
            l.append(o)
            o = next(bg)
    o = bg.send(b'')
    while o is not None:
        assert isinstance(o, bytes)
        l.append(o)
        try:
            o = next(bg)
        except StopIteration:
            break
    assert b''.join(l) == _DEC_DATA


def test_zlib_inc_compressed_buffered_iterable():
    g = ZlibCompression().decompress_incremental()
    ig = iterable_bytes_stepped_coro(buffer_bytes_stepped_reader_coro(g))
    sz = 13
    il = [*map(bytes, lang.chunk(sz, _ENC_DATA)), b'']
    l = []
    for i in il:
        for o in ig.send(i):
            assert isinstance(o, bytes)
            l.append(o)
    assert b''.join(l) == _DEC_DATA

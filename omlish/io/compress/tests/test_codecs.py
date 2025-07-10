import io
import typing as ta

import pytest

from .... import check
from .... import codecs
from .... import lang
from ....testing import pytest as ptu


##


def _test_compression(name: str) -> None:
    co = codecs.lookup(name).new()
    o = b'abcd1234'
    c = co.encode(o)
    u = co.decode(c)
    assert o == u


@pytest.mark.parametrize('name', [
    'bz2',
    'gzip',
    'lzma',
])
def test_compression_codec(name: str) -> None:
    _test_compression(name)


@ptu.skip.if_cant_import('lz4')
def test_compression_lz4() -> None:
    _test_compression('lz4')


@ptu.skip.if_cant_import('snappy')
def test_compression_snappy() -> None:
    _test_compression('snappy')


@ptu.skip.if_cant_import('zstandard')
def test_compression_zstd() -> None:
    _test_compression('zstd')


##


def _run_incremental_codec(g: ta.Generator[bytes | None, bytes | None], i: bytes) -> bytes:
    cg = lang.capture_coroutine(g)
    o = io.BytesIO()

    for b in i:
        r = cg.send(bytes([b]))
        assert not r.is_return

        while r.v is not None:
            o.write(r.v)
            r = cg.send(None)
            assert not r.is_return

    r = cg.send(b'')
    assert not r.is_return

    while r.v is not None:
        o.write(r.v)
        r = cg.send(None)

    # assert r.is_return  # FIXME: ??
    cg.close()

    return o.getvalue()


def _test_incremental_compression(name: str) -> None:
    co = check.not_none(codecs.lookup(name).new_incremental)()
    o = b'abcd1234'
    c = _run_incremental_codec(co.encode_incremental(), o)
    u = _run_incremental_codec(co.decode_incremental(), c)
    assert o == u


@pytest.mark.parametrize('name', [
    'bz2',
    'gzip',
    'lzma',
])
def test_incremental_compression_codec(name: str) -> None:
    _test_incremental_compression(name)

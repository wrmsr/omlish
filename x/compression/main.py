"""
TODO:
 - https://docs.python.org/3/library/zlib.html#zlib.compressobj
"""
import bz2
import contextlib
import gzip
import io
import random
import string
import typing as ta

from .gzip import GzipWriter
from .gzip import GzipReader


##


def generate_random_text(size: int) -> str:
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=size))


##


def run_decompress(z_bytes: bytes, fac: ta.Callable[[ta.Any], ta.Any]) -> bytes:
    with contextlib.closing(fac(io.BytesIO(z_bytes))) as raw:  # noqa
        with contextlib.closing(io.BufferedReader(raw)) as buffer:
            out_buf = io.BytesIO()
            while out := buffer.read(0x1000):
                out_buf.write(out)

    return out_buf.getvalue()


def run_compress(in_bytes: bytes, fac: ta.Callable[[ta.Any], ta.Any]) -> bytes:
    z_buf = io.BytesIO()
    with fac(z_buf) as gf:
        gf.write(in_bytes)
    return z_buf.getvalue()


##


def _main() -> None:
    in_bytes = generate_random_text(0x100_000).encode('utf-8')

    gz_bytes = run_compress(in_bytes, lambda f: gzip.GzipFile(fileobj=f, mode='wb'))
    assert len(gz_bytes) < len(in_bytes)

    out_bytes = run_decompress(gz_bytes, GzipReader)
    assert out_bytes == in_bytes

    gz_bytes2 = run_compress(in_bytes, GzipWriter)
    out_bytes2 = run_decompress(gz_bytes2, GzipReader)
    assert out_bytes2 == in_bytes


if __name__ == '__main__':
    _main()

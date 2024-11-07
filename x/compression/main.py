"""
TODO:
 - https://docs.python.org/3/library/zlib.html#zlib.compressobj
"""
import contextlib
import gzip
import bz2
import io
import random
import string

from .gzip import GzipWriter
from .gzip import GzipReader


def generate_random_text(size: int) -> str:
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=size))


def run_decompress(gz_bytes: bytes) -> bytes:
    fileobj = io.BytesIO(gz_bytes)

    with contextlib.closing(GzipReader(fileobj)) as raw:  # noqa
        with contextlib.closing(io.BufferedReader(raw)) as buffer:
            out_buf = io.BytesIO()
            while out := buffer.read(0x1000):
                out_buf.write(out)

    return out_buf.getvalue()


def run_compress(in_bytes: bytes) -> bytes:
    gz_buf = io.BytesIO()
    with GzipWriter(gz_buf) as gf:
        gf.write(in_bytes)
    return gz_buf.getvalue()


def run_decompress2(gz_bytes: bytes) -> bytes:
    fileobj = io.BytesIO(gz_bytes)

    with contextlib.closing(GzipReader(fileobj)) as raw:  # noqa
        with contextlib.closing(io.BufferedReader(raw)) as buffer:
            out_buf = io.BytesIO()
            while out := buffer.read(0x1000):
                out_buf.write(out)

    return out_buf.getvalue()


##


def _main() -> None:
    in_bytes = generate_random_text(0x100_000).encode('utf-8')

    gz_buf = io.BytesIO()
    with gzip.GzipFile(fileobj=gz_buf, mode='wb') as gf:
        gf.write(in_bytes)
    gz_bytes = gz_buf.getvalue()
    assert len(gz_bytes) < len(in_bytes)

    out_bytes = run_decompress(gz_bytes)
    assert out_bytes == in_bytes

    gz_bytes2 = run_compress(in_bytes)
    out_bytes2 = run_decompress(gz_bytes2)
    assert out_bytes2 == in_bytes


if __name__ == '__main__':
    _main()

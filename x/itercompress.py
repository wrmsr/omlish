"""
TODO:
 - https://docs.python.org/3/library/zlib.html#zlib.compressobj
"""
import gzip
import io
import random
import string


def generate_random_text(size: int) -> str:
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choices(chars, k=size))


def run_decompress(in_bytes: bytes, gz_bytes: bytes) -> None:
    fileobj = io.BytesIO(gz_bytes)
    raw = gzip._GzipReader(fileobj)  # noqa
    buffer = io.BufferedReader(raw)

    out_buf = io.BytesIO()
    while out := buffer.read(0x1000):
        out_buf.write(out)

    out_bytes = out_buf.getvalue()
    assert out_bytes == in_bytes


def _main() -> None:
    in_bytes = generate_random_text(0x100_000).encode('utf-8')

    gz_buf = io.BytesIO()
    with gzip.GzipFile(fileobj=gz_buf, mode='wb') as gf:
        gf.write(in_bytes)
    gz_bytes = gz_buf.getvalue()
    assert len(gz_bytes) < len(in_bytes)

    run_decompress(in_bytes, gz_bytes)


if __name__ == '__main__':
    _main()

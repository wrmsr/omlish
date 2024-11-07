import contextlib
import gzip
import io

from ...testing import pytest as ptu
from ...text.random import generate_random_text
from ..trampoline import IoTrampoline
from ..trampoline import ThreadIoTrampoline
from ..trampoline import ThreadletIoTrampoline


def _test_trampoline(iot_cls: type[IoTrampoline]) -> None:
    in_bytes = generate_random_text(0x100_000).encode('utf-8')

    gz_buf = io.BytesIO()
    with gzip.GzipFile(fileobj=gz_buf, mode='wb') as gf:
        gf.write(in_bytes)
    gz_bytes = gz_buf.getvalue()
    assert len(gz_bytes) < len(in_bytes)

    @contextlib.contextmanager
    def target(bf):
        with gzip.GzipFile(fileobj=bf, mode='rb') as gf:
            yield lambda: gf.read(0x1000)

    out_buf = io.BytesIO()
    in_file = io.BytesIO(gz_bytes)
    with iot_cls(target) as iot:
        while raw := in_file.read(0x1000):
            for out in iot.feed(raw):
                out_buf.write(out)
        for out in iot.feed(b''):
            out_buf.write(out)

    out_bytes = out_buf.getvalue()
    assert out_bytes == in_bytes


def test_thread_trampoline() -> None:
    _test_trampoline(ThreadIoTrampoline)


@ptu.skip.if_cant_import('greenlet')
def test_greenlet_trampoline() -> None:
    _test_trampoline(ThreadletIoTrampoline)

import contextlib
import gzip
import io  # noqa
import json
import os.path

from ...testing import pytest as ptu
from ..trampoline import GreenletIoTrampoline
from ..trampoline import IoTrampoline
from ..trampoline import ThreadIoTrampoline


def _test_trampoline(iot_cls: type[IoTrampoline]) -> None:
    @contextlib.contextmanager
    def target(bf):
        with gzip.GzipFile(fileobj=bf, mode='rb') as gf:
            yield lambda: gf.read(0x1000)

    buf = io.BytesIO()
    in_file = os.path.expanduser('~/Downloads/access.json.gz')
    with open(in_file, 'rb') as f:
        with iot_cls(target) as iot:
            while raw := f.read(0x1000):
                for out in iot.feed(raw):
                    buf.write(out)
            for out in iot.feed(b''):
                buf.write(out)

    for l in buf.getvalue().decode('utf-8').splitlines():
        json.loads(l)


def test_thread_trampoline() -> None:
    _test_trampoline(ThreadIoTrampoline)


@ptu.skip.if_cant_import('greenlet')
def test_greenlet_trampoline() -> None:
    _test_trampoline(GreenletIoTrampoline)

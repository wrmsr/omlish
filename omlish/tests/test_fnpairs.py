import pytest

from .. import fnpairs as fps
from ..testing import pytest as ptu


def test_simple():
    fp = fps.of(lambda s: s.encode('utf-8'), lambda b: b.decode('utf-8'))
    assert fp.forward('hi') == b'hi'
    assert fp.backward(b'hi') == 'hi'


def test_text():
    fp = fps.text('utf-8')
    assert fp.forward('hi') == b'hi'
    assert fp.backward(b'hi') == 'hi'


def test_compose():
    fp = fps.text('utf-8').compose(fps.Gzip())
    buf = fp.forward('hi')
    assert isinstance(buf, bytes)
    assert fp.backward(buf) == 'hi'

    jzfp = fps.Json() \
        .compose(fps.UTF8) \
        .compose(fps.Gzip())
    obj = {'hi': ['there', 420]}
    buf = jzfp.forward(obj)
    assert isinstance(buf, bytes)
    assert jzfp.backward(buf) == obj

    jlzfp = fps.JsonLines() \
        .compose(fps.UTF8) \
        .compose(fps.Gzip())
    obj2 = [{'hi': ['there', 420]}, {'bye': {'yes': None}}]
    buf = jlzfp.forward(obj2)
    assert isinstance(buf, bytes)
    assert jlzfp.backward(buf) == obj2


def _test_compression(cls: type[fps.Compression]) -> None:
    fp = cls()
    o = b'abcd1234'
    c = fp.forward(o)
    u = fp.backward(c)
    assert o == u


@pytest.mark.parametrize('cls', [
    fps.Bz2,
    fps.Gzip,
    fps.Lzma,
    fps.Lz4,
])
def test_compression(cls: type[fps.Compression]) -> None:
    _test_compression(cls)


@ptu.skip_if_cant_import('snappy')
def test_compression_snappy() -> None:
    _test_compression(fps.Snappy)


@ptu.skip_if_cant_import('zstd')
def test_compression_zstd() -> None:
    _test_compression(fps.Zstd)


@pytest.mark.parametrize('cls', [
    fps.Pickle,
    fps.Json,
    fps.Cloudpickle,
    fps.Yaml,
    fps.YamlUnsafe,
])
def test_object(cls: type[fps.Object_]) -> None:
    fp = cls()
    o = {'hi': {'i am': [123, 4.56, False, None, {'a': 'test'}]}}
    e = fp.forward(o)
    d = fp.backward(e)
    assert o == d


def test_compose_types():
    fp0 = fps.of[float, int](int, float)
    fp1 = fps.of[int, str](str, int)
    fp2 = fps.of[str, list[str]](list, ''.join)

    cfp = fps.compose(fp0, fp1, fp2)
    assert cfp(13.1) == ['1', '3']
    assert cfp.backward(['2', '4']) == 24.

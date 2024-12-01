import pytest

from ...testing import pytest as ptu
from .. import pairs as fpa


def test_simple():
    fp = fpa.of(lambda s: s.encode('utf-8'), lambda b: b.decode('utf-8'))
    assert fp.forward('hi') == b'hi'
    assert fp.backward(b'hi') == 'hi'


def test_text():
    fp = fpa.text('utf-8')
    assert fp.forward('hi') == b'hi'
    assert fp.backward(b'hi') == 'hi'


def test_compose():
    fp = fpa.text('utf-8').compose(fpa.Gzip())
    buf = fp.forward('hi')
    assert isinstance(buf, bytes)
    assert fp.backward(buf) == 'hi'

    jzfp = fpa.Json() \
        .compose(fpa.UTF8) \
        .compose(fpa.Gzip())
    obj = {'hi': ['there', 420]}
    buf = jzfp.forward(obj)
    assert isinstance(buf, bytes)
    assert jzfp.backward(buf) == obj

    jlzfp = fpa.JsonLines() \
        .compose(fpa.UTF8) \
        .compose(fpa.Gzip())
    obj2 = [{'hi': ['there', 420]}, {'bye': {'yes': None}}]
    buf = jlzfp.forward(obj2)
    assert isinstance(buf, bytes)
    assert jlzfp.backward(buf) == obj2


def _test_compression(cls: type[fpa.Compression]) -> None:
    fp = cls()
    o = b'abcd1234'
    c = fp.forward(o)
    u = fp.backward(c)
    assert o == u


@pytest.mark.parametrize('cls', [
    fpa.Bz2,
    fpa.Gzip,
    fpa.Lzma,
    fpa.Lz4,
])
def test_compression(cls: type[fpa.Compression]) -> None:
    _test_compression(cls)


@ptu.skip.if_cant_import('snappy')
def test_compression_snappy() -> None:
    _test_compression(fpa.Snappy)


@ptu.skip.if_cant_import('zstandard')
def test_compression_zstd() -> None:
    _test_compression(fpa.Zstd)


@pytest.mark.parametrize('cls', [
    fpa.Pickle,
    fpa.Json,
    fpa.JsonPretty,
    fpa.JsonCompact,
    fpa.Cbor,
    fpa.Cloudpickle,
    fpa.Yaml,
    fpa.YamlUnsafe,
])
def test_object(cls: type[fpa.Object_]) -> None:
    fp = cls()
    o = {'hi': {'i am': [123, 4.56, False, None, {'a': 'test'}]}}
    e = fp.forward(o)
    d = fp.backward(e)
    assert o == d


def test_compose_types():
    fp0 = fpa.of[float, int](int, float)
    fp1 = fpa.of[int, str](str, int)
    fp2 = fpa.of[str, list[str]](list, ''.join)

    cfp = fpa.compose(fp0, fp1, fp2)
    assert cfp(13.1) == ['1', '3']
    assert cfp.backward(['2', '4']) == 24.

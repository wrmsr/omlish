import pytest

from ... import codecs
from ...testing import pytest as ptu


def _test_object(name: str) -> None:
    co = codecs.lookup(name).new()
    o = {'hi': {'i am': [123, 4.56, False, None, {'a': 'test'}]}}
    e = co.encode(o)
    d = co.decode(e)
    assert o == d


@pytest.mark.parametrize('name', [
    'pickle',
    'json',
    'json-pretty',
    'json-compact',
    'json5',
])
def test_object(name: str) -> None:
    _test_object(name)


@ptu.skip.if_cant_import('cbor')
def test_object_cbor() -> None:
    _test_object('cbor')


@ptu.skip.if_cant_import('cloudpickle')
def test_object_cloudpickle() -> None:
    _test_object('cloudpickle')


@ptu.skip.if_cant_import('yaml')
@pytest.mark.parametrize('name', [
    'yaml',
    'yaml-unsafe',
])
def test_object_yaml(name: str) -> None:
    _test_object(name)

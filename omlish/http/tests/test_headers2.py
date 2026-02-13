import pytest

from ..headers2 import DuplicateHttpHeaderError
from ..headers2 import HttpHeaders


def test_http_headers_init_with_mapping():
    src = {'Content-Type': 'text/html', 'Content-Length': '1234'}
    headers = HttpHeaders(src)
    assert headers.single['content-type'] == 'text/html'
    assert headers.single['content-length'] == '1234'


def test_http_headers_init_with_sequence():
    src = [('Content-Type', 'text/html'), ('Content-Length', '1234')]
    headers = HttpHeaders(src)
    assert headers.single['content-type'] == 'text/html'
    assert headers.single['content-length'] == '1234'


def test_http_headers_init_with_http_headers_instance():
    src = HttpHeaders([('Content-Type', 'text/html'), ('Content-Length', '1234')])
    headers = HttpHeaders(src)
    assert headers is src


def test_http_headers_as_key():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert headers._as_key('Content-Type') == 'content-type'  # noqa
    assert headers._as_key(b'Content-Type') == 'content-type'  # noqa


def test_http_headers_normalized():
    src = {'Content-Type': 'text/html', 'Accept': 'application/json'}
    headers = HttpHeaders(src)
    assert list(headers.all) == [
        ('content-type', 'text/html'),
        ('accept', 'application/json'),
    ]


def test_http_headers_duplicate_normalized():
    src = [
        ('Content-Type', 'text/html'),
        ('CONTENT-TYPE', 'Foo'),
        ('Accept', 'application/json'),
    ]
    headers = HttpHeaders(src)
    assert list(headers.all) == [
        ('content-type', 'text/html'),
        ('content-type', 'Foo'),
        ('accept', 'application/json'),
    ]
    assert list(headers['Content-Type']) == ['text/html', 'Foo']
    assert list(headers['content-type']) == ['text/html', 'Foo']


def test_http_headers_multi_dct():
    src = {'Content-Type': ['text/html', 'application/json']}
    headers = HttpHeaders(src)
    assert list(headers['content-type']) == ['text/html', 'application/json']


def test_http_headers_single_dct():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert headers.single['content-type'] == 'text/html'


def test_http_headers_strict_dct():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert headers.single['content-type'] == 'text/html'


def test_http_headers_bool():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert bool(headers)
    headers = HttpHeaders({})
    assert not bool(headers)


def test_http_headers_len():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert len(headers) == 1


def test_http_headers_iter_and_items():
    src = [('Content-Type', 'text/html'), ('valid', 'yes'), ('content-type', 'bad')]
    headers = HttpHeaders(src)
    assert list(iter(headers)) == ['content-type', 'valid']
    (k1, v1), (k2, v2) = list(headers.items())
    assert (k1, list(v1)) == ('content-type', ['text/html', 'bad'])
    assert (k2, list(v2)) == ('valid', ['yes'])


def test_http_headers_getitem():
    src = {'Content-Type': ['text/html', 'application/json']}
    headers = HttpHeaders(src)
    assert list(headers['content-type']) == ['text/html', 'application/json']


def test_http_headers_keys():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert list(headers.keys()) == ['content-type']


def test_http_headers_invalid_init():
    with pytest.raises(TypeError):
        HttpHeaders(1234)  # type: ignore

    with pytest.raises(TypeError):
        HttpHeaders([('Content-Type', 1234)])  # type: ignore


def test_http_headers_duplicate_key_error():
    src = {'Content-Type': ['text/html', 'application/json'], 'foo': 'bar'}
    headers = HttpHeaders(src)
    assert headers.single['foo'] == 'bar'
    with pytest.raises(DuplicateHttpHeaderError):
        headers.single['content-type']  # noqa

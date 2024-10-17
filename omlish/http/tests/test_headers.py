import pytest

from ...collections import DuplicateKeyError
from ..headers import HttpHeaders


def test_http_headers_init_with_mapping():
    src = {'Content-Type': 'text/html', 'Content-Length': '1234'}
    headers = HttpHeaders(src)
    assert headers.single_str_dct['content-type'] == 'text/html'
    assert headers.single_str_dct['content-length'] == '1234'


def test_http_headers_init_with_sequence():
    src = [('Content-Type', 'text/html'), ('Content-Length', '1234')]
    headers = HttpHeaders(src)
    assert headers.single_str_dct['content-type'] == 'text/html'
    assert headers.single_str_dct['content-length'] == '1234'


def test_http_headers_init_with_http_headers_instance():
    src = HttpHeaders([('Content-Type', 'text/html'), ('Content-Length', '1234')])
    headers = HttpHeaders(src)
    assert headers is src


def test_http_headers_as_bytes():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert headers._as_bytes('Content-Type') == b'Content-Type'  # noqa
    assert headers._as_bytes(b'Content-Type') == b'Content-Type'  # noqa


def test_http_headers_as_key():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert headers._as_key('Content-Type') == b'content-type'  # noqa
    assert headers._as_key(b'Content-Type') == b'content-type'  # noqa


def test_http_headers_normalized():
    src = {'Content-Type': 'text/html', 'Accept': 'application/json'}
    headers = HttpHeaders(src)
    normalized = headers.normalized
    assert (b'content-type', b'text/html') in normalized
    assert (b'accept', b'application/json') in normalized


def test_http_headers_duplicate_normalized():
    src = [
        ('Content-Type', 'text/html'),
        ('CONTENT-TYPE', 'Foo'),
        ('Accept', 'application/json'),
    ]
    headers = HttpHeaders(src)
    assert list(headers.normalized) == [
        (b'content-type', b'text/html'),
        (b'content-type', b'Foo'),
        (b'accept', b'application/json'),
    ]
    assert list(headers['Content-Type']) == ['text/html', 'Foo']
    assert list(headers[b'Content-Type']) == [b'text/html', b'Foo']


def test_http_headers_strs():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert ('content-type', 'text/html') in headers.strs


def test_http_headers_multi_dct():
    src = {'Content-Type': ['text/html', 'application/json']}
    headers = HttpHeaders(src)
    assert headers.multi_dct[b'content-type'] == [b'text/html', b'application/json']


def test_http_headers_single_dct():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert headers.single_dct[b'content-type'] == b'text/html'


def test_http_headers_strict_dct():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert headers.strict_dct[b'content-type'] == b'text/html'


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


def test_http_headers_iter():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert list(iter(headers)) == [(b'Content-Type', b'text/html')]


def test_http_headers_getitem():
    src = {'Content-Type': ['text/html', 'application/json']}
    headers = HttpHeaders(src)
    assert headers['content-type'] == ['text/html', 'application/json']
    assert headers[0] == (b'Content-Type', b'text/html')
    assert headers[1] == (b'Content-Type', b'application/json')


def test_http_headers_keys():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert list(headers.keys()) == [b'content-type']


def test_http_headers_items():
    src = {'Content-Type': 'text/html'}
    headers = HttpHeaders(src)
    assert list(headers.items()) == [(b'Content-Type', b'text/html')]


def test_http_headers_invalid_init():
    with pytest.raises(TypeError):
        HttpHeaders(1234)  # type: ignore

    with pytest.raises(TypeError):
        HttpHeaders([('Content-Type', 1234)])  # type: ignore


def test_http_headers_duplicate_key_error():
    src = {'Content-Type': ['text/html', 'application/json']}
    headers = HttpHeaders(src)
    with pytest.raises(DuplicateKeyError):
        headers.strict_dct  # noqa

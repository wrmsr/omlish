import itertools

import pytest

from ..parsers import Rule


@pytest.mark.parametrize('src', [chr(x) for x in itertools.chain(range(0x41, 0x5b), range(0x61, 0x7b))])
def test_alpha(src):
    node, _ = Rule('ALPHA').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', ['0', '1'])
def test_bit(src):
    node, _ = Rule('BIT').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', [chr(x) for x in range(0x01, 0x80)])
def test_char(src):
    node, _ = Rule('CHAR').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', ['\r'])
def test_cr(src):
    node, _ = Rule('CR').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', ['\r\n'])
def test_crlf(src):
    node, _ = Rule('CRLF').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', [chr(x) for x in itertools.chain(range(0x20), [0x7f])])
def test_ctl(src):
    node, _ = Rule('CTL').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', [chr(x) for x in range(0x30, 0x3a)])
def test_digit(src):
    node, _ = Rule('DIGIT').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', ['"'])
def test_dquote(src):
    node, _ = Rule('DQUOTE').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', list('0123456789abcdefABCDEF'))
def test_hexdig(src):
    node, _ = Rule('HEXDIG').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', ['\t'])
def test_htab(src):
    node, _ = Rule('HTAB').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', ['\n'])
def test_lf(src):
    node, _ = Rule('LF').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', [
    '',
    *[x*y for x, y in itertools.product([1, 2], [' ', '\t', '\r\n ', '\r\n\t'])],
])
def test_lwsp(src):
    node, _ = Rule('LWSP').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', [chr(x) for x in range(0x100)])
def test_octet(src):
    node, _ = Rule('OCTET').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', [' '])
def test_sp(src):
    node, _ = Rule('SP').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', [chr(x) for x in range(0x21, 0x7f)])
def test_vchar(src):
    node, _ = Rule('VCHAR').parse(src, 0)
    assert node and node.value == src


@pytest.mark.parametrize('src', [' ', '\t'])
def test_wsp(src):
    node, _ = Rule('WSP').parse(src, 0)
    assert node and node.value == src

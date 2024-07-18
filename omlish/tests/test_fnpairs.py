from .. import fnpairs


def test_simple():
    fp = fnpairs.of(lambda s: s.encode('utf-8'), lambda b: b.decode('utf-8'))
    assert fp.forward('hi') == b'hi'
    assert fp.backward(b'hi') == 'hi'


def test_text():
    fp = fnpairs.text('utf-8')
    assert fp.forward('hi') == b'hi'
    assert fp.backward(b'hi') == 'hi'

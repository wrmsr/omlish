from .. import fnpairs


def test_simple():
    fp = fnpairs.of(lambda s: s.encode('utf-8'), lambda b: b.decode('utf-8'))
    assert fp.forward('hi') == b'hi'
    assert fp.backward(b'hi') == 'hi'


def test_text():
    fp = fnpairs.text('utf-8')
    assert fp.forward('hi') == b'hi'
    assert fp.backward(b'hi') == 'hi'


def test_compose():
    fp = fnpairs.text('utf-8').compose(fnpairs.Gzip())
    buf = fp.forward('hi')
    assert isinstance(buf, bytes)
    assert fp.backward(buf) == 'hi'

    jzfp = fnpairs.Json() \
        .compose(fnpairs.UTF8) \
        .compose(fnpairs.Gzip())
    obj = {'hi': ['there', 420]}
    buf = jzfp.forward(obj)
    assert isinstance(buf, bytes)
    assert jzfp.backward(buf) == obj

    jlzfp = fnpairs.JsonLines() \
        .compose(fnpairs.UTF8) \
        .compose(fnpairs.Gzip())
    obj2 = [{'hi': ['there', 420]}, {'bye': {'yes': None}}]
    buf = jlzfp.forward(obj2)
    assert isinstance(buf, bytes)
    assert jlzfp.backward(buf) == obj2

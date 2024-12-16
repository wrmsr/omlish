from .. import pairs as fpa


def test_simple():
    fp = fpa.of(lambda s: s.encode('utf-8'), lambda b: b.decode('utf-8'))
    assert fp.forward('hi') == b'hi'
    assert fp.backward(b'hi') == 'hi'


def test_compose():
    fp0 = fpa.of(
        lambda v: v + 1,
        lambda v: v - 1,
    )

    fp1 = fpa.of(
        lambda v: v * 3,
        lambda v: v // 3,
    )

    fp2 = fpa.compose(fp0, fp1)

    assert fp2.forward(10) == 33
    assert fp2.backward(33) == 10


def test_compose_types():
    fp0 = fpa.of[float, int](int, float)
    fp1 = fpa.of[int, str](str, int)
    fp2 = fpa.of[str, list[str]](list, ''.join)

    cfp = fpa.compose(fp0, fp1, fp2)
    assert cfp(13.1) == ['1', '3']
    assert cfp.backward(['2', '4']) == 24.

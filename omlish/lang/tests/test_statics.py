from ..statics import static


def test_static():
    l0 = []
    l1 = []

    def foo():
        l0.append(True)
        return 420

    for _ in range(3):
        l1.append(static(lambda: foo()))

    assert l0 == [True]
    assert l1 == [420] * 3

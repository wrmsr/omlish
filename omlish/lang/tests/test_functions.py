from ..functions import Args


def test_args():
    def f(x, y, z):
        return x + y * z

    assert Args(1, 2, 3)(f) == 6

from ..functions import Args


def _main():
    def f(x, y, z):
        return x + y * z

    assert Args(1, 2, 3)(f) == 7

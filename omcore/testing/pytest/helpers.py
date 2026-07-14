import contextlib


##


@contextlib.contextmanager
def assert_raises_star(et):
    num_caught = 0
    try:
        yield
    except* et as eg:  # noqa
        num_caught += 1
    assert num_caught > 0

from .. import libc


def test_libc():
    with libc.Malloc(1024) as mem:
        assert int(mem)

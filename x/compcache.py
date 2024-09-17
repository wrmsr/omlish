"""
compute cache
 - Keyer scheme
 - per-module-ish CACHE_VERSION convention
 - are pickles stable?
 - ComputeCache class
 - Cacheable - fn is one
 - ttl
 - nice to have: np mmap
 - compress?
"""
import tempfile


##


class Cache:
    def __init__(self, base_dir: str) -> None:
        super().__init__()


##


def f(x: int, y: int) -> int:
    return x + y


def g(x: int, y: int) -> int:
    return f(x, 1) + f(y, 1)


def _main():
    assert g(1, 2) == 5

    #

    tmp_dir = tempfile.mkdtemp()
    print(f'{tmp_dir=}')

    cache = Cache(tmp_dir)


if __name__ == '__main__':
    _main()

"""
See:
 - https://github.com/python/cpython/blob/1494d9563f72e5ac14e55d8df3b5cb9391ccef6f/Parser/asdl_c.py
"""
import pickle


def _main():
    import os
    print(os.getpid())
    input()

    import glob
    import os.path
    import shutil
    from omdev.cexts import importhook
    here = os.path.join(os.path.dirname(__file__))
    if os.path.exists(bdir := os.path.join(here, 'build')):
        shutil.rmtree(bdir)
    for f in glob.glob(os.path.join(here, '*.so')):
        os.remove(f)
    importhook.install()

    from ._dc import point  # noqa
    p = point(1, 2)
    print(p)
    print(p.x)
    p2 = pickle.loads(pickle.dumps(p))
    assert isinstance(p2, point)
    assert (p2.x, p2.y) == (p.x, p.y)


if __name__ == '__main__':
    _main()

import glob
import os.path
import shutil

from .exts import importhook


def barf(x: object) -> str:
    """hi i do barf"""
    return f'barf str! {x!r}'


def return_barf(ty):
    return barf


def _main():
    here = os.path.join(os.path.dirname(__file__))
    if os.path.exists(bdir := os.path.join(here, 'build')):
        shutil.rmtree(bdir)
    for f in glob.glob(os.path.join(here, '*.so')):
        os.remove(f)

    importhook.install()

    ##

    from . import junk  # noqa
    print(junk.junk())
    print(junk.abctok())

    ##

    import functools

    print(os.getpid())
    # input()

    from . import _dispatch  # noqa
    fw = functools.wraps(barf)(_dispatch.function_wrapper(return_barf))

    print(fw)
    print(fw.dispatch)
    assert fw(10) == 'barf str! 10'

    import weakref
    fwr = weakref.ref(fw)
    assert fwr() is fw

    import pickle
    upfw = pickle.loads(pickle.dumps(fw))
    assert upfw(10) == 'barf str! 10'

    from . import _descriptor  # noqa
    print(_descriptor.field_descriptor)


if __name__ == '__main__':
    _main()

import glob
import os.path
import shutil

from omdev.exts import importhook


def _main():
    here = os.path.join(os.path.dirname(__file__))
    if os.path.exists(bdir := os.path.join(here, 'build')):
        shutil.rmtree(bdir)
    for f in glob.glob(os.path.join(here, '*.so')):
        os.remove(f)

    importhook.install()

    ##

    from . import _uuid  # noqa
    print(_uuid)

    ##

    importhook.uninstall()


if __name__ == '__main__':
    _main()

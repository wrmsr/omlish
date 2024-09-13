import glob
import os.path
import shutil

from omdev.cexts import build


def _main():
    here = os.path.join(os.path.dirname(__file__))
    if os.path.exists(bdir := os.path.join(here, 'build')):
        shutil.rmtree(bdir)
    for f in glob.glob(os.path.join(here, '*.so')):
        os.remove(f)

    #

    build.build_ext(build.BuildExt(
        'x.dev.c._pybindthing',
        os.path.join(here, '_pybindthing.cc'),
    ))

    #

    import _pybindthing  # noqa
    print(_pybindthing.add(1, 2))


if __name__ == '__main__':
    _main()

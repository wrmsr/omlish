import glob
import os.path
import shutil
import time

from omdev.cexts import importhook


def _main() -> None:
    here = os.path.join(os.path.dirname(__file__))
    if os.path.exists(bdir := os.path.join(here, 'build')):
        shutil.rmtree(bdir)
    for f in glob.glob(os.path.join(here, '*.so')):
        os.remove(f)

    importhook.install()

    #

    # from . import _claude as dispatch  # noqa
    from . import _gpto1 as dispatch  # noqa

    #

    disp = dispatch.Dispatcher()
    disp.register('object', [object])
    disp.register('str', [str])
    disp_dispatch = disp.dispatch

    n = 1_000_000
    start = time.time_ns()

    for _ in range(n):
        disp_dispatch(str)

    end = time.time_ns()
    total = end - start
    per = total / n
    print(f'{per} ns / it')

    #

    importhook.uninstall()


if __name__ == '__main__':
    _main()

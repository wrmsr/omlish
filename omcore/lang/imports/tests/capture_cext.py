import glob
import os.path
import sys


def _main() -> None:
    for cxp in glob.glob(os.path.join(os.path.dirname(os.path.dirname(__file__)), '_capture.*.so')):
        os.unlink(cxp)

    from omdev.cexts import importhook
    importhook.install()

    from .. import _capture  # type: ignore[attr-defined]
    print(_capture)

    def new_import(*args, **kwargs):
        print(f'new import: {args=} {kwargs=}')

    frame = sys._getframe(0)  # noqa
    old_builtins = frame.f_builtins
    new_builtins = {**old_builtins, '__import__': new_import}

    if _capture._set_frame_builtins(frame, old_builtins, new_builtins):  # noqa
        print(_capture._set_frame_builtins(frame, new_builtins, old_builtins))  # noqa


if __name__ == '__main__':
    _main()

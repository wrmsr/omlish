import os.path
import sys


def _main() -> None:
    if os.path.exists(
            cxp := os.path.join(os.path.dirname(os.path.dirname(__file__)), '_capture.cpython-313-darwin.so'),
    ):
        os.unlink(cxp)

    from omdev.cexts import importhook
    importhook.install()

    from .. import _capture  # type: ignore[attr-defined]
    print(_capture)

    frame = sys._getframe(0)  # noqa
    old_builtins = frame.f_builtins
    new_builtins = {**old_builtins}

    if _capture._set_frame_builtins(frame, old_builtins, new_builtins):  # noqa
        print(_capture._set_frame_builtins(frame, new_builtins, old_builtins))  # noqa


if __name__ == '__main__':
    _main()

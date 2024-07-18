import os.path

from .. import importhook


def test_import_hook():
    for fn in os.listdir(os.path.dirname(__file__)):
        if os.path.isfile(fn) and fn.endswith('.so'):
            os.unlink(fn)

    was_installed = importhook.is_installed()
    try:
        importhook.install()

        from . import _junk  # type: ignore
        assert _junk.junk() == 424

    finally:
        if not was_installed:
            importhook.uninstall()

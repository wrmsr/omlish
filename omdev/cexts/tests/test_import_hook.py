import os.path

from .. import importhook


def test_import_hook():
    if not os.path.isfile(os.path.join(os.getcwd(), 'pyproject.toml')):
        raise RuntimeError('run in project root')

    for fn in os.listdir(bp := os.path.dirname(__file__)):
        if os.path.isfile(fp := os.path.join(bp, fn)) and fn.endswith('.so'):
            os.unlink(fp)

    was_installed = importhook.is_installed()
    try:
        importhook.install()

        from . import _junk  # type: ignore
        assert _junk.junk() == 424

    finally:
        if not was_installed:
            importhook.uninstall()

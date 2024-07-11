from .. import importhook


def test_import_hook():
    was_installed = importhook.is_installed()
    try:
        importhook.install()

        from . import _junk  # type: ignore
        assert _junk.junk() == 424

    finally:
        if not was_installed:
            importhook.uninstall()

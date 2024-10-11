"""
TODO:
 - select best debugger: ipdb, pudb,
"""
import contextlib
import sys
import traceback
import typing as ta


@contextlib.contextmanager
def debugging_on_exception(
        *,
        silent: bool = False,
) -> ta.Iterator[None]:
    import pdb  # noqa

    try:
        yield
    except Exception:
        if not silent:
            traceback.print_exc()

        pdb.post_mortem(sys.exc_info()[2])

        raise

# type: ignore
# ruff: noqa
# flake8: noqa
import _imp
import contextlib
import sys


@contextlib.contextmanager
def frozen_modules(enabled=True):
    """
    Force frozen modules to be used (or not).

    This only applies to modules that haven't been imported yet. Also, some essential modules will always be imported
    frozen.
    """

    _imp._override_frozen_modules_for_tests(1 if enabled else -1)  # noqa
    try:
        yield
    finally:
        _imp._override_frozen_modules_for_tests(0)  # noqa


class CleanImport:
    """
    Context manager to force import to return a new module reference.

    This is useful for testing module-level behaviours, such as the emission of a DeprecationWarning on import.

    Use like this:

        with CleanImport("foo"):
            importlib.import_module("foo") # new reference

    If "usefrozen" is False (the default) then the frozen importer is disabled (except for essential modules like
    importlib._bootstrap).
    """

    def __init__(self, *module_names, usefrozen=False):
        self.original_modules = sys.modules.copy()
        for module_name in module_names:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                # It is possible that module_name is just an alias for another module (e.g. stub for modules renamed in
                # 3.x). In that case, we also need delete the real module to clear the import cache.
                if module.__name__ != module_name:
                    del sys.modules[module.__name__]
                del sys.modules[module_name]
        self._frozen_modules = frozen_modules(usefrozen)

    def __enter__(self):
        self._frozen_modules.__enter__()
        return self

    def __exit__(self, *ignore_exc):
        sys.modules.update(self.original_modules)
        self._frozen_modules.__exit__(*ignore_exc)
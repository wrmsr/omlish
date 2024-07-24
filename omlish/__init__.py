import sys as _sys


REQUIRED_PYTHON_VERSION = (3, 12)


if _sys.version_info < REQUIRED_PYTHON_VERSION:
    raise RuntimeError(f'Python version {_sys.version_info=} < {REQUIRED_PYTHON_VERSION}')

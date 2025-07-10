import sys


##


REQUIRED_PYTHON_VERSION = (3, 13)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise OSError(
            f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa


def is_gil_enabled() -> bool:
    if (fn := getattr(sys, '_is_gil_enabled', None)) is not None:
        return fn()
    return True

import sys


REQUIRED_PYTHON_VERSION = (3, 8)


def check_runtime_version() -> None:
    if sys.version_info < REQUIRED_PYTHON_VERSION:
        raise EnvironmentError(
            f'Requires python {REQUIRED_PYTHON_VERSION}, got {sys.version_info} from {sys.executable}')  # noqa

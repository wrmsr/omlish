import sys


def is_gil_enabled() -> bool:
    if (fn := getattr(sys, '_is_gil_enabled', None)) is not None:
        return fn()
    return True

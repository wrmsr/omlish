if __name__ == '__main__':
    import sys

    from .main import _main  # noqa

    sys.exit(rc if isinstance(rc := _main(), int) else 0)

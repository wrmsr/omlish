import functools


##


def error_logging(log):  # noqa
    def outer(fn):
        @functools.wraps(fn)
        def inner(*args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception:
                log.exception('Error in %r', fn)
                raise

        return inner

    return outer

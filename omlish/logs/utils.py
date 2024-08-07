import functools
import logging


log = logging.getLogger(__name__)


def error_logging(log=log):  # noqa
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

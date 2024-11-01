import functools
import os.path
import pickle
import typing as ta


T = ta.TypeVar('T')


def pkl_cache(pkl_file: str | ta.Callable[[], str]) -> ta.Callable[[ta.Callable[[], T]], ta.Callable[[], T]]:
    def outer(fn):
        @functools.wraps(fn)
        def inner():
            pf = pkl_file if isinstance(pkl_file, str) else pkl_file()

            if not os.path.exists(pf):
                v = fn()
                with open(pf, 'wb') as f:
                    pickle.dump(v, f)
                return v

            else:
                with open(pf, 'rb') as f:
                    return pickle.load(f)  # noqa

        return inner
    return outer



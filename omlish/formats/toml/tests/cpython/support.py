import contextlib
import sys
import typing as ta


def get_recursion_depth():
    """
    Get the recursion depth of the caller function.

    In the __main__ module, at the module level, it should be 1.
    """

    try:
        import _testinternalcapi
        depth = _testinternalcapi.get_recursion_depth()
    except (ImportError, RecursionError) as exc:  # noqa
        # sys._getframe() + frame.f_back implementation.
        frame: ta.Any
        try:
            depth = 0
            frame = sys._getframe()  # noqa
            while frame is not None:
                depth += 1
                frame = frame.f_back
        finally:
            # Break any reference cycles.
            frame = None

    # Ignore get_recursion_depth() frame.
    return max(depth - 1, 1)


def get_recursion_available():
    """
    Get the number of available frames before RecursionError.

    It depends on the current recursion depth of the caller function and sys.getrecursionlimit().
    """

    limit = sys.getrecursionlimit()
    depth = get_recursion_depth()
    return limit - depth


@contextlib.contextmanager
def set_recursion_limit(limit):
    """Temporarily change the recursion limit."""

    original_limit = sys.getrecursionlimit()
    try:
        sys.setrecursionlimit(limit)
        yield
    finally:
        sys.setrecursionlimit(original_limit)


def infinite_recursion(max_depth=None):
    if max_depth is None:
        # Pick a number large enough to cause problems but not take too long for code that can handle very deep
        # recursion.
        max_depth = 20_000
    elif max_depth < 3:
        raise ValueError('max_depth must be at least 3, got {max_depth}')
    depth = get_recursion_depth()
    depth = max(depth - 1, 1)  # Ignore infinite_recursion() frame.
    limit = depth + max_depth
    return set_recursion_limit(limit)

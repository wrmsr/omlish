import types
import typing as ta
import weakref


T = ta.TypeVar('T')


##


_STATIC_VALUES: ta.MutableMapping[types.CodeType, ta.Any] = weakref.WeakKeyDictionary()


def static(fn: ta.Callable[[], T]) -> T:
    """
    An 'inline' nullary cache, useful for late initialization of things that would be inconvenient to have to move
    outside of their point of use to a more proper for shared cached objects like a class or module body.

    Cached contents are effectively immortal (more specifically tied to the lifetime of the passed code object). Users
    must be careful to ensure to local state is unintentionally closed over.

    There is intentionally no locking performed - before population, any number of threads may simultaneously call the
    function and they will all execute like normal, but afterward only (an unspecified) one will remain in the cache -
    this mechanism alone does not provide 'exactly-once' semantics.

    Primarily intended for the inline construction of immutable objects - particularly things like query builders. For
    example:

    >>> sql.api.query_opt_one(db, lang.static(lambda: Q.select(
    >>>     [Q.i.value],
    >>>     Q.n.states,
    >>>     Q.eq(Q.n.key, Q.p.key),
    >>> )), {
    >>>     Q.p.key: key,
    >>> })

    As the cache will 'stabilize' to a single value after any possible concurrent initialization the returned object is
    generally suitable for use as key in separate caches (like query compilation caches).
    """

    try:
        return _STATIC_VALUES[fn.__code__]  # noqa
    except KeyError:
        pass

    _STATIC_VALUES[fn.__code__] = v = fn()  # noqa
    return v

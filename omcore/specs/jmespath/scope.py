import typing as ta


K = ta.TypeVar('K')
V = ta.TypeVar('V')


##


class ScopedChainDict(ta.Generic[K, V]):
    """
    Dictionary that can delegate lookups to multiple dicts. This provides a basic get/set dict interface that is backed
    by multiple dicts.  Each dict is searched from the top most (most recently pushed) scope dict until a match is
    found.
    """

    def __init__(self, *scopes: ta.Mapping[K, V]) -> None:
        super().__init__()

        # The scopes are evaluated starting at the top of the stack (the most recently pushed scope via .push_scope()).
        self._scopes: list[ta.Mapping[K, V]] = list(reversed(scopes))

    def __getitem__(self, key: K) -> V:
        for scope in reversed(self._scopes):
            if key in scope:
                return scope[key]
        raise KeyError(key)

    def get(self, key: K, default: V | None = None) -> V | None:
        try:
            return self[key]
        except KeyError:
            return default

    def push_scope(self, scope: ta.Mapping[K, V]) -> None:
        self._scopes.append(scope)

    def pop_scope(self) -> None:
        self._scopes.pop()

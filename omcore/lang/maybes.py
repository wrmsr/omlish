from ..lite.maybes import Maybe


##

# These are classmethods on the lite `Maybe` class, and thus can't be directly `auto_proxy_init` imported in lang's
# `__init__.py`.
empty = Maybe.empty
just = Maybe.just

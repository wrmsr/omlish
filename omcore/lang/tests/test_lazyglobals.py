import pytest

from ..lazyglobals import AmbiguousLazyGlobalsFallbackError
from ..lazyglobals import LazyGlobals


def test_set_fn():
    lg = LazyGlobals()
    lg.set_fn('x', lambda: 42)
    assert lg.get('x') == 42
    assert lg('x') == 42


def test_fallback_claims_and_declines():
    lg = LazyGlobals()
    lg.add_fallback_fn(lambda attr: (lambda: 42) if attr == 'x' else None)
    lg.add_fallback_fn(lambda attr: (lambda: 43) if attr == 'y' else None)

    # The claiming fallback's getter is invoked - the value, not the getter, is returned.
    assert lg.get('x') == 42
    assert lg.get('y') == 43

    with pytest.raises(AttributeError):
        lg.get('z')


def test_fallback_ambiguity():
    lg = LazyGlobals()
    lg.add_fallback_fn(lambda attr: (lambda: 1))
    lg.add_fallback_fn(lambda attr: (lambda: 2))

    # Only when more than one fallback actually claims the attr is the lookup ambiguous.
    with pytest.raises(AmbiguousLazyGlobalsFallbackError):
        lg.get('x')


def test_update_globals():
    glo: dict = {}
    lg = LazyGlobals(globals=glo, update_globals=True)
    lg.add_fallback_fn(lambda attr: (lambda: 42) if attr == 'x' else None)
    assert lg.get('x') == 42
    assert glo['x'] == 42

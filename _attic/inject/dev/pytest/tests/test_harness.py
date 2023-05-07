"""
TODO:
 - pytest injector scopes:
  - lifecycle callbacks
 - still use pytest for parameterization
 - 'harness' dep?
 - inj mods reg in conftests?
  - watch imports
"""
from _pytest.fixtures import FixtureRequest # noqa
import pytest

from .... import inject as inj
from ..harness import Harness
from ..harness import PytestScope


def provider():
    def inner(fn):
        def new(cls):
            return fn()
        cls = type(fn.__name__, (), {'__new__': new})
        return cls
    return inner


@provider()
def some_url() -> str:
    return 'a url'


def test_harness():
    bnd = inj.create_binder()
    bnd.bind(some_url)
    ij = inj.create_injector(bnd)
    assert ij[some_url] == 'a url'
    with pytest.raises(Exception):
        ij[5]  # noqa


def test_harness_2(harness: Harness):
    req: FixtureRequest = harness[inj.Key(FixtureRequest, PytestScope.FUNCTION)]
    print(req.function)

    print(harness[FixtureRequest])


def test_harness_3(harness: Harness):
    req: FixtureRequest = harness[inj.Key(FixtureRequest, PytestScope.FUNCTION)]
    print(req.function)

    print(harness[FixtureRequest])

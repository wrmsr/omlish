import importlib
import pkgutil
import types

import pytest

import abnf.grammars


@pytest.mark.parametrize('rfc', map(importlib.import_module, [
    f'{abnf.grammars.__name__}.{x[1]}'
    for x in pkgutil.walk_packages(abnf.grammars.__path__)
    if x[1] == 'cors' or x[1].startswith('rfc')
]))
def test_grammar(rfc: types.ModuleType):
    """Catches rules used but not defined in grammar."""

    for rule in rfc.Rule.rules():
        if not hasattr(rule, 'definition'):
            print(str(rule))  # noqa: T201
        assert hasattr(rule, 'definition')

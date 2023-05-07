import pytest

from ..testing import can_import


def skip_if_cant_import(module: str, *args, **kwargs):
    return pytest.mark.skipif(not can_import(module, *args, **kwargs), reason=f'requires import {module}')

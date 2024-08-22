import pickle
import secrets

import pytest

from ... import lang


@lang.cached_function(lock=True)
def _opaque_key() -> bytes:
    return secrets.token_bytes(12)


class Opaque(lang.NotPicklable):
    _VALUE_ATTR = '__opaque_value__'

    def __init__(self, value: str) -> None:
        super().__init__()
        setattr(self, self._VALUE_ATTR, lambda: value)

    def reveal(self) -> str:
        return getattr(self, self._VALUE_ATTR)()


def test_opaque():
    o = Opaque('foo')
    assert o.reveal() == 'foo'
    with pytest.raises(TypeError):
        pickle.dumps(o)

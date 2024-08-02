from ... import reflect as rfl
from ..binder import bind
from ..bindings import Binding
from ..keys import Key
from ..providers import ConstProvider


def test_api():
    assert bind(5) == Binding(Key(rfl.type_(int)), ConstProvider(5))

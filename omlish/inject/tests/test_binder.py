from ... import reflect as rfl
from ..binder import bind
from ..bindings import Binding
from ..keys import Key
from ..providers import ConstProvider


def test_binder():
    assert bind(5) == Binding(Key(rfl.typeof(int)), ConstProvider(5))

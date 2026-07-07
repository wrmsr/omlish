from ... import reflect2 as rfl
from ..binder import bind
from ..bindings import Binding
from ..keys import Key
from ..providers import ConstProvider


def test_binder():
    assert bind(5) == Binding(Key(rfl.reflect_type(int)), ConstProvider(5))

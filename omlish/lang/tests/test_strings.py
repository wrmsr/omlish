from ..strings import camel_case
from ..strings import snake_case


def test_camel_case():
    assert camel_case('some_class') == 'SomeClass'


def test_snake_case():
    assert snake_case('Abc') == 'abc'
    assert snake_case('AbcDef') == 'abc_def'
    assert snake_case('AbcDefG') == 'abc_def_g'
    assert snake_case('AbcDefGH') == 'abc_def_g_h'
    assert snake_case('') == ''

import pytest

from .. import strings as strings_


def test_camelize():
    assert strings_.camelize('some_class') == 'SomeClass'


def test_decamelize():
    assert strings_.decamelize('Abc') == 'abc'
    assert strings_.decamelize('AbcDef') == 'abc_def'
    assert strings_.decamelize('AbcDefG') == 'abc_def_g'
    assert strings_.decamelize('AbcDefGH') == 'abc_def_g_h'
    assert strings_.decamelize('') == ''


def test_delimited_escaping():
    de = strings_.DelimitedEscaping('.', '"', '\\')
    assert de.quote('abc') == 'abc'
    assert de.quote('a.bc') == '"a\\.bc"'

    parts = ['abc', 'de.f', 'g', 'f']
    delimited = de.delimit_many(parts)
    assert delimited == 'abc."de\\.f".g.f'

    undelimited = de.undelimit(delimited)
    assert undelimited == parts


def test_redact():
    barf = strings_.redact('barf')
    assert barf.value == 'barf'
    assert strings_.redact(barf) is barf
    assert 'barf' not in str(barf)
    assert 'barf' not in repr(barf)
    assert barf == 'barf'
    assert barf != 'barfx'
    assert barf < 'barfx'


def test_bools():
    assert strings_.parse_bool('1') is True
    assert strings_.parse_bool('t') is True
    assert strings_.parse_bool('f') is False
    assert strings_.parse_bool('tRuE') is True
    with pytest.raises(ValueError):
        assert strings_.parse_bool('tRuE', strict=True)

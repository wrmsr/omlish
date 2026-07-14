from .. import delimit


def test_delimited_escaping():
    de = delimit.DelimitedEscaping('.', '"', '\\')
    assert de.quote('abc') == 'abc'
    assert de.quote('a.bc') == '"a\\.bc"'

    parts = ['abc', 'de.f', 'g', 'f']
    delimited = de.delimit_many(parts)
    assert delimited == 'abc."de\\.f".g.f'

    undelimited = de.undelimit(delimited)
    assert undelimited == parts

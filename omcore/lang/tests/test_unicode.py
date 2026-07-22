from ..unicode import is_ident
from ..unicode import is_ident_cont
from ..unicode import is_ident_start


def test_is_ident_start():
    assert is_ident_start('a')
    assert is_ident_start('_')
    assert is_ident_start('\u1885')  # Other_ID_Start (category Mn since Unicode 9)
    assert is_ident_start('\u1886')
    assert not is_ident_start('1')
    assert not is_ident_start(' ')
    assert not is_ident_start('¼')  # NFKC-normalizes to a multi-char string


def test_is_ident_cont():
    assert is_ident_cont('a')
    assert is_ident_cont('1')
    assert is_ident_cont('_')
    assert not is_ident_cont(' ')
    assert not is_ident_cont('¼')  # NFKC-normalizes to a multi-char string


def test_is_ident():
    assert is_ident('foo')
    assert is_ident('_foo1')
    assert not is_ident('1foo')
    assert not is_ident('')


def test_matches_isidentifier():
    for i in range(0x300):
        c = chr(i)
        assert is_ident_start(c) == c.isidentifier(), hex(i)
        assert is_ident(c) == c.isidentifier(), hex(i)

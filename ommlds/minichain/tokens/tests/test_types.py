from ..types import NonSpecialToken
from ..types import SpecialToken


def test_token_types():
    assert type(SpecialToken) is not int
    assert type(NonSpecialToken(420)) is int

    assert isinstance(SpecialToken(420), SpecialToken)
    assert not isinstance(NonSpecialToken(420), SpecialToken)

    assert isinstance(SpecialToken(420), int)
    assert isinstance(NonSpecialToken(420), int)

    assert hash(SpecialToken(420)) == hash(NonSpecialToken(420)) == hash(420) == 420
    assert SpecialToken(420) == NonSpecialToken(420) == 420

    assert {420: 'abc', 421: 'def'}[SpecialToken(420)] == 'abc'
    assert {420: 'abc', 421: 'def'}[NonSpecialToken(420)] == 'abc'

    assert {420: 'abc', 421: 'def'}.get(SpecialToken(422)) is None
    assert {420: 'abc', 421: 'def'}.get(NonSpecialToken(422)) is None

    assert SpecialToken(420) in {420, 421}
    assert NonSpecialToken(420) in {420, 421}

    assert SpecialToken(422) not in {420, 421}
    assert NonSpecialToken(422) not in {420, 421}

    assert len({SpecialToken(420), NonSpecialToken(420), 420}) == 1

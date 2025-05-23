import pytest

from omlish import lang

from ..specials import StandardSpecialToken
from ..specials import StandardSpecialTokens


Bos = StandardSpecialTokens.Bos
Eos = StandardSpecialTokens.Eos


def test_standard():
    assert Bos(420) == Eos(420) == 420
    assert issubclass(Eos, StandardSpecialToken)
    assert isinstance(Eos(420), StandardSpecialToken)

    # Opting not to enforce for now.
    # with pytest.raises(lang.AbstractTypeError):
    #     StandardSpecialToken(420)

    with pytest.raises(lang.SealedError):
        class NewSpecialToken(StandardSpecialToken):  # noqa
            pass


def test_namespace():
    print(list(StandardSpecialTokens))
    # reveal_type(StandardSpecialTokens['foo'])
    # bos = StandardSpecialTokens['foo']
    # reveal_type(bos)
    bos2 = StandardSpecialTokens.__getitem__('bos')
    # reveal_type(bos2)
    assert bos2 is Bos

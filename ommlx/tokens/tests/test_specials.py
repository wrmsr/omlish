import pytest

from omlish import lang

from ..specials import AmbiguousSpecialTokenError
from ..specials import SpecialTokens
from ..specials import StandardSpecialToken
from ..specials import StandardSpecialTokens


Bos = StandardSpecialTokens.Bos
Eos = StandardSpecialTokens.Eos
Unk = StandardSpecialTokens.Unk
Sep = StandardSpecialTokens.Sep


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


def test_collection():
    sts = SpecialTokens([
        Bos(420),
        Eos(531),
        Sep(1024),
        Sep(1025),
    ])
    print(sts)

    assert sts[Bos] == Bos(420)
    assert list(sts.by_type[Bos]) == [Bos(420)]
    with pytest.raises(KeyError):
        sts[Unk]  # noqa
    assert list(sts.by_type[Sep]) == [Sep(1024), Sep(1025)]
    with pytest.raises(AmbiguousSpecialTokenError):
        sts[Sep]  # noqa

    assert sts.get(Bos) == Bos(420)
    assert sts.get(Bos, Bos(421)) == Bos(420)
    assert sts.get(Bos(421)) is None

    assert sts.get(Unk) is None
    assert sts.get(Unk, Unk(422)) == Unk(422)

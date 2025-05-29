from ..types import TokenStr
from ..types import cast_token
from ..vocabs import Vocab


def test_vocab() -> None:
    vocab = Vocab([
        (cast_token(0), TokenStr('zero')),
        (cast_token(1), TokenStr('one')),
        (cast_token(2), TokenStr('two')),
    ])
    print(vocab)

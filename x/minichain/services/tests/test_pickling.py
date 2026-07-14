import pickle

import pytest

from .._typedvalues import _TypedValuesTypeError  # noqa
from .chat import ApiKey
from .chat import LocalChatRequest
from .chat import MaxTokens
from .chat import Message
from .chat import ModelPath


def test_pickling1():
    lcr = LocalChatRequest([Message('user', 'hi')], [MaxTokens(10), ModelPath('my_model')])
    assert lcr.options[MaxTokens] == MaxTokens(10)
    lcr.validate()

    lcr2 = pickle.loads(pickle.dumps(lcr))  # noqa
    assert lcr == lcr2
    lcr2.validate()


def test_pickling2():
    lcr = LocalChatRequest([Message('user', 'hi')], [MaxTokens(10), ApiKey('secret')])  # type: ignore[list-item]
    assert lcr.options[MaxTokens] == MaxTokens(10)

    lcr2 = pickle.loads(pickle.dumps(lcr))  # noqa
    assert lcr == lcr2
    with pytest.raises(_TypedValuesTypeError):
        lcr2.validate()

import typing as ta

from omlish import lang

from ..generative import GenerativeOption
from ..models import ModelOption
from ..options import Option


class ChatOption(Option, lang.Abstract):
    pass


ChatOptions: ta.TypeAlias = ModelOption | GenerativeOption | ChatOption

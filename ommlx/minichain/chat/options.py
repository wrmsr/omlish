import typing as ta

from omlish import lang

from ..generative import GenerativeRequestOption
from ..models import ModelRequestOption
from ..options import Option


class ChatRequestOption(Option, lang.Abstract):
    pass


ChatRequestOptions: ta.TypeAlias = ModelRequestOption | GenerativeRequestOption | ChatRequestOption

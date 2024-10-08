import typing as ta

from omlish import lang

from ..generative import GenerativeRequestOption
from ..models import Option
from ..models import RequestOption


class ChatRequestOption(Option, lang.Abstract):
    pass


ChatRequestOptions: ta.TypeAlias = RequestOption | GenerativeRequestOption | ChatRequestOption

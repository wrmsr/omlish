from omlish import lang

from ..services import RequestOption
from ..services import ResponseOutput


##


class ChatRequestOption(RequestOption, lang.Abstract):
    pass


class ChatResponseOutput(ResponseOutput, lang.Abstract):
    pass

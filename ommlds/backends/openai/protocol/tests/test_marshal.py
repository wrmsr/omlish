import json

from omlish import marshal as msh

from ..chatcompletion.responseformat import ChatCompletionResponseFormat
from ..chatcompletion.responseformat import TextChatCompletionResponseFormat


def test_marshal():
    crf = TextChatCompletionResponseFormat()
    mv = msh.marshal(crf, ChatCompletionResponseFormat)
    mj = json.dumps(mv)
    print(mj)

    crf2 = msh.unmarshal(json.loads(mj), ChatCompletionResponseFormat)
    assert crf2 == crf

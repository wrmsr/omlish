from omlish import marshal as msh

from .chat import ChatRequest
from .chat import MaxTokens
from .chat import Message


def test_marshal():
    for chat_request in [
        ChatRequest((Message('user', 'hi'),), [MaxTokens(10)]),
        # Request((Message('user', 'hi'),), [MaxTokens(10)]),
    ]:
        mv = msh.marshal(chat_request, ChatRequest)
        print(mv)
        chat_request2: ChatRequest = msh.unmarshal(mv, ChatRequest)
        assert chat_request == chat_request2

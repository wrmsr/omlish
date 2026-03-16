import uuid

from omlish import marshal as msh

from ...metadata import RequestUuid
from .chat import ChatRequest
from .chat import MaxTokens
from .chat import Message


def test_marshal():
    for cr, xv in [
        (
            ChatRequest((Message('user', 'hi'),)),
            {'v': [{'role': 'user', 'message': 'hi'}]},
        ),
        (
            ChatRequest((Message('user', 'hi'),), [MaxTokens(10)]),
            {'v': [{'role': 'user', 'message': 'hi'}], 'options': [{'max_tokens': 10}]},
        ),
        (
            ChatRequest((Message('user', 'hi'),)).with_options(MaxTokens(10)),
            {'v': [{'role': 'user', 'message': 'hi'}], 'options': [{'max_tokens': 10}]},
        ),
        (
            ChatRequest((Message('user', 'hi'),), [MaxTokens(10)]).with_metadata(RequestUuid(uid := uuid.uuid4())),
            {'v': [{'role': 'user', 'message': 'hi'}], 'options': [{'max_tokens': 10}], 'metadata': [{'request_uuid': str(uid)}]},  # noqa
        ),
    ]:
        mv = msh.marshal(cr, ChatRequest)
        assert mv == xv
        cr2: ChatRequest = msh.unmarshal(mv, ChatRequest)
        assert cr == cr2

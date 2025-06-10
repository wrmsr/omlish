import uuid

from omlish import marshal as msh

from ...metadata import Uuid
from ..messages import Message
from ..messages import UserMessage


def test_marshal_messages():
    um = UserMessage('hi')

    umv = msh.marshal(um)
    assert umv == {'c': 'hi'}

    um2 = msh.unmarshal(umv, UserMessage)
    assert um2 == um

    mv = msh.marshal(um, Message)
    assert mv == {'user': {'c': 'hi'}}

    m2 = msh.unmarshal(mv, Message)
    assert m2 == um

    u = uuid.uuid4()
    um = UserMessage('hi').with_metadata(Uuid(u))

    mv = msh.marshal(um, Message)
    assert mv == {'user': {'c': 'hi', 'metadata': [{'uuid': str(u)}]}}

    m2 = msh.unmarshal(mv, Message)
    assert m2 == um
